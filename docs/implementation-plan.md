# Implementation Plan – Front‑end Architecture (Stitch)

**Purpose** – Translate the Stitch HTML prototypes into a maintainable, component‑based UI for Campus Split while preserving the visual language defined in `design.md` and the design‑system tokens baked into each `code.html`.

---

## 1. High‑level component hierarchy

```
App
├─ Layout
│   ├─ DesktopShell
│   │   ├─ Sidebar (persistent left navigation)
│   │   ├─ TopBar (page title + optional actions)
│   │   └─ MainContent (router outlet)
│   └─ MobileShell
│       ├─ TopBar (compact title & actions)
│       ├─ BottomNav (Home, Expenses, Groups, Balances)
│       └─ MainContent
├─ Pages (Jinja templates)
│   ├─ overview_dashboard.html
│   ├─ balances.html
│   ├─ vendors_directory.html
│   ├─ admin_manage_vendors.html
│   ├─ create_expense_multi_step_flow.html
│   ├─ expense_detail.html   (missing – see §4)
│   ├─ vendor_detail.html    (missing – see §4)
│   ├─ upi_payment_sheet.html (mobile & QR/Intent variants)
│   └─ settlement_sheet.html (missing – see §4)
└─ Reusable UI components (Jinja macros / partials)
    ├─ Card
    │   ├─ MetricCard (summary numbers)
    │   └─ SummaryCard (peer‑receivable / payable / vendor‑liabilities)
    ├─ Table / TableRow
    │   ├─ VendorRow
    │   ├─ TransactionRow
    │   └─ PeerDebtRow
    ├─ Button (primary, secondary, icon‑only)
    ├─ Badge (status, count)
    ├─ Dialog / Drawer / BottomSheet
    ├─ FormField (input, textarea, select)
    ├─ FilterPill (category, status)
    ├─ SearchBar
    ├─ Avatar / InitialsBadge
    └─ Icon (Lucide – unified wrapper)
```

### 1.1 Layout components
* **DesktopShell** – matches the `aside` element found in every prototype (fixed 60 px width, dark border, navigation list). Contains a *Sidebar* macro that receives the navigation items (path, label, icon) and handles the `data‑active‑classes` logic.
* **MobileShell** – for the `*_mobile_companion` screens. Uses a top bar with a hamburger/menu button, a centered title and a right‑hand action area. Bottom navigation mirrors the four primary destinations (`Home`, `Expenses`, `Groups`, `Balances`).
* **Header** – the gray top bar inside `pl‑60` (`fixed top‑0 …`). Holds the page breadcrumb / title and optional CTA buttons (Export CSV, Add New Vendor, etc.).
* **MainContent** – a simple `<main>` wrapper (`bg‑canvas min‑h‑screen pt‑16 px‑margin‑desktop`). All page templates slot into this.

### 1.2 Page skeletons
Every page will follow the same pattern:
```jinja
{% extends "layout/base.html" %}
{% block content %}
  {{ header(page_title, actions) }}
  <section class="...">{{ body }}</section>
{% endblock %}
```
The header macro takes the **title** and an **actions list** (button configs).

---

