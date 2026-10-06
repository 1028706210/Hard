export type LanguageId = "python" | "java" | "csharp" | "cpp";
export type MapStatus = "unavailable" | "not_started" | "in_progress" | "mastered" | "locked";

export interface LanguageWorld {
  id: LanguageId;
  title: string;
  x: number;
  y: number;
}

export const orbitRings = [28, 46, 72] as const;

export const languageWorlds: readonly LanguageWorld[] = [
  { id: "python", title: "Python", x: 20, y: 28 },
  { id: "java", title: "Java", x: 76, y: 24 },
  { id: "csharp", title: "C#", x: 80, y: 72 },
  { id: "cpp", title: "C++", x: 20, y: 76 },
];

export const statusLabels: Record<MapStatus, string> = {
  unavailable: "尚无课程内容",
  not_started: "未开始",
  in_progress: "学习中",
  mastered: "已掌握",
  locked: "待前置",
};
