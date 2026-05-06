# Content Philosophy

Guidance for Phase 2.5 (briefs) and Phase 3 (writing modules). Every rule here exists to keep the course visual, engaging, and useful for non-technical learners.

## Visual-First Approach

- Text blocks are capped at **2-3 sentences** per screen
- **Every screen must be at least 50% visual** — diagrams, cards, animations, code blocks
- Lists of 3+ items should become cards, flow diagrams, or step cards
- Sequences should become numbered step cards or flow animations
- Comparisons should become side-by-side columns
- Use generous whitespace — let content breathe
- At least one "hero visual" per module (a large diagram, animation, or interactive element)

## Code & English Translations

- Every code snippet requires a side-by-side plain English explanation
- Code must **never produce horizontal scrollbars** — use `white-space: pre-wrap`
- Original code must appear **exactly as-is** without modification or trimming
- Select naturally concise snippets (5-10 lines) that demonstrate the concept
- English translations should explain the **why**, not just the **what**
- Use conversational language: "Include our API key so the server knows who we are" not "Set the Authorization header"

## One Concept Per Screen

Each screen teaches a single idea. Rather than cramming content, add more screens. If a screen covers two distinct concepts, split it.

## Metaphor Strategy

New concepts start with a real-world metaphor before grounding them in code.

**Strict rules:**
- NEVER use the "restaurant" or "kitchen" metaphor — it's overused
- NEVER reuse the same metaphor across modules
- Each module needs its own metaphor that feels naturally suited to that concept
- The best metaphors feel *inevitable* for the concept, not forced
- If you catch yourself using a metaphor twice, stop and find a new one

## Learn by Tracing

Content should follow real user actions through the system end-to-end, leveraging the learner's existing experience with the app. Start with "you click this button" and trace what happens through the code.

## Glossary Tooltips

Every technical term gets a dashed-underline tooltip on first use in each module.

**Rules:**
- Use `cursor: pointer` (not `cursor: help` — pointer feels clickable and inviting)
- Append tooltips to `document.body` with `position: fixed` (prevents clipping by `overflow: hidden` containers)
- Cover anything a non-technical person might not know — including software names, acronyms, and programming concepts
- Keep definitions to 1-2 sentences in everyday language
- Use a metaphor in the definition when it helps
- Don't mark the same term twice within the same screen

## Beginner Modification Guidance (Submodules)

When writing submodule content aimed at enabling simple code modifications:

### Code Block Standards
- **Show complete functions**, not fragments — include the full function signature, all parameters, and return statement
- **Include line numbers** in code blocks using `<span class="line-num">N</span>` pattern
- **Mark extension points** with `// [EDIT HERE]` comments in the code
- **Include file path + line range** above each code block: `// File: Scheduler.cpp:142-178`

### Modification-Oriented Screens
Each submodule should have at least one screen structured as:
1. **The problem**: "How do I add a new VSYNC source type?"
2. **The context**: What data structure holds the existing types?
3. **The exact location**: File path and line numbers
4. **The change**: Complete before/after code comparison
5. **The verification**: How to test the change

### Spot-the-Bug Pattern
Use `.bug-challenge` from `interactive-elements.md` to create exercises where beginners identify the buggy line. Common bugs to include:
- Missing `break` in switch statements
- Off-by-one errors in buffer indices
- Wrong parameter order in function calls
- Forgetting to acquire/release mutex locks

### Practice Exercise Format
```html
<div class="callout callout-accent">
  <div class="callout-icon">✏️</div>
  <div class="callout-content">
    <strong class="callout-title">动手练习</strong>
    <p>如果要支持一种新的合成模式（如 DRM leased 显示），应该在 Scheduler.cpp 的哪个函数中添加分支？提示：看 handleFrameMetadata() 函数。</p>
  </div>
</div>
```

### Common Gotchas to Highlight
- Binder transactions are one-way: caller doesn't block waiting for reply unless explicitly requested
- BufferQueue slots are indexed from 0 but slot allocation is ref-counted
- HWC prepare/commit must be called in pairs — never skip the commit
- VSync callbacks execute on a different thread than the main SurfaceFlinger thread

## Quiz Design

Quizzes come at module end (3-5 questions) and prioritize **practical application over memorization**.

**Question type hierarchy (most to least valuable):**
1. Scenario-based problem-solving ("What would you do if...")
2. Tracing exercises ("If the user clicks X, what happens next?")
3. Pattern recognition ("Which approach is better for this situation?")
4. Concept application ("How would you explain this to the AI?")

**Rules:**
- Wrong answers should deliver **encouraging, non-judgmental explanations**
- Scoring metrics are explicitly avoided — "the quiz is a thinking exercise, not an exam"
- Never ask "What does API stand for?" or other definition-recall questions
- Each question should present a novel scenario requiring the learner to *apply* what they've learned