## 2. Reusable UI elements (identified from prototypes)
| Element | Typical markup (Tailwind) | Where used |
|---|---|---|
| **Sidebar navigation link** | `<a class="{{ active ? activeClasses : inactiveClasses }}" data‑path="{{name}}">…</a>` | `admin_manage_vendors`, `balances`, `vendors_directory` etc. |
| **Metric/summary card** | `<div class="bg‑surface rounded‑xl p‑space‑lg shadow‑sm flex …">…</div>` | Overview dashboard – Total Registered, Active Outlets, etc. |
| **Summary card (financial)** | `bg‑surface rounded‑xl p‑space‑lg` with top‑border colour (`bg‑success`, `bg‑danger`, `bg‑warning`) | Balances page – Peer receivable/payable, Vendor liabilities |
| **Table** | `<table class="w‑full text‑left border‑collapse">…</table>` | Vendor registry, expense tables |
| **Table row** | `<tr class="vendor‑row hover:bg‑surface‑raised …">` | Vendor registry rows |
| **Badge / status pill** | `<span class="inline‑flex … bg‑success‑soft text‑success">Active</span>` | Vendor status column, activity tags |
| **Button** | Primary: `bg‑brand text‑on‑primary hover:bg‑brand‑hover`; Secondary: `bg‑surface border‑line hover:bg‑surface‑muted` | Export CSV, Add New Vendor, dialogs |
| **Icon button** | `<button class="p‑space‑xs rounded‑lg hover:bg‑surface‑muted"><span class="material‑symbols‑outlined …">logout</span></button>` |
| **Dialog / Drawer** | Hidden `<div id="new‑vendor‑drawer" class="fixed inset‑0 …">` – triggered by `openDrawer('new')` in prototypes |
| **Bottom sheet (mobile)** | `<div class="fixed inset‑x‑0 bottom‑0 …">` – used in `upi_payment_sheet_mobile_companion` |
| **Form field** | `<input class="w‑full pl‑9 …">` with surrounding `<div class="relative flex‑1 max‑w‑md">` – search & filters |
| **Filter pill** | `<button class="category‑pill …">All [8]</button>` – category filter bar |
| **Search bar** | `<input class="w‑full pl‑9 …" placeholder="Search…">` – vendor search |
| **Avatar / initials** | `<div class="w‑9 h‑9 rounded‑full bg‑primary flex …">` – user avatar |

All these components will be extracted into Jinja macro files under `templates/components/` (e.g. `_button.html`, `_card.html`).  The macros receive parameters (label, icon, variant, size, click handler) to keep templates DRY.

---

## 3. Design‑token extraction & Tailwind theme
The `code.html` files embed a **runtime Tailwind config** (see line 4 of each file).  We will move that config into a **static `tailwind.config.js`** at the project root so it is shared across the whole app.

### 3.1 Tokens to extract
* **Colors** – all entries under `extend.colors` match the token table in `design.md`.  They become the canonical source for Tailwind classes (`bg‑brand`, `text‑ink‑muted`, `border‑line`, etc.).
* **Spacing** – values such as `space‑lg`, `space‑md`, `margin‑desktop` map directly to Tailwind spacing utilities (`p‑4`, `mx‑4`, etc.).  We'll rename them to Tailwind default scale where possible (`4`, `8`, `12`, `16`, `24`, `32`).  Custom names (`margin‑desktop`) become **custom utilities** via `extend.spacing`.
* **Border radius** – already aligned with Tailwind defaults (`rounded`, `rounded‑lg`, `rounded‑xl`).  Keep the custom sizes (`lg:0.5rem`, `xl:0.75rem`).
* **Typography** – `fontFamily` and `fontSize` tables map to the design token table.  We'll add a **custom font family** (`'Geist', system‑ui`) and expose utility classes (`font‑headline‑lg`, `font‑body‑md`, etc.) via `extend.fontSize` and `extend.fontFamily`.

### 3.2 Example `tailwind.config.js`
```js
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.html", "./templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        canvas: "#F5F6F1",
        surface: "#FFFFFF",
        "surface-muted": "#EEF1EA",
        "surface-raised": "#FAFBF8",
        ink: "#1B2821",
        "ink-muted": "#68746C",
        "ink-subtle": "#879188",
        line: "#DDE3DB",
        brand: "#176B4B",
        "brand-hover": "#12573D",
        "brand-soft": "#E7F1EA",
        accent: "#D6ED75",
        success: "#24784E",
        "success-soft": "#E8F4EC",
        warning: "#9A5B13",
        "warning-soft": "#FFF3DE",
        danger: "#B43F3F",
        "danger-soft": "#FCECEC",
        info: "#356B91",
        "info-soft": "#EAF2F8",
        // … other colors copied from the prototype
      },
      spacing: {
        "space-xs": "0.25rem",
        "space-sm": "0.5rem",
        "space-md": "1rem",
        "space-lg": "1.5rem",
        "space-xl": "2rem",
        "space-2xl": "2.5rem",
        "space-3xl": "3rem",
        "margin-desktop": "2rem",
        "margin-tablet": "1.5rem",
        // keep any bespoke names used in HTML
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px",
      },
      fontFamily: {
        geist: ["Geist", "sans-serif"],
      },
      fontSize: {
        "headline-lg": ["30px", { lineHeight: "36px", letterSpacing: "-0.02em", fontWeight: "600" }],
        "headline-md": ["20px", { lineHeight: "28px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "headline-sm": ["16px", { lineHeight: "24px", fontWeight: "600" }],
        "body-lg": ["16px", { lineHeight: "24px" }],
        "body-md": ["14px", { lineHeight: "20px" }],
        "body-sm": ["12px", { lineHeight: "16px" }],
        "label-md": ["14px", { lineHeight: "20px", letterSpacing: "0.01em", fontWeight: "600" }],
        // … other sizes as defined
      },
    },
  },
  plugins: [],
};
```
Running `npm run build:css` (via the optional asset pipeline) will generate a single `static/css/tailwind.css` that the Jinja templates can include.

