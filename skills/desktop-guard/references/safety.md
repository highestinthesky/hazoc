# Desktop Guard safety notes

## Core rule

Desktop control is real-world control. Treat it like touching the keyboard and mouse yourself.

## Default operating stance

1. Inspect first (`position`, `windows`, `screenshot`)
2. Mutate only with explicit user intent
3. Keep actions small and checkable
4. Prefer dry-run unless the user wants real execution

## Sensitive surfaces

- screenshots may capture secrets
- clipboard may contain secrets
- hotkeys can trigger destructive actions in the wrong window
- clicks are context-sensitive; stale coordinates are dangerous

## Preferred workflow

- identify target window
- inspect/screenshot if needed
- do one small live action
- re-check state
- continue only if still correct
