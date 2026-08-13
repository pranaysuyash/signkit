# Per-Pane Contextual Controls Proposal

## Problem

Currently ALL controls are in the left sidebar, regardless of which pane (Source/Preview/Result) the user is working with. This creates confusion:

- Rotate buttons affect Source but are always visible
- Export buttons affect Result but show up before there's a result
- User can't tell at a glance which controls apply to which pane

## User Question

> "should have controls in the source, preview and output screens? what is your take?"

## Proposal: Contextual Controls Per Pane

### Current Layout

```
[Left Sidebar - 320px Fixed]          [Right Pane]
- Open & Upload                       - Source Image View
- Threshold Slider                    - Preview (small crop)
- Color Picker                        - Result Image View
VIEW:
  - Zoom In/Out
  - Fit/100%
IMAGE:
  - ↺ CCW / ↻ CW
SELECTION:
  - Mode: Select
  - Clear Selection
EXPORT & SAVE:
  - Export...
  - Copy
  - Save to Library
  - Export JSON
```

### Proposed Layout Option A: Inline Pane Controls

```
[Left Sidebar - 280px]               [Right Pane]
- Open & Upload                      ┌────────────────────────┐
- Threshold Slider                   │ SOURCE                 │
- Color Picker                       │ [View Controls Here]   │
                                     │ [Rotate Controls Here] │
                                     │ [Image Display]        │
                                     └────────────────────────┘
MY SIGNATURES:
- [Library List]                     ┌────────────────────────┐
                                     │ PREVIEW                │
                                     │ [Selection Tools]      │
                                     │ [Small Crop Display]   │
                                     └────────────────────────┘

                                     ┌────────────────────────┐
                                     │ RESULT                 │
                                     │ [Export Controls Here] │
                                     │ [Result Display]       │
                                     └────────────────────────┘
```

**Pros:**

- Crystal clear which controls affect which pane
- Controls only visible when pane has content
- Natural workflow: source → process → export
- More screen space for library in sidebar

**Cons:**

- More complex layout code (per-pane toolbars)
- Slightly less horizontal space for images
- Need to decide: mini-toolbar or full-width buttons?

### Proposed Layout Option B: Sidebar with Smart State

Keep sidebar layout but:

- **Disable/hide** irrelevant controls based on state
- **Visual grouping** with collapsible sections
- **Clear labels** like "SOURCE Controls", "RESULT Controls"

```
[Left Sidebar - 320px]              [Right Pane]
┌──────────────────────┐            [Source/Preview/Result
│ FILE                 │             as before]
│ - Open & Upload      │
└──────────────────────┘

┌──────────────────────┐
│ SOURCE Controls      │  ← Disabled if no source
│ VIEW:                │
│ - Zoom In/Out        │
│ - Fit/100%           │
│ IMAGE:               │
│ - ↺ CCW / ↻ CW       │
└──────────────────────┘

┌──────────────────────┐
│ SELECTION            │  ← Disabled if no source
│ - Mode: Select       │
│ - Color: #000000     │
│ - Threshold: [200]   │
│ - Clear Selection    │
└──────────────────────┘

┌──────────────────────┐
│ RESULT Controls      │  ← Disabled until result exists
│ - Export...          │
│ - Copy to Clipboard  │
│ - Save to Library    │
│ - Export JSON        │
└──────────────────────┘

┌──────────────────────┐
│ MY SIGNATURES        │
│ [Library List]       │
└──────────────────────┘
```

**Pros:**

- Simpler implementation (just enable/disable)
- Consistent left-sidebar pattern
- Full image width preserved
- Clear state feedback

**Cons:**

- Still some visual clutter when all enabled
- User must scan sidebar to find controls

## Recommendation: **Option B with Progressive Disclosure**

**Why:**

1. **Desktop convention**: Sidebars are standard for tools/properties
2. **Simpler code**: No per-pane toolbar widgets needed
3. **Better first-run**: User sees all available features upfront
4. **State feedback**: Disabled controls teach the workflow

**Implementation:**

- Start with all controls in sidebar (current layout ✅)
- Add **collapsible sections** with QGroupBox or custom headers
- **Disable sections** based on state:
  - "SOURCE Controls" enabled when image loaded
  - "RESULT Controls" enabled when result exists
- Add **tooltips** explaining why disabled: "Open an image first"
- Consider **colored section headers**: Blue for active, Gray for disabled

**Phase 2 Enhancement** (optional):

- Add **floating mini-toolbar** on hover over Result pane
  - Just: [Export] [Copy] [Save]
  - Quick actions without sidebar

## Decision Points for You

1. **Do you prefer Option A (per-pane inline) or Option B (smart sidebar)?**
2. **Should sections be collapsible?** (More compact when not needed)
3. **Should we add a floating toolbar for Result pane?** (Quick export)
4. **Color coding for sections?** (Blue = active, Gray = disabled)

Let me know your preference and I'll implement it!
