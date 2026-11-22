---
name: Campus Split
colors:
  surface: '#FFFFFF'
  surface-dim: '#d9dad6'
  surface-bright: '#f9faf5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4ef'
  surface-container: '#edeee9'
  surface-container-high: '#e7e9e4'
  surface-container-highest: '#e2e3de'
  on-surface: '#1a1c19'
  on-surface-variant: '#3f4943'
  inverse-surface: '#2e312e'
  inverse-on-surface: '#f0f1ec'
  outline: '#6f7a72'
  outline-variant: '#bec9c1'
  surface-tint: '#176b4b'
  primary: '#005136'
  on-primary: '#ffffff'
  primary-container: '#176b4b'
  on-primary-container: '#9ae9c0'
  inverse-primary: '#88d6af'
  secondary: '#55615a'
  on-secondary: '#ffffff'
  secondary-container: '#d9e6dc'
  on-secondary-container: '#5b675f'
  tertiary: '#3f4c00'
  on-tertiary: '#ffffff'
  tertiary-container: '#556500'
  on-tertiary-container: '#cce36c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a4f3ca'
  primary-fixed-dim: '#88d6af'
  on-primary-fixed: '#002114'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#d9e6dc'
  secondary-fixed-dim: '#bdcac0'
  on-secondary-fixed: '#131e18'
  on-secondary-fixed-variant: '#3e4942'
  tertiary-fixed: '#d6ed75'
  tertiary-fixed-dim: '#bad15c'
  on-tertiary-fixed: '#181e00'
  on-tertiary-fixed-variant: '#3f4c00'
  background: '#f9faf5'
  on-background: '#1a1c19'
  surface-variant: '#e2e3de'
  canvas: '#F5F6F1'
  surface-muted: '#EEF1EA'
  surface-raised: '#FAFBF8'
  ink: '#1B2821'
  ink-muted: '#68746C'
  ink-subtle: '#879188'
  line: '#DDE3DB'
  brand: '#176B4B'
  brand-hover: '#12573D'
  brand-soft: '#E7F1EA'
  accent: '#D6ED75'
  success: '#24784E'
  success-soft: '#E8F4EC'
  warning: '#9A5B13'
  warning-soft: '#FFF3DE'
  danger: '#B43F3F'
  danger-soft: '#FCECEC'
  info: '#356B91'
  info-soft: '#EAF2F8'
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-md-strong:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  body-sm-strong:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  financial-amount-lg:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  financial-amount-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 2.5rem
  space-3xl: 3rem
---

## Brand & Style

This design system embodies a warm, precise campus fintech utility. It serves collegiate communities, roommates, and student organizations who require uncompromising mathematical accuracy delivered through an approachable, low-stress operational substrate. The visual identity avoids both the cold, sterile tropes of corporate commercial banking and the superficial, gamified aesthetics of consumer micro-apps.

The design movement is **Utilitarian Modernism with Warm Minimalist Discipline**. Clarity precedes ornamentation. The UI establishes institutional trust through disciplined layout alignment, deliberate white-space management, and strict contrast ratios, while grounding the user experience in organic, warm neutral surfaces and natural deep evergreen tones. Visual noise—such as decorative gradients, glassmorphism, floating drop-shadow layers, and emoji icons—is strictly forbidden. Every pixel and line serves an explicit financial workflow purpose: organizing liabilities, parsing group expenditures, and settling balances with zero ambiguity.

## Colors

The palette operates exclusively within a disciplined, WCAG AA-compliant light mode structure. Contrast relies on tonal differentiation across warm off-white and evergreen scales rather than stark optical blacks.

### Color Roles & Guidelines
- **Primary Canvas & Surfaces:** The foundational app background is `canvas` (`#F5F6F1`). Primary data containers, forms, and cards rest on pure white `surface` (`#FFFFFF`). `surface-muted` (`#EEF1EA`) designates passive utility containers or selected navigation items, while `surface-raised` (`#FAFBF8`) supports secondary grouped cards and nested forms.
- **Typography & Content:** All core headings and high-priority amounts utilize `ink` (`#1B2821`), a deep forest-tinged black. Supporting text and input field labels map to `ink-muted` (`#68746C`), providing a 4.5:1 minimum contrast. Metadata, timestamps, and secondary captions use `ink-subtle` (`#879188`).
- **Brand Actions:** `brand` (`#176B4B`) commands all primary actions, active navigational states, and links, darkening to `brand-hover` (`#12573D`) on interactive states. `brand-soft` (`#E7F1EA`) provides a low-intensity green tint for active item badges and subtle state highlights.
- **Accent Highlight:** `accent` (`#D6ED75`) is a sharp citrus yellow-green used with high restraint. It is restricted to tiny badges, status pills, or key financial notification indicators. Text rendered atop `accent` must always be `ink` (`#1B2821`); it must never be used with white or light text.
- **Semantic Financial States:** The interface enforces a strict separation of liability models:
  - `success` (`#24784E`) & `success-soft` (`#E8F4EC`): Completed payments, settled peer balances, and balanced group sheets.
  - `warning` (`#9A5B13`) & `warning-soft` (`#FFF3DE`): Pending approvals and vendor balance thresholds nearing due dates.
  - `danger` (`#B43F3F`) & `danger-soft` (`#FCECEC`): Overdue vendor liabilities, failed payouts, and critical settlement disputes.
  - `info` (`#356B91`) & `info-soft` (`#EAF2F8`): Transaction logs, contextual campus notices, and receipt parsing progress.