---

## 4. Screens not represented in the Stitch export (gaps)
| Missing screen | Expected purpose | Where it should live (new folder) |
|---|---|---|
| **Group management** (list, create, edit) | Allows students to create / edit roommate / friend groups. | `design-reference/stitch/groups` (future) |
| **Expense detail view** | Shows a single expense, its shares, payment status, and actions (add payment, edit share). | `design-reference/stitch/expense_detail` |
| **Create expense – step 2 (share allocation)** | The multi‑step flow currently only has a single prototype; a second step for allocating custom amounts / percentages is required. | `design-reference/stitch/create_expense_multi_step_flow` (extend) |
| **Vendor detail – edit mode** (currently only a read‑only view) | Admins need a modal/drawer to edit vendor fields. | `design-reference/stitch/vendor_detail_*` (add edit variant) |
| **Peer settlement workflow** | A dedicated page/dialog for recording peer repayments (full/partial). | `design-reference/stitch/settlement_sheet` |
| **Payment‑pending list** | Shows pending UPI intents / QR scans, with manual “Mark as paid” actions. | `design-reference/stitch/payments_pending` |
| **Analytics / empty‑state dashboards** | Screens for when there are no expenses, no vendors, etc. | `design-reference/stitch/empty_state_*` |

These gaps should be added during later phases (Phase 2+).  The component library prepared now will make their implementation straightforward.

---

## 5. Implementation steps (Phase 1 – front‑end foundation)
1. **Create Tailwind config** (`tailwind.config.js`) using the token tables from the prototypes.
2. **Add build script** in `package.json` (e.g., `"build:css": "tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --watch"`).  This satisfies the optional Node.js asset pipeline mentioned in the tech constraints.
3. **Add layout templates**:
   * `templates/layout/base.html` – loads Tailwind CSS, defines `<body>` with `{% block content %}`.
   * `templates/components/_sidebar.html`, `_topbar.html`, `_bottomnav.html`.
4. **Extract reusable macros** (buttons, cards, table rows, badges, dialogs) into `templates/components/`.
5. **Create page shells** for the existing screens (admin_manage_vendors, balances, vendors_directory, overview_dashboard, upi_payment_sheet variants). Each page imports the layout and component macros and reproduces the prototype structure using data‑driven loops.
6. **Wire navigation logic** – a small Alpine.js helper (`window.navigate(path)`) that updates the active classes; this mirrors the inline script found in the prototypes.
7. **Add placeholder data JSON** for the server side to feed the Jinja tables (e.g., `vendors.json`).  This satisfies the “hard‑coded data” requirement while keeping the UI decoupled from backend logic.
8. **Update README** – document the new Tailwind build step, how to run the dev server, and the component library location.
9. **Write tests** – using Playwright, verify that the sidebar navigation works, that the metric cards appear, and that the vendor table renders the correct number of rows.  These tests fall under the existing `tests/` suite.

---

## 6. Known limitations
* The current prototypes contain **inline scripts** for active‑state handling.  In production we will replace them with a tiny Alpine.js store (`$store.nav`) that updates on route change.
* Some screens (group management, settlement workflow) are not yet available – they will be added in later phases.
* The design system currently mixes custom utility names (`space‑lg`, `margin‑desktop`).  The Tailwind config will keep these names for backward compatibility, but developers are encouraged to use the standard Tailwind spacing scale where possible.
* The QR/Intent payment sheets are mobile‑only; a responsive fallback for desktop will be added once the payment flow is implemented (Phase 4).

---

**Next steps** – run `npm install && npm run build:css`, then start the FastAPI dev server (`uvicorn app.main:app --reload`).  The UI should now render using the shared layout and component macros, with a clean separation between markup and business logic.
