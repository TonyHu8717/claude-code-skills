---
name: chrome-devtools-mcp
description: Guide for using Chrome DevTools MCP to control a live Chrome browser for automation, debugging, and performance analysis. Use when you need to automate browser tasks, debug web applications, analyze page performance, take screenshots, inspect network requests, or test web UI changes. Requires Chrome DevTools MCP server running as an MCP server.
---

# Chrome DevTools MCP

Control a live Chrome browser through the Model Context Protocol. This enables reliable browser automation, deep debugging, and performance analysis directly from Claude Code.

## Quick Setup

### 1. Add MCP Server

Add to your Claude Code MCP settings (`~/.claude/settings.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### 2. Start Chrome with Remote Debugging

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Windows
start chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

### 3. Verify Connection

Use `list_pages` to confirm the browser is connected.

---

## Core Workflows

### Browser Automation

**Navigate and interact:**
```
1. navigate_page(url="https://example.com")
2. take_snapshot()           # Get page content with element UIDs
3. click(uid="element-uid") # Click elements by UID
4. fill(uid="input-uid", value="text")
5. take_screenshot()
```

**Form automation:**
```
1. take_snapshot()
2. fill_form(elements=[...])  # Fill multiple fields at once
3. click(uid="submit-uid")
```

**Handle dialogs:**
```
1. handle_dialog(action="accept", promptText="optional input")
```

### Performance Analysis

**Trace page load:**
```
1. performance_start_trace(reload=true, filePath="trace.json.gz")
2. performance_stop_trace(filePath="trace.json.gz")
3. performance_analyze_insight(insightSetId="...", insightName="...")
```

**Lighthouse audit:**
```
1. lighthouse_audit(device="desktop", mode="navigation")
```

### Network Debugging

**Inspect requests:**
```
1. list_network_requests(resourceTypes=["script", "stylesheet"])
2. get_network_request(reqid=123)
```

### Console & Debugging

**Check console:**
```
1. list_console_messages()
2. get_console_message(msgid=1)
```

**Run scripts:**
```
1. evaluate_script(function="() => document.title")
```

### Emulation

**Device testing:**
```
1. emulate(viewport="390x844x3,mobile,touch", colorScheme="dark")
2. navigate_page(url="https://example.com")
```

**Network throttling:**
```
1. emulate(networkConditions="Slow 4G")
```

---

## Tool Categories

| Category | Tools | Use Case |
|----------|-------|----------|
| **Navigation** | `navigate_page`, `new_page`, `list_pages`, `select_page`, `wait_for` | Open URLs, switch tabs, wait for content |
| **Input** | `click`, `fill`, `fill_form`, `type_text`, `press_key`, `hover`, `drag` | Form filling, UI interaction |
| **Performance** | `performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight` | Core Web Vitals, page load analysis |
| **Network** | `list_network_requests`, `get_network_request` | Debug API calls, resource loading |
| **Debugging** | `evaluate_script`, `list_console_messages`, `take_screenshot`, `take_snapshot` | Inspect page state, errors, screenshots |
| **Memory** | `take_memory_snapshot`, `load_memory_snapshot`, `get_nodes_by_class` | Memory leak investigation |
| **Emulation** | `emulate`, `resize_page` | Device testing, geolocation, dark mode |

---

## Common Patterns

### Wait for Page Load
```javascript
navigate_page(url="https://example.com", timeout=30000)
wait_for(text=["Loading complete", "Error"], timeout=30000)
```

### Screenshot After Action
```javascript
click(uid="btn-uid")
take_screenshot(filePath="result.png")
```

### Multi-step Form
```javascript
take_snapshot()
fill_form(elements=[
  {uid: "name-input", value: "John"},
  {uid: "email-input", value: "john@example.com"}
])
click(uid="submit-btn")
```

### Debug Failed Load
```javascript
list_console_messages()
list_network_requests(resourceTypes=["document"])
evaluate_script(function="() => document.body.innerHTML")
```

---

## Troubleshooting

**Browser not connecting:**
- Ensure Chrome is running with `--remote-debugging-port=9222`
- Check no firewall blocking localhost:9222

**Tools not working:**
- Use `list_pages` to verify correct page is selected
- Try `take_snapshot` to get fresh element UIDs (they change on navigation)

**Performance trace too large:**
- Use `autoStop=true` or limit trace duration
- Filter with `filePath="trace.json.gz"` for compression

---

## Tool Reference

Full tool reference: https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md
