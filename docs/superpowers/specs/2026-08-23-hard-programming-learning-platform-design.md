# Hard Programming Learning Platform Design

**Date:** 2026-08-23

**Status:** Approved

**Owner:** Project manager and auditor: Codex root task

**Executor:** Terra in a separate task, one implementation task at a time

## 1. Product objective

Hard is a private, local-first programming learning web application for one learner who understands basic syntax but has not studied deeply. It must help the learner complete the full main tutorials for Python, Java, C#, and C++ from 菜鸟教程, practice each topic, run code, earn meaningful scores, revisit weak knowledge, and compare equivalent concepts across languages.

The core learning loop is:

`知识星图 → 选择语言 → 学习章节 → 完成知识题与代码题 → 获得经验和掌握度 → 错题进入间隔复习 → 解锁后续章节`

Success means the learner can study all four complete routes, complete automatically checked exercises on desktop or phone, understand weak areas, and recover all learning data from a local backup.

## 2. Scope

### 2.1 Included in version 1

- Four independent and fully open routes: Python, Java, C#, and C++.
- Every route contains all chapters, examples, and quiz structure in the corresponding main tutorial directory on 菜鸟教程 as captured on 2026-08-23.
- Original Chinese explanations, exercises, answers, and feedback written for Hard. Each lesson links to its source page. Hard does not bulk-copy the source text or reuse its quiz wording.
- Prerequisite ordering inside each language and placement tests that may unlock modules.
- Knowledge questions, executable code questions, module challenges, and route completion challenges.
- Python, Java, C#, and C++ compilation or interpretation on the Windows host.
- Experience, levels, course mastery, badges, streaks, route completion, and scheduled review.
- Full-text search, favorites, lesson notes, cross-language concept comparison, weak-point reports, and code submission history with diffs.
- Desktop and mobile responsive interfaces. Mobile has the same capabilities, including editing and running code.
- Local SQLite storage, automatic backups, manual import/export, and same-Wi-Fi phone access.
- A dark, immersive orbital knowledge-map homepage based on the selected Product Design visual target.

### 2.2 Explicitly excluded from version 1

- AI tutor or any online model dependency.
- Cloud hosting, accounts, multi-user permissions, social features, payments, or public access.
- Docker or container execution.
- Live scraping or runtime synchronization with 菜鸟教程.
- A browser-based course-authoring administration panel.
- Unity, Cocos Creator, Android, databases, Web full stack, testing, Git, Linux, Docker, data structures, or other courses outside the four selected language tutorials.
- A security guarantee for hostile third-party code. The runner is safe enough for the learner's own course submissions, not an adversarial public judge.

## 3. Environment and storage constraints

- Operating system: Windows x64.
- Project root: `D:\projects\1\Hard`.
- All source, project dependencies, virtual environments, learning data, backups, exports, and runner work directories live on drive D.
- Configurable language tools live below `D:\DevTools`.
- Node.js 24.17.0, pnpm 11.19.0, and Git 2.55.0 are already available.
- Install a project-owned Python 3.13.x under `D:\DevTools\python`; do not depend on Codex or Workbuddy internal runtimes.
- Java 17.0.7 and `javac` are already available.
- Install a .NET 10 SDK under `D:\DevTools\dotnet` with the official install script.
- Install MSYS2 UCRT64 and GCC under `D:\DevTools\msys64`.
- Docker is not installed and must not be required.
- The repository is an independent Git repository rooted at `D:\projects\1\Hard`.

Runtime paths inside the project:

- SQLite database: `data/hard.db`
- Daily and weekly backups: `backups/`
- Manual exports: `exports/`
- Per-submission temporary work: `runner-work/`

All four paths are excluded from Git.

## 4. User experience and information architecture

### 4.1 Primary destinations

1. **知识星图主页** — language worlds, current lesson, daily goals, mastery, level, streak, and primary resume action.
2. **课程学习** — chapter navigation, original lesson text, examples, favorites, and notes.
3. **练习评分** — objective questions, Monaco code exercises, module challenges, and route challenges.
4. **错题复习** — deterministic spaced-review queue and ordinary wrong-answer browser.
5. **全文搜索** — course text, knowledge points, notes, and favorites.
6. **跨语言对照** — concept-aligned syntax and semantic comparisons across the four languages.
7. **成长与成就** — experience, level, badges, mastery, code diffs, weekly report, and learning heatmap.
8. **设置与数据** — daily goals, local tool status, phone access address, backups, imports, and exports.

