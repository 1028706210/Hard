# Assessment asynchronous feedback review — 2026-10-21

Scope: `apps/web/src/features/assessment/assessment.store.ts`, `AssessmentPage.vue`, and existing `apps/web/tests/assessment/*` regression cases. Read the complete global `C:/Users/李帅朋/.codex/AGENTS.md`. No AGENTS changes, commit/reset, service launch, E2E run, API changes, styles, or other-page changes were made by this review.

## Findings and minimal fixes

1. **Same-question requests could overwrite newer feedback.** The baseline had three failing deferred-request cases: an older success replaced a newer score; an older failure added an offline error after a newer success; an older success added a score after a newer failure. Added a per-exercise `knowledgeRevision`, incremented when an answer is submitted and checked before either success or failure changes visible feedback. This follows the store's existing runner revision pattern without adding an abstraction or dependency.
2. **Discarded lesson loads reset the current exercise.** The store already returns `null` for a superseded lesson load, but the page unconditionally reset `selectedIndex` after every completion. The page now resets it only when `loadLesson` returns a lesson. The deferred navigation regression keeps the second question selected after the old load returns `null`.

Offline preservation is deliberately before the failure revision check. Every failed answer request still enters the existing offline queue with its original lesson, exercise, answer, hint level, and idempotency key. A stale failure only loses permission to change the visible feedback. Per-exercise feedback still allows an earlier question's response to be seen when returning to that question, without replacing the currently selected question's score. Loading another lesson clears the feedback map, so old feedback objects remain detached from the new lesson.

Existing regression tests were reused unchanged in this review. They were already present on entry and reproduced the defects before implementation.

## Actual verification

All commands ran in `apps/web` with `C:/Program Files/nodejs/node.exe`.

| Check | Result |
| --- | --- |
| Baseline: `node_modules/vitest/vitest.mjs run tests/assessment --reporter=verbose --no-color` | **RED**, exit 1: 4 failed, 34 passed, 3 files |
| Same command after implementation | **PASS**, exit 0: 38 passed, 3 files |
| Full frontend suite: `node_modules/vitest/vitest.mjs run --reporter=verbose --no-color` | **PASS**, exit 0: 107 passed, 19 files |
| `node_modules/vue-tsc/bin/vue-tsc.js --noEmit` | **PASS**, exit 0 |
| `git diff --check -- src/features/assessment/assessment.store.ts src/features/assessment/AssessmentPage.vue` | **PASS**, exit 0 |

The assessment suite covers stale same-question success/failure, offline payload preservation, late responses after lesson navigation, feedback matching the selected exercise, retained answers/hints across question switches, and the superseded-load selected-index regression. Other existing assessment tests cover runner polling/cancellation, scoring, and editor drafts.

The output includes Vue Router warnings because page test routers omit the `/lesson/:lessonId` destination. The full suite also includes unresolved `RouterLink` warnings from `tests/course/lesson-components.spec.ts` fixtures. These warnings were preserved, with no test failures. This is unit/component and type-check evidence; browser/GUI acceptance is being performed separately by the parent task.

Raw red/green/full-suite/type-check output and source/test SHA256 values are preserved in `assessment-review-20261021.log`. This review created new audit files and did not overwrite earlier evidence.

## Verified source SHA256

| File | SHA256 |
| --- | --- |
| `apps/web/src/features/assessment/assessment.store.ts` | `4660B896827C49E0C41B740BB01D010E48D4AAB8ACC061DA9685971EC8340D17` |
| `apps/web/src/features/assessment/AssessmentPage.vue` | `EBBE2E430EF2D41F6899895C25CA90CA0DEF3026241A9DB45C43ADF7F3120ABA` |

Used local PowerShell/file tools and the systematic-debugging, test-driven-development, and verification-before-completion skill workflows. No remaining defect was identified in the reviewed asynchronous feedback and exercise-selection cases.
