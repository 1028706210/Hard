# Compare lesson round-trip context review — 2026-10-21

Scope: `apps/web/src/features/compare/ComparePage.vue` and `apps/web/tests/compare/compare-page.spec.ts`.

## Evidence and cause

The existing mobile comparison failure is recorded in `.tool-cache/e2e-frontend-battery-20261021/comparison-compare-mobile--13643-slots-and-lesson-round-trip/error-context.md`. The test filters `pointers`, follows the C++ lesson, then goes back. The returned page shows an empty filter, 45/45 concepts and page 1/12; the requested concept is absent from the first four concepts.

`filter` and `page` were local refs initialized to an empty string and 1. Leaving the comparison page via its lesson link and recreating it on return discarded both values. Pagination exposed that state loss by rendering only the first four concepts.

## Change

- Use existing Vue Router query parameters `filter` and `page` as the source of comparison state.
- Replace the current URL when filtering or paging, so entering a lesson leaves the current comparison state in its preceding history entry.
- Reset the page when changing the filter, remove default query values and preserve unrelated query parameters.
- Fall back to page 1 for invalid, repeated, non-positive, fractional or unsafe page numbers; bound valid page numbers to the current result count.
- Exercise the real memory router and RouterView in the comparison tests, including component removal while viewing a lesson and recreation on back navigation.

No dependencies, state store or separate persistence mechanism were introduced. Existing comparison E2E expectations were not modified. No service or browser E2E run was started by this scoped review.

## Verification

All command output, including intermediate failures, is preserved in `compare-context-review-20261021.log`.

- Before the production change: 16 comparison tests executed; 4 failed and 12 passed. Failures reproduced the empty filter on return, page reset on return, ignored query state and incorrect filtered bookmark results.
- After the production change: the targeted comparison file passed 16/16 tests.
- Final frontend Vitest suite: 19 files, 117/117 tests passed; exit 0.
- Final `vue-tsc --noEmit`: exit 0. The initial type check found two test href values typed as possibly undefined; their non-null DOM references were narrowed and both the full suite and type check rerun successfully.
- Scoped `git diff --check`: exit 0.

The initial `pnpm` entry point reported Node v24.19.0 / pnpm 11.25.0 and refused to start because the project pins Node v24.17.0 / pnpm 11.19.0. Tests and type checking then used the already installed tools directly through `C:/Program Files/nodejs/node.exe`, which was subsequently verified to report **v24.8.0**. The package-manager runtime and directly invoked test runtime must be distinguished. These results do not claim validation under the pinned versions.

Post-run runtime clarification: `& 'C:/Program Files/nodejs/node.exe' --version` returned `v24.8.0`; a separate `node --version` check also returned `v24.8.0`. Every successful test/type-check tool invocation in this review used that absolute executable path. The earlier log heading `RED (installed tools, Node v24.19.0)` incorrectly carried forward the package-manager error's version without checking the directly invoked executable. The original log is preserved; this paragraph corrects its heading and the earlier review summary. Only this review document was updated for the clarification, and no passed suite was rerun.

The browser comparison regression and broader E2E acceptance remain with the root task.

## Source fingerprints

- `ComparePage.vue` SHA-256: `8E167701C3CAA270D0410A10F85CA607E3EEBB8C638682E9D42BC8F6A1A592C6`
- `compare-page.spec.ts` SHA-256: `6EB241BB244B357E1C6F0EB4306193722D6123C23F432CF9548AD9CA0F2E94B6`

Skills used: systematic-debugging for the evidence and root-cause trace, test-driven-development for the reproduced failure before the fix, and verification-before-completion for the final test and type-check evidence. Local shell and file-edit tools were used for source inspection, the scoped changes and validation.
