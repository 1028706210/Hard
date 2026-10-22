"""跨语言概念对照映射：把 concepts.yaml 的对照元数据与课时引用合成公开载荷。

无对照元数据的旧概念完全兼容：槽位从课时 front matter 的 concepts 引用自动推导。
available 槽位的 lesson_id 必须指向同语言、且确实引用该概念的课时；
无效引用由调用方按 isolated error 记录，对应槽位降级为 missing。
"""

from __future__ import annotations

from typing import Iterable

from hard_api.content.models import ConceptCompareSlot, ConceptsDocument

LANGUAGES = ("python", "java", "csharp", "cpp")

_DERIVED_AVAILABLE_NOTE = ""
_INVALID_REFERENCE_NOTE = "对照课时引用无效，已按缺失处理。"
_DERIVED_MISSING_NOTE = "该语言路线暂无标注此概念的课时。"

ComparisonSlot = dict[str, object]
ComparisonConcept = dict[str, object]


def build_concept_reference_index(
    lessons_by_id: dict[str, tuple[str, Iterable[str]]],
) -> dict[str, dict[str, list[str]]]:
    """concept_id -> language -> [lesson_id]（按课程声明顺序）。"""

    index: dict[str, dict[str, list[str]]] = {}
    for lesson_id, (language, concepts) in lessons_by_id.items():
        for concept_id in concepts:
            index.setdefault(concept_id, {}).setdefault(language, []).append(lesson_id)
    return index


def build_comparison(
    concepts_document: ConceptsDocument | None,
    reference_index: dict[str, dict[str, list[str]]],
    lesson_title_by_id: dict[str, str],
) -> tuple[list[ComparisonConcept], list[dict[str, str]]]:
    """返回 (概念对照载荷, 无效引用列表)。"""

    payload: list[ComparisonConcept] = []
    invalid_references: list[dict[str, str]] = []
    for concept in concepts_document.concepts if concepts_document else []:
        slots: dict[str, ComparisonSlot] = {}
        for language in LANGUAGES:
            authored = concept.compare.get(language) if concept.compare else None
            if authored is not None:
                slot = _authored_slot(concept.id, language, authored, reference_index, lesson_title_by_id)
                if slot is None:
                    invalid_references.append(
                        {
                            "concept_id": concept.id,
                            "language": language,
                            "lesson_id": str(authored.lesson_id),
                        }
                    )
                    slot = _missing_slot(_INVALID_REFERENCE_NOTE)
            else:
                slot = _derived_slot(
                    reference_index.get(concept.id, {}).get(language, []),
                    lesson_title_by_id,
                )
            slots[language] = slot
        payload.append(
            {
                "id": concept.id,
                "name": concept.name,
                "description": concept.description,
                "slots": slots,
            }
        )
    return payload, invalid_references


def _missing_slot(note: str) -> ComparisonSlot:
    return {
        "status": "missing",
        "summary": "",
        "difference": "",
        "code": None,
        "lesson_id": None,
        "lesson_title": None,
        "note": note,
    }


def _derived_slot(lesson_ids: list[str], lesson_title_by_id: dict[str, str]) -> ComparisonSlot:
    if not lesson_ids:
        return _missing_slot(_DERIVED_MISSING_NOTE)
    lesson_id = lesson_ids[0]
    return {
        "status": "available",
        "summary": "",
        "difference": "",
        "code": None,
        "lesson_id": lesson_id,
        "lesson_title": lesson_title_by_id.get(lesson_id),
        "note": _DERIVED_AVAILABLE_NOTE or None,
    }


def _authored_slot(
    concept_id: str,
    language: str,
    slot: ConceptCompareSlot,
    reference_index: dict[str, dict[str, list[str]]],
    lesson_title_by_id: dict[str, str],
) -> ComparisonSlot | None:
    if slot.status == "missing":
        return _missing_slot(slot.note or "")
    assert slot.lesson_id is not None
    lesson_ids = reference_index.get(concept_id, {}).get(language, [])
    if slot.lesson_id not in lesson_ids:
        return None
    return {
        "status": "available",
        "summary": slot.summary,
        "difference": slot.difference,
        "code": slot.code,
        "lesson_id": slot.lesson_id,
        "lesson_title": lesson_title_by_id.get(slot.lesson_id),
        "note": None,
    }
