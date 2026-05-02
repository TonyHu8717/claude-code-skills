# Design System Reference

Complete CSS design token library for the course system. All tokens are defined in `references/styles.css` and can be overridden per-course via `:root` in `_base.html`.

## 1. Color Palette

### Backgrounds
| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#FAF7F2` | Primary background — warm off-white, like aged paper |
| `--color-bg-warm` | `#F5F0E8` | Alternating module background — slightly warmer |
| `--color-bg-code` | `#1E1E2E` | Code blocks — deep indigo-charcoal |

### Text
| Token | Value | Usage |
|-------|-------|-------|
| `--color-text` | `#2C2A28` | Primary text — dark charcoal, never pure black |
| `--color-text-secondary` | `#6B6560` | Secondary text — descriptions, subtitles |
| `--color-text-muted` | `#9E9790` | Muted text — labels, hints |

### Borders & Surfaces
| Token | Value | Usage |
|-------|-------|-------|
| `--color-border` | `#E5DFD6` | Standard borders |
| `--color-border-light` | `#EEEBE5` | Subtle borders |
| `--color-surface` | `#FFFFFF` | Cards, containers |
| `--color-surface-warm` | `#FDF9F3` | Translation blocks, warm surfaces |

### Accent (overridden per course in `_base.html`)
| Token | Default | Usage |
|-------|---------|-------|
| `--color-accent` | `#D94F30` | Primary accent — vermillion |
| `--color-accent-hover` | `#C4432A` | Hover state |
| `--color-accent-light` | `#FDEEE9` | Light accent background |
| `--color-accent-muted` | `#E8836C` | Muted accent — visited dots, subtle highlights |

**Accent palette options:**
- **Vermillion** (default): `#D94F30` / `#C4432A` / `#FDEEE9` / `#E8836C`
- **Coral**: `#E06B56` / `#C85A47` / `#FDECEA` / `#E89585`
- **Teal**: `#2A7B9B` / `#1F6280` / `#E4F2F7` / `#5A9DB8`
- **Amber**: `#D4A843` / `#BF9530` / `#FDF5E0` / `#E0C070`
- **Forest**: `#2D8B55` / `#226B41` / `#E8F5EE` / `#5AAD7A`

### Semantic Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-success` | `#2D8B55` | Correct answers, success states |
| `--color-success-light` | `#E8F5EE` | Success backgrounds |
| `--color-error` | `#C93B3B` | Incorrect answers, errors |
| `--color-error-light` | `#FDE8E8` | Error backgrounds |
| `--color-info` | `#2A7B9B` | Info callouts, scenarios |
| `--color-info-light` | `#E4F2F7` | Info backgrounds |

### Actor Colors (for group chat avatars, flow diagrams)
| Token | Value | Usage |
|-------|-------|-------|
| `--color-actor-1` | `#D94F30` | Primary actor (vermillion) |
| `--color-actor-2` | `#2A7B9B` | Secondary actor (teal) |
| `--color-actor-3` | `#7B6DAA` | Tertiary actor (purple) |
| `--color-actor-4` | `#D4A843` | Quaternary actor (amber) |
| `--color-actor-5` | `#2D8B55` | Quinary actor (green) |

**Rule:** Even-numbered modules use `--color-bg`, odd-numbered use `--color-bg-warm` for visual rhythm.

## 2. Typography

### Font Families
| Token | Value | Usage |
|-------|-------|-------|
| `--font-display` | `'Bricolage Grotesque', Georgia, serif` | Headings — bold, geometric, personality |
| `--font-body` | `'DM Sans', -apple-system, sans-serif` | Body text — clean, readable |
| `--font-mono` | `'JetBrains Mono', 'Fira Code', 'Consolas', monospace` | Code — ligatures, clear distinction |

**Never use:** Inter, Roboto, Arial, Space Grotesk — these are too generic.

### Type Scale (1.25 ratio)
| Token | Value |
|-------|-------|
| `--text-xs` | `0.75rem` (12px) |
| `--text-sm` | `0.875rem` (14px) |
| `--text-base` | `1rem` (16px) |
| `--text-lg` | `1.125rem` (18px) |
| `--text-xl` | `1.25rem` (20px) |
| `--text-2xl` | `1.5rem` (24px) |
| `--text-3xl` | `1.875rem` (30px) |
| `--text-4xl` | `2.25rem` (36px) |
| `--text-5xl` | `3rem` (48px) |
| `--text-6xl` | `3.75rem` (60px) |

### Line Heights
| Token | Value | Usage |
|-------|-------|-------|
| `--leading-tight` | `1.15` | Headings |
| `--leading-snug` | `1.3` | Subtitles, short text |
| `--leading-normal` | `1.6` | Body text |
| `--leading-loose` | `1.8` | Long-form reading |

