"""Compile only newly authored small examples using installed offline reference assemblies."""
from pathlib import Path
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
DOTNET=Path('D:/DevTools/dotnet/dotnet.exe')
CSC=DOTNET.parent/'sdk/10.0.100/Roslyn/bincore/csc.dll'
REF=DOTNET.parent/'packs/Microsoft.NETCore.App.Ref/10.0.0/ref/net10.0'
assert CSC.is_file() and REF.is_dir()
cases={
 'csharp-oop/classes': [['8','True']],
 'csharp-oop/structs': [['1','2'], ['3']],
 'csharp-oop/inheritance': [['base:pen','derived']],
 'csharp-oop/polymorphism': [['meow','animal','cat'],['1']],
 'csharp-oop/interfaces': [['report']],
 'csharp-oop/nullable': [['-1','0','True','False','0'],['-1','2']],
 'csharp-language-features/properties': [['Hello, Lin']],
 'csharp-language-features/indexer': [['7','0']],
 'csharp-language-features/delegates': [['-4','-16'],['6']],
 'csharp-language-features/events': [['31']],
 'csharp-language-features/generics': [['9','True','False']],
 'csharp-language-features/collections': [['True','False','2','5']],
 'csharp-language-features/anonymous-methods': [['12','0','1']],
}
usings='using System;\nusing System.Collections.Generic;\nusing System.Linq;\n'
result=[]
for key,expected_cases in cases.items():
 raw=(ROOT/'content/csharp'/f'{key}.md').read_text(encoding='utf-8')
 added=raw.split('### ',1)[1].split('## 常见错误与实践建议',1)[0]
 blocks=re.findall(r'```csharp\n(.*?)\n```',added,re.S)
 assert len(blocks)==len(expected_cases),(key,len(blocks))
 for index,(code,expected) in enumerate(zip(blocks,expected_cases),1):
  context=''
  if key.endswith('/delegates') and index==1:
   context=re.findall(r'```csharp\n(.*?)\n```',raw,re.S)[0]
  elif key.endswith('/events'):
   context=re.findall(r'```csharp\n(.*?)\n```',raw,re.S)[0]
  label=key.replace('/','-')+f'-{index}'
  directory=OUT/'examples'/label
  directory.mkdir(parents=True,exist_ok=False)
  source=directory/'Program.cs'
  source.write_text(usings+code+'\n'+context+'\n',encoding='utf-8')
  target=directory/'example.dll'
  rsp=directory/'compiler.rsp'
  rsp.write_text('\n'.join(['-nologo','-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable',
    f'-out:"{target}"',*[f'-r:"{p}"' for p in sorted(REF.glob('*.dll'))],f'"{source}"']),encoding='utf-8')
  build=subprocess.run([str(DOTNET),'exec',str(CSC),'@'+str(rsp)],capture_output=True,text=True,encoding='utf-8')
  runtime=directory/'example.runtimeconfig.json'
  runtime.write_text(json.dumps({'runtimeOptions':{'tfm':'net10.0','framework':{'name':'Microsoft.NETCore.App','version':'10.0.0'}}}),encoding='utf-8')
  run=subprocess.run([str(DOTNET),str(target)],capture_output=True,text=True,encoding='utf-8') if build.returncode==0 else None
  passed=build.returncode==0 and run.returncode==0 and run.stdout.splitlines()==expected
  row=dict(label=label,source_lesson=key+'.md',compiler_exit=build.returncode,compiler_output=build.stdout+build.stderr,
    runtime_exit=run.returncode if run else None,actual_stdout=run.stdout.splitlines() if run else None,
    expected_stdout=expected,passed=passed)
  result.append(row)
OUT.joinpath('example-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(examples=len(result),passed=sum(x['passed'] for x in result),failed=[x for x in result if not x['passed']]),ensure_ascii=False,indent=2))
raise SystemExit(0 if all(x['passed'] for x in result) else 1)
