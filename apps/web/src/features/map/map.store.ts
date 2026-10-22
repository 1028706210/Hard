import { reactive, readonly } from "vue";
import { requestJson } from "../../api/client";
import { languageWorlds, type LanguageId, type MapStatus, statusLabels } from "./map-layout";

export interface MapLanguageState { status: MapStatus; label: string; available: boolean; }
export type MapLoadState = "loading" | "ready" | "error";
export type LessonStatus = "not_started" | "in_progress" | "completed" | "mastered" | "due_review";
export interface LessonState { status: LessonStatus; label: string; }
const lessonLabels: Record<LessonStatus, string> = { not_started: "未学习", in_progress: "学习中", completed: "已学完", mastered: "已掌握", due_review: "待复习" };
export interface MapSnapshot { loadState: MapLoadState; error: string; continueLessonId: string; continueLessonTitle: string; dailyGoal: string; level: string; streakDays: string; mastery: string; dueReviews: string; languages: Record<LanguageId, MapLanguageState>; lessons: Record<string, LessonState>; }

function languageState(status: MapStatus): MapLanguageState {
  return { status, label: statusLabels[status], available: status !== "unavailable" };
}

function emptySnapshot(): MapSnapshot {
  return {
    loadState: "loading", error: "", continueLessonId: "", continueLessonTitle: "正在读取学习概览", dailyGoal: "", level: "", streakDays: "", mastery: "", dueReviews: "",
    languages: Object.fromEntries(languageWorlds.map((world) => [world.id, languageState("unavailable")])) as Record<LanguageId, MapLanguageState>,
    lessons: {},
  };
}

const snapshot = reactive<MapSnapshot>(emptySnapshot());
let loading: Promise<void> | null = null;

export function buildMapSnapshot(catalog: any, progress: any, growth: any, review: any): MapSnapshot {
  const result = emptySnapshot();
  result.loadState = "ready";
  const courses = Array.isArray(catalog?.courses) ? catalog.courses : [];
  const current = progress?.continue_learning;
  const allLessons = courses.flatMap((course: any) => (Array.isArray(course.modules) ? course.modules : []).flatMap((module: any) => Array.isArray(module.lessons) ? module.lessons.map((lesson: any) => ({ ...lesson, language: course.language })) : []));
  const currentLesson = allLessons.find((lesson: any) => lesson.id === current?.lesson_id);
  result.dailyGoal = `${Math.floor(Number(progress?.daily_goal?.studied_seconds ?? 0) / 60)} / ${Number(progress?.daily_goal?.target_minutes ?? 0)} 分钟`;
  result.level = `Lv. ${Number(growth?.level ?? progress?.current_level ?? 1)}`;
  result.streakDays = `${Number(growth?.streak_days ?? progress?.streak_days ?? 0)} 天`;
  result.dueReviews = `${Array.isArray(review?.items) ? review.items.length : 0} 项`;
  const mastery = Array.isArray(growth?.mastery) ? growth.mastery : [];
  const saved = progress?.lesson_statuses ?? {};
  const dueLessons = new Set((Array.isArray(review?.items) ? review.items : []).map((item: any) => item.lesson_id));
  for (const lesson of allLessons) {
    const mastered = mastery.some((item: any) => item.scope_type === "lesson" && item.scope_id === lesson.id && Number(item.score) >= 85);
    const status: LessonStatus = dueLessons.has(lesson.id) ? "due_review" : mastered || saved[lesson.id] === "validated" ? "mastered" : saved[lesson.id] === "completed" ? "completed" : saved[lesson.id] === "in_progress" || lesson.id === current?.lesson_id ? "in_progress" : "not_started";
    result.lessons[lesson.id] = { status, label: lessonLabels[status] };
  }
  const lessonScores = mastery.filter((item: any) => item.scope_type === "lesson" && allLessons.some((lesson: any) => lesson.id === item.scope_id));
  result.mastery = lessonScores.length ? `${Math.round(lessonScores.reduce((sum: number, item: any) => sum + Number(item.score), 0) / allLessons.length)}%` : "未开始";
  const unlockedByLanguage = progress?.unlocked_lessons && typeof progress.unlocked_lessons === "object" ? progress.unlocked_lessons : null;
  for (const world of languageWorlds) {
    const course = courses.find((item: any) => item.language === world.id);
    if (!course) continue;
    const courseMastered = mastery.some((item: any) => item.scope_type === "course" && item.scope_id === world.id && Number(item.score) >= 85);
    const inProgress = current?.course_id === world.id || allLessons.some((lesson: any) => lesson.language === world.id && result.lessons[lesson.id].status !== "not_started");
    const firstModule = Array.isArray(course.modules) ? course.modules[0] : undefined;
    const unlocked = unlockedByLanguage && Array.isArray(unlockedByLanguage[world.id]) ? unlockedByLanguage[world.id] : null;
    const locked = !courseMastered && !inProgress && (unlocked ? unlocked.length === 0 : Array.isArray(firstModule?.prerequisites) && firstModule.prerequisites.length > 0);
    result.languages[world.id] = languageState(courseMastered ? "mastered" : inProgress ? "in_progress" : locked ? "locked" : "not_started");
  }
  const firstUnlockedLesson = allLessons.find((lesson: any) => Array.isArray(unlockedByLanguage?.[lesson.language]) && unlockedByLanguage[lesson.language].includes(lesson.id));
  const firstLesson = firstUnlockedLesson ?? (unlockedByLanguage ? undefined : allLessons[0]);
  result.continueLessonId = currentLesson?.id ?? firstLesson?.id ?? "";
  result.continueLessonTitle = currentLesson?.title ?? (firstLesson?.title ? `开始学习 · ${firstLesson.title}` : "尚无继续学习课时");
  return result;
}

export function refreshMapSnapshot(fetchImpl: typeof fetch = fetch) {
  if (!loading) Object.assign(snapshot, emptySnapshot());
  loading ??= Promise.all([requestJson<any>("/api/content/catalog", undefined, fetchImpl), requestJson<any>("/api/progress/summary", undefined, fetchImpl), requestJson<any>("/api/growth/summary", undefined, fetchImpl), requestJson<any>("/api/review/queue", undefined, fetchImpl)]).then(([catalog, progress, growth, review]) => {
    Object.assign(snapshot, buildMapSnapshot(catalog, progress, growth, review));
  }).catch(() => {
    Object.assign(snapshot, emptySnapshot(), { loadState: "error" as const, error: "无法读取学习概览。请检查连接后重试。", continueLessonTitle: "学习概览暂不可用" });
  }).finally(() => { loading = null; });
  return loading;
}
export function useMapStore() { return readonly(snapshot); }
