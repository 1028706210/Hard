[CmdletBinding()]
param(
    [switch]$Check
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$apiSource = Join-Path $projectRoot 'apps\api\src'
$openApiPath = Join-Path $projectRoot 'packages\contracts\openapi.json'
$clientPath = Join-Path $projectRoot 'apps\web\src\api\client.ts'

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    throw "缺少项目虚拟环境：$venvPython"
}

function ConvertTo-TypeName {
    param([string]$Value)

    $parts = [regex]::Matches($Value, '[A-Za-z0-9]+') | ForEach-Object {
        $_.Value.Substring(0, 1).ToUpperInvariant() + $_.Value.Substring(1)
    }
    return ($parts -join '')
}

function ConvertTo-TypeScript {
    param([object]$Schema)

    if ($null -eq $Schema) {
        return 'unknown'
    }

    $typeProperty = $Schema.PSObject.Properties['type']
    $schemaType = if ($null -ne $typeProperty) { [string]$typeProperty.Value } else { '' }
    switch ($schemaType) {
        'string' { return 'string' }
        'integer' { return 'number' }
        'number' { return 'number' }
        'boolean' { return 'boolean' }
        'array' { return "Array<$((ConvertTo-TypeScript $Schema.items))>" }
        'object' {
            $additional = $Schema.PSObject.Properties['additionalProperties']
            if ($null -ne $additional -and $additional.Value -is [System.Management.Automation.PSCustomObject]) {
                return "Record<string, $((ConvertTo-TypeScript $additional.Value))>"
            }
            return 'Record<string, unknown>'
        }
        default { return 'unknown' }
    }
}

function Set-GeneratedFile {
    param(
        [string]$Path,
        [string]$Content,
        [string]$Label
    )

    if ($Check) {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            throw "$Label 缺失：$Path"
        }
        if ([System.IO.File]::ReadAllText($Path) -ne $Content) {
            throw "$Label 存在漂移：请运行 scripts\export-openapi.ps1"
        }
        return
    }

    $directory = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = if ($previousPythonPath) {
        "$apiSource$([System.IO.Path]::PathSeparator)$previousPythonPath"
    }
    else {
        $apiSource
    }
    $openApiLines = @(
        & $venvPython -c 'from hard_api.main import create_app; import json; print(json.dumps(create_app().openapi(), ensure_ascii=False, indent=2, sort_keys=True))'
    )
    if ($LASTEXITCODE -ne 0) {
        throw "导出 OpenAPI 失败，退出码 $LASTEXITCODE。"
    }
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

$openApiContent = ($openApiLines -join [Environment]::NewLine) + [Environment]::NewLine
$document = $openApiContent | ConvertFrom-Json
$responseTypes = [System.Collections.Generic.List[string]]::new()
$responseMappings = [System.Collections.Generic.List[string]]::new()
# Preserve the public aliases already imported by the frontend when several
# operations share one response schema.
$responseAliases = @{
    'DELETE /api/lan/enable' = 'LanDisableResponse'
    'POST /api/lan/enable' = 'LanEnableResponse'
    'DELETE /api/progress/favorites/{lesson_id}' = 'DeleteFavoriteResponse'
    'DELETE /api/progress/notes/{lesson_id}' = 'DeleteNoteResponse'
    'DELETE /api/runners/jobs/{job_id}' = 'RunnerJobCancelResponse'
    'GET /api/runners/jobs/{job_id}' = 'RunnerJobStatusResponse'
    'POST /api/runners/submissions' = 'RunnerSubmissionResponse'
}

foreach ($pathEntry in $document.paths.PSObject.Properties) {
    $methodMappings = [System.Collections.Generic.List[string]]::new()
    foreach ($methodEntry in $pathEntry.Value.PSObject.Properties) {
        $response = $methodEntry.Value.responses.'200'
        $schema = $response.content.'application/json'.schema
        $reference = $schema.PSObject.Properties['$ref']
        if ($null -ne $reference) {
            $prefix = '#/components/schemas/'
            if (-not ([string]$reference.Value).StartsWith($prefix)) {
                throw "Unsupported response schema reference: $($reference.Value)"
            }
            $componentName = ([string]$reference.Value).Substring($prefix.Length)
            $component = $document.components.schemas.PSObject.Properties[$componentName]
            if ($null -eq $component) { throw "Missing response schema: $componentName" }
            $schema = $component.Value
        }
        $titleProperty = $schema.PSObject.Properties['title']
        $title = if ($null -ne $titleProperty) { [string]$titleProperty.Value } else { '' }
        $typeName = if ($title) { ConvertTo-TypeName $title } else { 'UnknownResponse' }
        $operation = "$($methodEntry.Name.ToUpperInvariant()) $($pathEntry.Name)"
        if ($responseAliases.ContainsKey($operation)) { $typeName = $responseAliases[$operation] }
        $declaration = "export type $typeName = $(ConvertTo-TypeScript $schema);"
        if (-not $responseTypes.Contains($declaration)) { $responseTypes.Add($declaration) }
        $methodMappings.Add("$($methodEntry.Name.ToUpperInvariant()): $typeName;")
    }
    $responseMappings.Add("  `"$($pathEntry.Name)`": { $($methodMappings -join ' ') };")
}

$paths = @($document.paths.PSObject.Properties | ForEach-Object { "  | `"$($_.Name)`"" }) -join [Environment]::NewLine
$generatedClient = @(
    '/* This file is generated from packages/contracts/openapi.json by scripts/export-openapi.ps1. */'
    ''
    'export type ApiPath ='
    $paths + ';'
    ''
    $responseTypes
    ''
    'export interface ApiResponseByPath {'
    $responseMappings
    '}'
    ''
    'export class ApiClientError extends Error {'
    '  constructor(public readonly status: number, public readonly body: unknown) {'
    '    super("API request failed");'
    '    this.name = "ApiClientError";'
    '  }'
    '}'
    ''
    'export async function requestJson<T>('
    '  input: RequestInfo | URL,'
    '  init: RequestInit = {},'
    '  fetchImpl: typeof fetch = fetch,'
    '): Promise<T> {'
    '  const response = await fetchImpl(input, init);'
    '  const contentType = response.headers.get("content-type") ?? "";'
    '  const body: unknown = contentType.includes("application/json")'
    '    ? await response.json()'
    '    : await response.text();'
    '  if (!response.ok) {'
    '    throw new ApiClientError(response.status, body);'
    '  }'
    '  return body as T;'
    '}'
    ''
) -join [Environment]::NewLine

Set-GeneratedFile -Path $openApiPath -Content $openApiContent -Label 'OpenAPI 合同'
Set-GeneratedFile -Path $clientPath -Content $generatedClient -Label 'TypeScript API 类型'

if ($Check) {
    Write-Output 'OpenAPI 合同与 TypeScript 类型无漂移。'
}
