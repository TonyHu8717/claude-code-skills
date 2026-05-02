# Module Brief Template

Use this template during **Phase 2.5** for complex codebases. Save completed briefs to `course-name/briefs/0N-slug.md`. The brief gives a writing agent everything it needs to produce one module — without reading the codebase or SKILL.md.

---

## Module N: [Title]

### 1. Teaching Arc

**Metaphor:**
A fresh, specific metaphor — never "restaurant." Pick something that feels inevitable for this concept.

**Opening hook:**
One sentence connecting to something the learner already knows from using the app.

**Key insight:**
The single most important takeaway for this module. What should the learner remember a week from now?

**"Why should I care?":**
How does this knowledge help the learner steer AI, debug problems, or make better decisions?

### 2. Code Snippets (pre-extracted)

Copy-paste the actual code from the codebase. Include file paths and line numbers. The writing agent will use these verbatim — it will NOT re-read the codebase.

```javascript
// File: src/api/handler.js, lines 12-24
const response = await fetch(url, {
  method: 'POST',
  headers: { 'Authorization': apiKey }
});
```

### 3. Interactive Elements

Checklist of interactive elements for this module:

- [ ] **Code↔English translation** — which snippets?
- [ ] **Quiz** — how many questions? What style? (multiple-choice / scenario / drag-and-drop / spot-the-bug)
- [ ] **Group chat animation** — which actors? What conversation?
- [ ] **Data flow animation** — which actors? What steps?
- [ ] **Drag-and-drop** — what items and targets?
- [ ] **Other** — architecture diagram? layer toggle? pattern cards?

### 4. Reference Files to Read

List the specific sections of reference files the writing agent needs:

- `references/content-philosophy.md` — always include
- `references/gotchas.md` — always include
- `references/interactive-elements.md` — sections for the element types listed above
- `references/design-system.md` — sections for visual elements used

### 5. Connections

**Previous module:** [Title] — brief description of where we left off

**Next module:** [Title] — brief description of where we're going next

**Course-wide consistency notes:** Any tone, style, accent color, or actor naming conventions to maintain across modules.
