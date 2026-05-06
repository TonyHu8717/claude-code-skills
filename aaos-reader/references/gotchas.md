# Gotchas — Common Failure Points

> This section applies during Phase 3 (module HTML writing) and Phase 4 (review). Every item below must be checked before declaring a course complete.

These represent genuine issues that arise during course construction. All must be verified before a course is considered done.

### Tooltip Clipping

Translation blocks rely on `overflow: hidden` for wrapping. Tooltips using `position: absolute` inside the term element get clipped by the container. **Fix:** Tooltips should use `position: fixed` and attach to `document.body`, computing position via `getBoundingClientRect()`. `main.js` already handles this, yet it remains the most frequent bug across every build.

### Not Enough Tooltips

Under-tooltiping is the most prevalent failure. Learners without technical backgrounds won't recognize terms such as REPL, JSON, flag, entry point, PATH, pip, namespace, function, class, module, PR, E2E, or software names like Blender/GIMP. **Guideline:** if a term wouldn't come up in casual conversation with a non-technical friend, add a tooltip. Over-tip rather than under-tip. However, avoid tooltiping domain-specific terms the learner already understands (e.g., AI/ML terminology for someone working in AI).

### Walls of Text

The course ends up resembling a textbook rather than an infographic — typically caused by writing more than two to three consecutive sentences without a visual break. Each screen should be at least half visual. Lists of three or more items should become cards, sequences should become step cards or flow diagrams, and code explanations should use code↔English translation blocks.

### Recycled Metaphors

Reusing a single metaphor (like "restaurant" or "kitchen") repeatedly. Each module demands its own metaphor that feels naturally suited to that particular concept. If the same metaphor comes up twice, pause and find one that organically fits instead.

### Code Modifications

Trimming, simplifying, or "cleaning up" snippets from the actual codebase. Learners should be able to open the real file and find identical code. Rather than editing for brevity, *select* naturally concise snippets (5–10 lines) from the codebase that demonstrate the concept.

### Quiz Questions That Test Memory

Questions like "What does API stand for?" or "Which file handles X?" test recall rather than comprehension. Each quiz question should present a novel scenario and require the learner to *apply* what they've learned.

### Scroll-Snap Mandatory

Setting `scroll-snap-type: y mandatory` can trap users inside lengthy modules. Use `proximity` instead.

### Module Quality Degradation

Writing all modules in a single pass leads to later modules being thin and underdeveloped. Build and verify one module at a time. For complex codebases, leverage the parallel path with module briefs.

### Missing Interactive Elements

Modules containing only text and code blocks with no interactivity. Each module must include at least one of: quiz, data flow animation, group chat, architecture diagram, or drag-and-drop. These are not decorative — they serve as the primary way non-technical learners process and retain information.

### HTML Elements Not Matching JS Engine Conventions — CRITICAL

The most common and severe failure mode: the HTML uses different class names, data attributes, or button structures than what `main.js` expects. The JS engine silently fails because it scans for specific CSS class selectors and `data-*` attributes — if they don't match, nothing happens. There are no console errors to help diagnose this.

**This typically happens when agents write HTML from memory instead of copying the exact patterns from `references/interactive-elements.md`.** The HTML patterns in that file are the contract between content and engine. Every deviation breaks something.

**Mandatory verification checklist (check every interactive element):**

| Component | Must-Have Selectors/Attributes | Common Mistakes |
|---|---|---|
| **Quiz** | `.quiz-question-block` with `data-correct`, `data-explanation-right`, `data-explanation-wrong`; `.quiz-option` with `data-value` and `onclick="selectOption(this)"`; `.quiz-feedback` | Using `data-answer` instead of `data-value`; missing `onclick`; missing `data-correct` on the question block |
| **Chat** | `.chat-window` with `id`; `.chat-message` with `data-sender` and `style="display:none"`; `.chat-typing` with `style="display:none"`; `.chat-next-btn`, `.chat-all-btn`, `.chat-reset-btn`; `.chat-progress` | Messages visible by default (no `display:none`); missing `data-sender` (actor map fails); using `id` instead of class on control buttons; missing `.chat-typing` element |
| **Flow Animation** | `.flow-animation` with `data-steps='[...]'`; `.flow-actor` with `id="flow-xxx"`; `.flow-next-btn`, `.flow-reset-btn`; `.flow-progress`; `.flow-packet`; `.flow-step-label` | Missing `data-steps` (the engine has no steps to run); using custom button `id` instead of class `.flow-next-btn`; missing `.flow-packet` element (packet animation silently fails); actor `id` mismatch with `data-steps` values |
| **Bug Challenge** | `.bug-challenge` container; `.bug-line` with `onclick="checkBugLine(this, true/false)"`; `.bug-feedback` | Using `<pre>` code blocks instead of individual `.bug-line` elements; missing `checkBugLine` onclick handlers |
| **DnD** | `.dnd-container`; `.dnd-chip` with `data-answer` and `draggable="true"`; `.dnd-zone` with `data-correct`; `.dnd-zone-target` | Missing `draggable="true"` on chips; zone `data-correct` not matching chip `data-answer` |
| **Layer Toggle** | `.layer-demo` container; `.layer` with `id`; `.layer-tab` with `onclick="showLayer('id', this)"` | Missing `.layer-demo` wrapper; `showLayer` called with wrong ID |

**The golden rule:** Copy the HTML pattern from `references/interactive-elements.md` character by character, then substitute only the content text. Do not invent alternative class names, data attributes, or button structures. The JS engine's selectors are exact strings — even `quiz-option` vs `quiz_option` will break functionality.

### Chat Messages Not Initially Hidden

All `.chat-message` elements must have `style="display:none"`. If any message is visible on page load, the chat will appear pre-revealed and the step-by-step animation effect is lost. The JS engine's `showNext()` sets `display: flex` on the next message, so pre-visible messages disrupt the sequence.

### Flow Animation Packet ID Conflicts

When a page contains multiple flow animations, each `.flow-packet` element creates animation keyframes. If multiple flow animations share the same page, ensure each `.flow-animation` has a unique context — the JS engine scopes packet lookups via `.flow-packet` within the container, but `id` collisions on other elements (actors, labels) can cause unpredictable behavior.

### Quiz Feedback Text Accumulation

When using custom quiz implementations (not the standard engine), ensure `resetQuiz()` restores the original feedback text content. Prepending "Correct!" or "Wrong!" without saving/restoring the original text causes feedback text to accumulate prefixes on each reset + re-answer cycle. Store original text via `data-original-text` or a closure variable.
