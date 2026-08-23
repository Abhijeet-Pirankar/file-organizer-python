---
name: automatic_project_continuity
description: Automatically maintains project continuity using AI_PROGRESS.md.
---

# Automatic Project Continuity Rule

You MUST manage project continuity automatically. Do NOT ask the user to manually maintain progress files or remind you of this rule.

## 1. Automatic Continuation
Before starting ANY task:
- Inspect the current project files and Git branch/status.
- Check what has already been implemented by reviewing the code directly.
- Read `AI_PROGRESS.md` to determine the last recorded state.
- Compare `AI_PROGRESS.md` with the actual project state and correct it if outdated.
- Continue from the existing implementation instead of restarting. Do NOT assume a previous task is incomplete just because it is mentioned in an old message. The actual project code is the source of truth.
- Do NOT repeat work (no recreating existing components, deleting working files unnecessarily, etc.).

## 2. Automatic Progress Tracking
You are responsible for creating and updating `AI_PROGRESS.md` in the root of the project. I should NEVER have to manually update it.

After every significant task or implementation, OR when you reach a context limit/session limit and need to stop, update `AI_PROGRESS.md` with:

```md
## CURRENT TASK
[what you were working on]

## COMPLETED
[what actually finished]

## IN PROGRESS
[what was partially completed]

## REMAINING
[what still needs to be done]

## ERRORS
[any current errors]

## NEXT STEP
[the exact next action]
```
Do not claim something is complete if it was only partially implemented. Keep it concise. Do NOT create multiple progress files.

## 3. Git Safety
Never automatically:
- switch branches
- git reset --hard
- delete working files
- force push
- overwrite unrelated changes
- revert previous work

Always inspect `git status` and `git branch` before making major changes. Do NOT commit or push unless explicitly asked.

## 4. Quality Control
After significant changes:
- Run the appropriate TypeScript check (e.g. `npx tsc --noEmit`).
- Run the frontend build (e.g. `npm run build`).
- Check for runtime errors.
- Verify the application still starts.
- Update `AI_PROGRESS.md`.
If something fails, record the failure in `AI_PROGRESS.md` and continue fixing it rather than marking the task complete.

## IMPORTANT
`AI_PROGRESS.md` is a HANDOFF/BACKUP mechanism. The actual source code is always the final source of truth. Never blindly trust `AI_PROGRESS.md` if the code says otherwise.