### 4.2 Desktop design

The 1440 × 1024 visual target is a full-viewport deep-navy knowledge universe. A central current-lesson planet owns the main action. Python, Java, C#, and C++ domain worlds connect through orbital prerequisite paths. Violet is the primary action color; cyan, amber, and red are restrained status accents. Progress and review information sit at the edges of the map rather than inside a dense dashboard grid.

The selected reference is stored at `docs/design/hard-homepage-visual-target.png`.

### 4.3 Mobile design

The mobile layout converts orbital paths into a vertical route map rather than shrinking the desktop canvas. It retains course reading, notes, objective questions, Monaco editing, compilation, tests, review, scores, and backups. The code workspace supports portrait mode and offers a focused landscape layout with editor and output panes.

The mobile browser connects to the Windows host over the same Wi-Fi. The host must be running. No login or pairing is required, so the UI must warn that other devices on the same network may access learning data and code execution.

## 5. Architecture

Hard is a local modular monolith with independently testable modules.

### 5.1 Frontend

Vue 3 and TypeScript provide the desktop and mobile application. Vue Router owns navigation, Pinia owns client state, and Monaco Editor owns code editing. The frontend communicates only through the versioned FastAPI interface and never reads the database or course filesystem directly.

### 5.2 Backend

FastAPI exposes modules for content, progress, assessment, review, search, analytics, notes, backup, environment health, LAN access, and code execution. Module boundaries are expressed as service interfaces rather than internal HTTP microservices.

### 5.3 Content library

Course content is version-controlled and read-only at runtime:

```text
content/
  sources.yaml
  concepts.yaml
  python/
    course.yaml
    <module>/<lesson>.md
    <module>/<lesson>.exercises.json
  java/
  csharp/
  cpp/
```

`course.yaml` defines modules, ordering, prerequisites, placement tests, and source coverage. Lesson front matter defines the stable lesson ID, title, concepts, objectives, prerequisites, difficulty, source URL, and source snapshot date. Exercise JSON separates starter code and visible tests from server-only reference solutions and hidden tests.

`concepts.yaml` supplies stable cross-language concept IDs such as variables, loops, functions, classes, exceptions, generics, collections, and memory management.

### 5.4 Data store

SQLite is the single source of truth for mutable user state. It stores settings, daily goals, lesson progress, attempts, code submissions, mastery snapshots, review scheduling, notes, favorites, achievements, backups, and content-version metadata. FTS5 indexes course text plus user notes. Database changes use versioned migrations and transactions; WAL mode is enabled.

### 5.5 Code runner center

A runner manager accepts a normalized submission and delegates it to one adapter:

- Python adapter: interpret with project-owned Python 3.13.x.
- Java adapter: compile with `javac` and run with `java` 17.
- C# adapter: compile and run with the project-selected .NET 10 SDK.
- C++ adapter: compile with MSYS2 UCRT64 `g++` and run the resulting executable.

Every adapter implements the same contract: validate input, prepare a temporary directory, compile when required, run visible and hidden tests, normalize diagnostics, terminate the process tree, return a structured result, and clean the directory.

### 5.6 Learning analysis

The analysis module calculates mastery, schedules review, aggregates weak concepts, correlates compiler errors, and produces code diffs between adjacent submissions. It is deterministic and contains no AI calls.

## 6. Content acquisition and copyright policy

The build process uses 菜鸟教程 only as the approved scope and reference source. A source manifest records every expected main-tutorial page for Python, Java, C#, and C++. Content workers write original explanations and original questions, include a source link, and do not reproduce long passages, images, or existing quiz wording.

The content pipeline is:

`source manifest → original Markdown lesson → exercise JSON → schema validation → reference-solution execution → coverage report → human sample audit`

A language batch cannot pass audit until its manifest reports 100% main-tutorial chapter coverage, all internal references resolve, all question IDs are unique, all reference solutions pass, and no placeholder content remains.

## 7. Learning, scoring, and unlocking

### 7.1 Mastery