## Typography

The type system is powered entirely by Geist, selected for its precise geometric structure, clean legibility at compact scales, and neutral character. It eliminates typographic fragmentation across marketing and utility contexts.

### Execution Directives
- **Tabular Numerals Enforced:** All numerical displays, currency values (`₹`), timestamps, transaction tallies, and percentage breakdowns must declare `font-variant-numeric: tabular-nums`. This prevents horizontal jitter and misalignments across accounting grids and running totals.
- **Type Hierarchy Discipline:** Italics and weights above 600 (Semi-bold) are forbidden. Weights are restricted strictly to 400 (Regular), 500 (Medium), and 600 (Semi-bold).
- **Financial Balances:** Primary ledger summaries use `financial-amount-lg` on desktop and scale to `financial-amount-md` on compact screens. Currency symbols share the weight and color of their companion figures but must sit baseline-aligned.

## Layout & Spacing

The spatial architecture is derived from an unwavering 4px base modular scale, organized around the canonical target viewport of 1440px × 900px.

### Structural Frame Architecture
- **Desktop (1024px and above):** 
  - A fixed, persistent left navigation sidebar fixed at 240px width spanning full viewport height.
  - A persistent top utility header constrained to 64px height.
  - Main operational stage utilizes a fluid 12-column grid constrained to a maximum content width of 1280px, inset with a 32px (`space-xl`) outer canvas margin and 24px (`space-lg`) column gutters.
- **Tablet (768px – 1023px):** 
  - Sidebar collapses into an edge-docked slim rail (64px) or off-canvas modal drawer.
  - Outer stage padding scales to 24px (`margin-tablet`), gutters compress to 16px (`gutter`).
- **Mobile (360px – 767px):** 
  - The desktop sidebar is removed and replaced by a compact 56px top brand bar and an ergonomic 64px fixed bottom navigation sheet.
  - Outer margins reduce to 16px (`margin`), gutters align to 16px (`gutter`). Multi-column card arrangements reflow into single-column vertical stacks.

### Spacing Application Rules
- `space-xs` (4px): Used exclusively for inline metadata spacing, badge internal padding, and tight label-to-input gaps.
- `space-sm` (8px): Icon-to-text gaps inside controls and micro item-spacing inside list rows.
- `space-md` (16px): Internal padding for cards, standard table cell padding, and grid gaps between secondary inputs.
- `space-lg` (24px): Primary stack separation between form modules, financial ledger groups, and dashboard widget rows.
- `space-xl` (32px): Structural canvas padding and major section division.

## Elevation & Depth

Visual hierarchy and spatial separation are communicated through a **Surface Tonal Layering** system bolstered by crisp 1px structural outlines. Atmospheric drop shadows, heavy colored blurs, and glassmorphism are absent.

### Layering Architecture
- **Layer 0 (Canvas Base):** Rendered in `#F5F6F1`. The foundational canvas across all screens.
- **Layer 1 (Subordinate Containers):** Rendered in `surface-muted` (`#EEF1EA`). Defines neutral grouped containers, inactive sidebar panels, or recessed receipt review blocks.
- **Layer 2 (Primary Interactive Work Surfaces):** Rendered in `surface` (`#FFFFFF`). Houses primary cards, data tables, bill splitters, and actionable ledgers. Every Layer 2 element must carry a continuous 1px solid border using `line` (`#DDE3DB`).
- **Layer 3 (Floating Controls & Popovers):** Dropdown menus, calendar pickers, and tooltips utilize pure white surfaces framed by `line` borders and a single, restrained ambient shadow: `box-shadow: 0 4px 16px rgba(27, 40, 33, 0.06)`.
- **Layer 4 (Modals & Settlement Confirmations):** Modal sheets and settlement confirmation dialogs rest atop a solid 32% opacity overlay of `ink` (`rgba(27, 40, 33, 0.32)`). Modals utilize an elevated box shadow: `box-shadow: 0 12px 32px rgba(27, 40, 33, 0.12)`, anchored by a 1px `line` border.

