export const chainLanguages = ["python", "java", "csharp", "cpp"] as const;
export type ChainLanguage = typeof chainLanguages[number];
export const chainLabels: Record<ChainLanguage, string> = { python: "Python", java: "Java", csharp: "C#", cpp: "C++" };
export interface ChainLesson { id: string; title: string; }
export interface ChainModule { id: string; title: string; lessons: ChainLesson[]; }
export interface ChainCourse { language: ChainLanguage; modules: ChainModule[]; }
export interface ConceptSlot { status: "available" | "missing"; summary: string; difference: string; code: string | null; lesson_id: string | null; lesson_title: string | null; note: string | null; }
export interface ChainConcept { id: string; name: string; description: string; slots: Record<ChainLanguage, ConceptSlot>; }

// A cross-language connection exists only when both authored references exist in the catalog.
export function linkedLanguages(concept: ChainConcept, courses: ChainCourse[]) {
  return chainLanguages.filter(language => {
    const slot = concept.slots[language];
    return slot?.status === "available" && !!slot.lesson_id && courses.some(course => course.language === language &&
      course.modules.some(module => module.lessons.some(lesson => lesson.id === slot.lesson_id)));
  });
}

export function starPositions(lessons: ChainLesson[]) {
  return lessons.map((lesson, index) => {
    const row = Math.floor(index / 4);
    const column = row % 2 ? 3 - index % 4 : index % 4;
    const offset = [16, -12, 18, -4][column];
    return { ...lesson, x: 120 + column * 240, y: 78 + row * 148 + offset * (row % 2 ? -1 : 1) };
  });
}


const constellationGroups = [
  { id: "syntax", title: "基础语法", featured: ["variables", "types", "control-flow"], members: ["variables", "types", "control-flow", "operators", "strings", "nullable-types", "enums", "preprocessor-directives", "regular-expressions", "interpreter", "tooling"] },
  { id: "organization", title: "函数与组织", featured: ["functions", "packages", "exceptions"], members: ["functions", "methods", "packages", "namespaces", "exceptions", "io", "concurrency", "environments", "security", "web", "deployment", "delegates", "events", "anonymous-methods"] },
  { id: "data", title: "数据与对象", featured: ["collections", "classes", "inheritance"], members: ["collections", "classes", "inheritance", "polymorphism", "generics", "memory", "databases", "data-structures", "encapsulation", "arrays", "structs", "operator-overloading", "interfaces", "attributes", "reflection", "properties", "indexer", "pointers", "references", "signals"] },
];

// Presentation groups are thematic, not prerequisite edges or invented lesson records.
// Unknown authored concepts remain reachable in the data group instead of disappearing.
export function groupedConcepts(concepts: ChainConcept[], selectedId?: string) {
  const known = new Set(constellationGroups.flatMap(group => group.members));
  return constellationGroups.map(group => {
    const members = concepts.filter(concept => group.members.includes(concept.id) || (group.id === "data" && !known.has(concept.id)));
    const featured = group.featured.flatMap(id => members.filter(concept => concept.id === id));
    const selected = members.find(concept => concept.id === selectedId);
    const displayed = selected && !featured.some(concept => concept.id === selected.id)
      ? [...featured.slice(0, 2), selected] : featured;
    return { id: group.id, title: group.title, members, displayed };
  });
}
