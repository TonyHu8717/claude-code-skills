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
