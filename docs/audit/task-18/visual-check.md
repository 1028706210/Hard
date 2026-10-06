# Task 18 visual check

- `desktop-1440x1024.png`: inspected after a local trusted-run result. Python Monaco is active in the left workspace, the allowed runner aggregate is shown in the right output panel, and no private answer, reference solution, or hidden-test text is present.
- `mobile-390x844.png`: inspected in portrait mode. The explicit 编辑器/结果 controls switch panels without relying on orientation hover; the textarea fallback remains available when Monaco has not loaded.
- Browser checks submitted a knowledge choice, completed a server runner job, sent only its job ID for scoring, and asserted that private runner terms do not reach the rendered page.