Each course mastery score is 0–100 and uses approved weights:

- Knowledge-question performance: 30%
- Code-exercise performance: 40%
- Module-challenge performance: 20%
- Scheduled-review retention: 10%

Unattempted required items contribute zero. The displayed course mastery is the weighted aggregate of completed and required work. A lesson passes at 70; a module or course is marked mastered at 85.

### 7.2 Experience and retries

Experience is awarded only on the first successful completion of an eligible lesson, exercise, challenge, review milestone, or badge condition. Repeating work can improve mastery but cannot repeatedly farm experience. Experience values live in reviewed content metadata so they are visible and testable.

Hint penalties apply only to the current attempt. A small hint reduces the item score slightly, a stronger hint reduces it further, and revealing the answer makes that item worth zero for the attempt. The learner may retry immediately.

### 7.3 Unlocking and placement

All four language routes are visible and selectable from the start. Within a language, passing a prerequisite lesson unlocks the next lesson. A placement test score of at least 85 unlocks its covered module. Skipped lessons are marked validated rather than completed and do not grant ordinary completion experience.

### 7.4 Review

Wrong or weak concepts enter a deterministic interval sequence of 1, 3, 7, 14, 30, and 60 days. A review score of at least 80 advances the interval, 60–79 preserves it, and below 60 moves the concept back one interval. The ordinary wrong-answer browser remains available separately.

### 7.5 Weakness and growth reports

Weakness reports rank concept tags using recent incorrect answers, hint use, compile-error categories, failed hidden tests, and review lapses. The report points to existing lessons and exercises only. Code growth records keep each submitted source, normalized test result, score, timestamp, and adjacent text diff.

## 8. Code execution safety

The runner is designed for the owner's own course code, not hostile public submissions.

- Only allowlisted executables and fixed argument templates may launch.
- Each submission uses a unique directory below `runner-work/`.
- Source size, compile time, runtime, output size, and concurrent jobs are limited.
- Environment variables and executable search paths are reduced to the adapter's needs.
- The complete child process tree is terminated on timeout or cancellation.
- User-supplied paths and compiler arguments are never interpolated into shell command strings.
- Hard's `data/`, `backups/`, and `exports/` paths are never used as working directories or passed to submissions.
- Work directories are removed after results are persisted.

Without a container or virtual machine, this cannot guarantee filesystem or network isolation against malicious code. The limitation is shown in developer-facing documentation and prevents future public exposure without a runner redesign.

## 9. Runtime data flow

### 9.1 Lesson flow

1. The frontend requests a lesson by stable ID.
2. The content service loads validated Markdown and exercise metadata.
3. The progress service records reading position separately from immutable content.
4. Objective answers are scored synchronously and stored as attempts.
5. Code submissions enter the runner queue and return a job ID.
6. The chosen adapter compiles, runs tests, and returns normalized diagnostics.
7. The assessment service persists the attempt and submission.
8. Mastery, experience, review schedule, achievements, and weak-concept aggregates update in one transaction.
9. The frontend receives the result and updated progress snapshot.

### 9.2 Mobile flow

The same API serves desktop and mobile. If the phone loses its LAN connection, the current lesson position, answer draft, note draft, and code draft remain in browser storage. Reconnection resubmits only unsaved drafts with an idempotency key.

## 10. Error handling

- Compilation errors show normalized filename, line, column, original compiler message, and a concise Chinese category label.
- Failed tests show pass counts, visible failure details, and configured hints; hidden-test secrets are not returned.
- Timeouts and output overflow terminate the process tree and explain likely causes such as an infinite loop.
- A missing tool disables only the affected language runner and shows the expected D-drive path and health-check evidence.
- A malformed content file is isolated from the catalog and included in a startup report; valid courses remain usable.
- Database writes are transactional. A migration failure leaves the previous database untouched and restores the pre-migration snapshot.
- API errors use stable error codes and user-readable Chinese messages. Raw stack traces stay in local logs.

## 11. Backup and recovery

