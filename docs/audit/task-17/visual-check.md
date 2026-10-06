# Task 17 visual check

- `desktop-1440x1024.png`: inspected with a local intercepted content response. The chapter sidebar, sanitized lesson body, structured source link, and notes/favorite tools form three readable columns without horizontal overflow.
- `mobile-390x844.png`: inspected after opening and closing the explicit lesson-directory control. The content and note tool stack vertically, and the long-form surface has no horizontal overflow.
- The interaction test saved a note, toggled a favorite, and exercised the source link. Store regressions prove failed note drafts remain local and retry with their original idempotency key.
