/* This file is generated from packages/contracts/openapi.json by scripts/export-openapi.ps1. */

export type ApiPath =
  | "/api/assessment/attempts"
  | "/api/assessment/placement"
  | "/api/backup/export"
  | "/api/backup/import"
  | "/api/content/catalog"
  | "/api/content/courses/{language}"
  | "/api/content/lessons/{lesson_id}"
  | "/api/growth/history"
  | "/api/growth/summary"
  | "/api/growth/weaknesses"
  | "/api/lan/enable"
  | "/api/lan/status"
  | "/api/progress/daily-goal"
  | "/api/progress/favorites/{lesson_id}"
  | "/api/progress/lessons/{lesson_id}"
  | "/api/progress/notes/{lesson_id}"
  | "/api/progress/summary"
  | "/api/review/items/{review_item_id}"
  | "/api/review/queue"
  | "/api/runners/jobs/{job_id}"
  | "/api/runners/submissions"
  | "/api/search"
  | "/api/v1/health/live"
  | "/api/v1/health/ready";

export type AttemptResponse = Record<string, unknown>;
export type PlacementResponse = Record<string, unknown>;
export type ExportResponse = Record<string, unknown>;
export type ImportResponse = Record<string, unknown>;
export type CatalogResponse = Record<string, unknown>;
export type CourseResponse = Record<string, unknown>;
export type LessonResponse = Record<string, unknown>;
export type HistoryResponse = Record<string, unknown>;
export type GrowthSummaryResponse = Record<string, unknown>;
export type WeaknessListResponse = Record<string, unknown>;
export type LanDisableResponse = Record<string, unknown>;
export type LanEnableResponse = Record<string, unknown>;
export type LanStatusResponse = Record<string, unknown>;
export type DailyGoalResponse = Record<string, unknown>;
export type DeleteFavoriteResponse = Record<string, unknown>;
export type FavoriteResponse = Record<string, unknown>;
export type ProgressResponse = Record<string, unknown>;
export type DeleteNoteResponse = Record<string, unknown>;
export type NoteResponse = Record<string, unknown>;
export type SummaryResponse = Record<string, unknown>;
export type ReviewScoreResponse = Record<string, unknown>;
export type ReviewQueueResponse = Record<string, unknown>;
export type RunnerJobCancelResponse = Record<string, unknown>;
export type RunnerJobStatusResponse = Record<string, unknown>;
export type RunnerSubmissionResponse = Record<string, unknown>;
export type SearchResponse = Record<string, unknown>;
export type ResponseLiveApiV1HealthLiveGet = Record<string, string>;
export type ResponseReadyApiV1HealthReadyGet = Record<string, unknown>;

export interface ApiResponseByPath {
  "/api/assessment/attempts": { POST: AttemptResponse; };
  "/api/assessment/placement": { POST: PlacementResponse; };
  "/api/backup/export": { POST: ExportResponse; };
  "/api/backup/import": { POST: ImportResponse; };
  "/api/content/catalog": { GET: CatalogResponse; };
  "/api/content/courses/{language}": { GET: CourseResponse; };
  "/api/content/lessons/{lesson_id}": { GET: LessonResponse; };
  "/api/growth/history": { GET: HistoryResponse; };
  "/api/growth/summary": { GET: GrowthSummaryResponse; };
  "/api/growth/weaknesses": { GET: WeaknessListResponse; };
  "/api/lan/enable": { DELETE: LanDisableResponse; POST: LanEnableResponse; };
  "/api/lan/status": { GET: LanStatusResponse; };
  "/api/progress/daily-goal": { PUT: DailyGoalResponse; };
  "/api/progress/favorites/{lesson_id}": { DELETE: DeleteFavoriteResponse; PUT: FavoriteResponse; };
  "/api/progress/lessons/{lesson_id}": { PATCH: ProgressResponse; };
  "/api/progress/notes/{lesson_id}": { DELETE: DeleteNoteResponse; PUT: NoteResponse; };
  "/api/progress/summary": { GET: SummaryResponse; };
  "/api/review/items/{review_item_id}": { POST: ReviewScoreResponse; };
  "/api/review/queue": { GET: ReviewQueueResponse; };
  "/api/runners/jobs/{job_id}": { DELETE: RunnerJobCancelResponse; GET: RunnerJobStatusResponse; };
  "/api/runners/submissions": { POST: RunnerSubmissionResponse; };
  "/api/search": { GET: SearchResponse; };
  "/api/v1/health/live": { GET: ResponseLiveApiV1HealthLiveGet; };
  "/api/v1/health/ready": { GET: ResponseReadyApiV1HealthReadyGet; };
}

export class ApiClientError extends Error {
  constructor(public readonly status: number, public readonly body: unknown) {
    super("API request failed");
    this.name = "ApiClientError";
  }
}

export async function requestJson<T>(
  input: RequestInfo | URL,
  init: RequestInit = {},
  fetchImpl: typeof fetch = fetch,
): Promise<T> {
  const response = await fetchImpl(input, init);
  const contentType = response.headers.get("content-type") ?? "";
  const body: unknown = contentType.includes("application/json")
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    throw new ApiClientError(response.status, body);
  }
  return body as T;
}