- Create a backup before every schema migration.
- Create one daily backup after the first successful learning write of the day.
- Retain the seven newest daily backups and four newest weekly backups.
- Checkpoint WAL before copying the database.
- A manual export contains the database, settings manifest, content-version manifest, and checksum list.
- Before an import, snapshot the current state. Validate checksums and schema compatibility before replacing data. Roll back automatically on failure.
- Backups under the same D drive protect against accidental changes and database corruption, not physical drive failure. The UI reminds the learner to copy manual exports to another disk when needed.

## 12. LAN access

Phone access is opt-in and binds to the selected private LAN interface. The interface displays a QR code and local address. Windows Firewall access must be restricted to private networks; opening a firewall rule requires explicit user approval during implementation.

No authentication is included by user choice. The product must not configure router port forwarding, public tunnels, or cloud exposure. Each LAN start shows a warning that devices on the same network may access learning data and submit code.

## 13. Testing and acceptance

### 13.1 Automated testing

- Frontend unit and component tests cover navigation, stores, responsive behavior, editor state, scoring displays, and offline drafts.
- Backend unit tests cover content parsing, scoring, mastery, review, search, backup, migrations, and every service boundary.
- Integration tests use temporary SQLite databases and temporary content fixtures.
- Each runner has compile/run success, compile failure, test failure, timeout, output overflow, process-tree cleanup, and missing-tool tests.
- End-to-end tests cover the primary learning loop, placement, review, search, notes, code history, backup restore, desktop viewport, and mobile viewport.
- Content validation checks schema, unique IDs, prerequisites, concept IDs, source links, reference solutions, hidden tests, and source-manifest coverage.

### 13.2 Visual and accessibility acceptance

- The desktop homepage is compared at 1440 × 1024 against the selected visual target.
- The mobile layout has no horizontal page overflow and uses a vertical route map.
- Core flows work by keyboard and touch.
- Focus indication, labels, contrast, reduced-motion behavior, and semantic landmarks are present.
- Compilation and network wait states are visible and cancellable.

### 13.3 Definition of done

Version 1 is complete only when all four source manifests report 100% main-tutorial coverage, all required tests pass, every runner is healthy on the documented D-drive toolchain, desktop and mobile core flows pass end-to-end, backup restoration is proven, no placeholder content remains, and the audit history contains an approved task for every delivered capability.

## 14. Terra execution and audit protocol

The implementation plan is written for Terra in another Codex task. Terra receives exactly one task at a time.

Each implementation task must:

1. Stay within the named files and acceptance criteria.
2. Write a failing test or validator first when behavior changes.
3. Implement the minimum code or content required.
4. Run the specified focused tests and relevant regression suite.
5. Produce one atomic Git commit.
6. Report commit hash, changed files, commands, results, UI screenshots when applicable, content coverage when applicable, and known limitations.
7. Stop and wait for audit.

The project manager audits requirement fit, scope discipline, code or content quality, test evidence, visual fidelity, and absence of placeholders. A rejected task is corrected in place before any later task begins.

## 15. Delivery sequence

1. D-drive toolchain, repository, schemas, contracts, and continuous validation.
2. End-to-end Python slice: content pipeline, lessons, questions, runner, scoring, review, search, notes, backups, and responsive UI.
3. Java runner and complete Java course batch.
4. C# runner and complete C# course batch.
5. C++ runner and complete C++ course batch.
6. Cross-language comparison, weak-point reports, code-growth views, achievement polish, visual QA, security regression, and release verification.

Every sequence item must leave a usable, tested product. Content production is divided into audited module-sized tasks rather than one unreviewable language dump.

## 16. Principal risks and controls

- **Content volume:** four complete tutorials are large. Control with source manifests, module batches, automated coverage, and per-batch human sampling.
- **Copyright:** control with original writing, original questions, source links, and no bulk reuse of source text or images.
- **Runner safety:** control with allowlisted commands, limits, process-tree cleanup, local-only scope, and an explicit non-hostile-code boundary.
- **Mobile code editing:** control with responsive Monaco layouts, landscape workspace, touch testing, and draft recovery.
- **Tool installation on a full C drive:** control with D-drive install roots, D-drive caches, health checks, and no Visual Studio Build Tools dependency.
- **No LAN authentication:** control with opt-in private-interface binding, warnings, private-network firewall scope, and no public exposure.
- **Long implementation:** control with a Python vertical slice, one Terra task at a time, atomic commits, and mandatory audit gates.