## Shapes

The design system applies a disciplined, functional curvature strategy that softens financial utility without drifting into toy-like roundness.

### Curvature Assignments
- **Compact Interactive Nodes (8px / `rounded-md`):** Status pills, table badges, inline chip tags, and secondary numeric markers.
- **Standard Controls (10px):** Form input fields, dropdown select triggers, primary call-to-action buttons, and segmented control tabs.
- **Primary Cards & Containers (14px–16px / `rounded-lg` to `rounded-xl`):** Ledger cards, vendor balance wrappers, dashboard overview panels, and sheet wrappers.
- **Structural Dialogs (20px / `rounded-2xl`):** Center-anchored confirmation modals, transaction split sheets, and mobile bottom drawers.

### Border Syntax
All borders are uniform 1px solid lines using `line` (`#DDE3DB`). Partial, dashed, or thick structural borders are prohibited. Visual boundaries between adjacent modules must rely either on this 1px stroke or contrasting surface color fills (`surface` adjacent to `surface-muted`).

## Components

### Buttons & Interactive Controls
- **Primary Action:** Solid background of `brand` (`#176B4B`), pure white typography (`#FFFFFF`), `10px` border radius, padding: `10px 16px`. Hover transitions to `brand-hover` (`#12573D`). Active/press state triggers `transform: scale(0.97)` over `140ms ease-out`.
- **Secondary / Outline Action:** Background of `surface` (`#FFFFFF`), 1px solid `line` (`#DDE3DB`), text in `ink` (`#1B2821`). Hover fills to `surface-muted` (`#EEF1EA`).
- **Subtle / Ghost Action:** Transparent background, `ink` text. Hover fills to `brand-soft` (`#E7F1EA`) with `brand` text color.
- **Destructive Action:** Solid background of `danger` (`#B43F3F`) or outline variant with `danger` border and text.

### Form Inputs & Select Fields
- Height: 40px standard (32px for dense ledger rows). Background: `surface` (`#FFFFFF`). Border: 1px solid `line` (`#DDE3DB`). Border radius: `10px`. Internal padding: `8px 12px`.
- **Focus State:** 1px border switch to `brand` (`#176B4B`) paired with a 2px outer ring in `brand-soft` (`#E7F1EA`). No generic blue outlines.
- **Input Metadata & Labels:** Positioned above inputs in `body-sm-strong` using `ink-muted`. Error feedback renders below in `body-sm` using `danger` (`#B43F3F`).

### Cards & Ledger Containers
- Background: `surface` (`#FFFFFF`), perimeter border: 1px solid `line` (`#DDE3DB`), radius: `14px`. Padding: 16px–24px.
- **Vendor Balance vs. Peer Liability Distinction:** 
  - *Vendor Liabilities (Canteen, Campus Stores, Labs):* Styled with a distinct `surface-raised` background header and formal invoice metadata labels.
  - *Peer Balances (Roommate splits, Group dining):* Clean inline lists utilizing avatar initials, split share percentages, and one-click quick-settle secondary buttons.

### Chips & Status Badges
- Height: 24px. Internal padding: `2px 8px`. Border radius: `8px`. Font: `label-sm`.
- **Status Configurations:**
  - *Success / Settled:* Background `success-soft` (`#E8F4EC`), text `success` (`#24784E`).
  - *Pending / Processing:* Background `warning-soft` (`#FFF3DE`), text `warning` (`#9A5B13`).
  - *Overdue / Owed:* Background `danger-soft` (`#FCECEC`), text `danger` (`#B43F3F`).
  - *Citrus Accent Tag:* Background `accent` (`#D6ED75`), text `ink` (`#1B2821`). Used exclusively for immediate spotlight items (e.g., "Settlement Due Today").

### Lists & Financial Tables
- Rows use horizontal single-line dividers in `line` (`#DDE3DB`). Alternating zebra rows are prohibited; contrast is maintained via hover fill to `surface-raised` (`#FAFBF8`).
- Numeric monetary columns must align right, with monospace/tabular numbers enabled (`font-variant-numeric: tabular-nums`). Category icons sit left within a 32px circular or 8px rounded square tinted in `surface-muted`.

### Iconography
- Strictly Lucide outline icons. Line stroke: consistent 1.75px–2px. Sizing: 16px (metadata), 20px (inputs, buttons), 24px (primary navigation). Never use emojis or multicolored solid fills as interface icons.