### Google Fonts Link (in `_base.html`)
```html
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400;1,9..40,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

## 3. Spacing & Layout

### Spacing Scale
| Token | Value |
|-------|-------|
| `--space-1` | `0.25rem` (4px) |
| `--space-2` | `0.5rem` (8px) |
| `--space-3` | `0.75rem` (12px) |
| `--space-4` | `1rem` (16px) |
| `--space-5` | `1.25rem` (20px) |
| `--space-6` | `1.5rem` (24px) |
| `--space-8` | `2rem` (32px) |
| `--space-10` | `2.5rem` (40px) |
| `--space-12` | `3rem` (48px) |
| `--space-16` | `4rem` (64px) |
| `--space-20` | `5rem` (80px) |
| `--space-24` | `6rem` (96px) |

### Content Widths
| Token | Value | Usage |
|-------|-------|-------|
| `--content-width` | `800px` | Standard content |
| `--content-width-wide` | `1000px` | Wide content (nav, diagrams) |
| `--nav-height` | `50px` | Fixed nav bar height |

### Module Layout
- Full viewport height: `min-height: 100dvh` with `100vh` fallback
- Scroll-snap: `scroll-snap-type: y proximity` (NOT mandatory)
- Top padding accounts for nav bar: `padding-top: calc(var(--nav-height) + var(--space-12))`

## 4. Shadows & Depth

Four shadow sizes using warm-tinted RGBA values. **Never use pure black shadows.**

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(44,42,40,0.05)` |
| `--shadow-md` | `0 4px 12px rgba(44,42,40,0.08)` |
| `--shadow-lg` | `0 8px 24px rgba(44,42,40,0.10)` |
| `--shadow-xl` | `0 16px 48px rgba(44,42,40,0.12)` |

## 5. Radii

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `8px` | Small elements (badges, buttons) |
| `--radius-md` | `12px` | Cards, code blocks |
| `--radius-lg` | `16px` | Large containers (quiz, chat) |
| `--radius-full` | `9999px` | Pills, circles |

## 6. Animations & Transitions

### Easing Curves
| Token | Value | Usage |
|-------|-------|-------|
| `--ease-out` | `cubic-bezier(0.16,1,0.3,1)` | Entering elements |
| `--ease-in-out` | `cubic-bezier(0.65,0,0.35,1)` | Packet animations |

### Duration Tokens
| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | `150ms` | Hover states, toggles |
| `--duration-normal` | `300ms` | Transitions, reveals |
| `--duration-slow` | `500ms` | Page-level animations |
| `--stagger-delay` | `120ms` | Delay between staggered children |

### Scroll-Triggered Reveal
Use `.animate-in` class on elements. They start invisible and animate in when scrolled into view. The Intersection Observer in `main.js` adds `.visible` class once, so elements animate only once.

```html
<div class="animate-in">
  <!-- content -->
</div>
```

For staggered children, add `.stagger-children` to the parent:
```html
<div class="stagger-children">
  <div class="animate-in">Item 1</div>
  <div class="animate-in">Item 2</div>
  <div class="animate-in">Item 3</div>
</div>
```

## 7. Navigation & Progress

### Fixed Nav Bar
- Position: fixed, top, full width
- Background: `rgba(250,247,242,0.92)` with `backdrop-filter: blur(8px)`
- Contains: course title (left) and module dots (right)

### Progress Bar
- Position: absolute, bottom of nav bar
- Height: 2px, color: accent
- Width updates on scroll via JS

### Nav Dots
Three visual states:
- **Default**: hollow circle, muted border
- **Current** (`.active`): filled accent color with glow ring
- **Visited** (`.visited`): filled muted accent

Tooltip on hover shows module name.

## 8. Syntax Highlighting (Catppuccin-inspired)

All code blocks use `--color-bg-code` (#1E1E2E) background.

| Token Class | Color | Usage |
|-------------|-------|-------|
| `.code-keyword` | `#CBA6F7` | Keywords (const, let, if, return) |
| `.code-string` | `#A6E3A1` | Strings |
| `.code-function` | `#89B4FA` | Function names |
| `.code-comment` | `#6C7086` | Comments |
| `.code-number` | `#FAB387` | Numbers |
| `.code-property` | `#F9E2AF` | Object properties |
| `.code-operator` | `#94E2D5` | Operators |
| `.code-tag` | `#F38BA8` | HTML/JSX tags |
| `.code-attr` | `#F9E2AF` | HTML/JSX attributes |
| `.code-value` | `#A6E3A1` | Attribute values |

## 9. Responsive Breakpoints

### Tablet (768px)
- Scale down `--text-4xl` to `1.875rem`, `--text-5xl` to `2.25rem`, `--text-6xl` to `3rem`
- Translation blocks stack vertically (single column)
- Pattern cards: 2 columns

### Mobile (480px)
- Further scale down type tokens
- Module padding reduced
- Pattern cards: 1 column
- Flow diagrams stack vertically, arrows rotate 90°
- Nav title max-width reduced to 140px

## 10. Scrollbar & Background

### Custom Scrollbar
- Width: 6px
- Track: transparent
- Thumb: `--color-border` with full border-radius

### Atmospheric Background
Body has a subtle radial gradient overlay:
```css
background-image: radial-gradient(
  ellipse at 20% 50%,
  rgba(217,79,48,0.03) 0%,
  transparent 50%
);
```

## 11. Code Block Globals

**Critical rules:**
- All code blocks use `white-space: pre-wrap` — NO horizontal scrollbar, ever
- `word-break: break-word` for wrapping
- `overflow-x: hidden` on all pre/code elements
- Translation code scrollbar hidden via `::-webkit-scrollbar { display: none }`
- Snippets should be **exact copies from the real codebase** — never simplified or modified
