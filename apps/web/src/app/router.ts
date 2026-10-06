import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
  type RouterHistory,
} from "vue-router";

import KnowledgeMapPage from "../features/map/KnowledgeMapPage.vue";
import CoursePage from "../features/course/CoursePage.vue";
import LessonPage from "../features/course/LessonPage.vue";
import AssessmentPage from "../features/assessment/AssessmentPage.vue";
import ReviewPage from "../features/review/ReviewPage.vue";
import SearchPage from "../features/search/SearchPage.vue";
import GrowthPage from "../features/growth/GrowthPage.vue";
import ComparePage from "../features/compare/ComparePage.vue";
import SettingsPage from "../features/settings/SettingsPage.vue";

export const destinations = [
  { path: "/", label: "主页", heading: "知识星图主页" },
  { path: "/course/python", label: "课程", heading: "课程：python" },
  { path: "/lesson/python-foundations-hello-world", label: "当前课时", heading: "当前课时" },
  { path: "/assessment/python-foundations-hello-world", label: "练习评分", heading: "练习评分" },
  { path: "/review", label: "复习", heading: "复习中心" },
  { path: "/search", label: "搜索", heading: "搜索" },
  { path: "/growth", label: "成长", heading: "成长报告" },
  { path: "/settings", label: "设置", heading: "设置" },
] as const;

const routes: RouteRecordRaw[] = [
  { path: "/", component: KnowledgeMapPage },
  { path: "/course/:language", component: CoursePage },
  { path: "/lesson/:lessonId", component: LessonPage },
  { path: "/assessment/:lessonId", component: AssessmentPage },
  { path: "/review", component: ReviewPage },
  { path: "/search", component: SearchPage },
  { path: "/compare", component: ComparePage },
  { path: "/growth", component: GrowthPage },
  { path: "/settings", component: SettingsPage },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

export function createHardRouter(history: RouterHistory = createWebHistory()) {
  return createRouter({ history, routes });
}
