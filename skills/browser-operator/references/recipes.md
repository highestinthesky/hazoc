# Browser Operator Recipes

## Use this skill vs not

Use this skill when the task needs:

- a real logged-in session
- JavaScript-rendered content
- buttons, forms, filters, dropdowns, tabs, modals
- screenshots or PDF capture

Do not use it for:

- normal web search
- basic article extraction
- reading static docs pages

## Common flows

### Open and inspect

```bash
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser get title
agent-browser get url
```

### Fill and submit a form

```bash
agent-browser open https://example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser wait --url "/dashboard"
agent-browser snapshot -i
```

### Click through a dashboard

```bash
agent-browser open https://app.example.com
agent-browser snapshot -i
agent-browser click @e4
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser get text @e7
```

### Take evidence

```bash
agent-browser screenshot page.png
agent-browser screenshot --full full.png
agent-browser pdf page.pdf
```

### Debug a flaky page

```bash
agent-browser open https://example.com --headed
agent-browser snapshot -i
agent-browser console
agent-browser errors
```

## Wait strategy

Prefer these in order:

1. `wait --url`
2. `wait --text`
3. `wait --load networkidle`
4. fixed millisecond wait only as fallback

## Notes on refs

Refs like `@e1` are tied to the current page state. After navigation or major DOM changes, throw them away and snapshot again.
