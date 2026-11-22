# Campus Split — Product UI Design Specification

**Document:** `design.md`  
**Version:** 1.0  
**Status:** Initial design direction for Stitch → local implementation  
**Product:** Campus Split  
**Target:** Desktop-first responsive web application, running on localhost

---

## 1. Product intent

Campus Split helps students manage shared campus expenses without making one person collect everybody's money. A student can create an expense, split it between friends or a group, and let each participant pay the campus vendor directly through UPI. When one student pays another person's share, Campus Split records the resulting peer-to-peer debt and helps them settle it later.

The interface must make one distinction unmistakable:

- **Vendor payment due:** a student's share has not yet been paid to the original vendor.
- **Peer balance:** one student owes another student because that person covered their share.

These are separate financial concepts and must never be visually merged into one ambiguous “you owe” number.

### Product promise

**Split the expense. Pay the right person. Keep every balance clear.**

### Primary user groups

- **Student:** creates expenses, joins groups, pays vendors, tracks peer balances and settles debts.
- **Administrator:** manages the campus vendor directory and vendor UPI details.

The first version uses demo usernames and seeded demo accounts. Campus Split is a university project for local demonstration, not a commercial financial product.

### Product principles

1. **Clarity before cleverness.** Make who owes whom, and to whom, obvious at a glance.
2. **Vendor-first splitting.** Direct vendor payment is a first-class flow, not a hidden variation of reimbursement.
3. **Trust through explicit states.** Never imply that a UPI payment is verified when it is only self-reported or simulated.
4. **Fast repeat use.** Common actions should take a few deliberate steps, not a long form.
5. **Consistent visual language.** All screens reuse the same tokens, components, states and content tone.
6. **Useful without decoration.** Avoid charts, gradients, illustrations or motion that do not improve a task.

---

## 2. Visual direction

### Direction: warm, precise campus fintech

Create a polished fintech utility with the clarity of a good finance dashboard and the warmth of a student-focused campus tool. The product should feel contemporary and thoughtfully designed, not like a bank portal, college ERP, generic SaaS admin template or a clone of Splitwise.

Use a warm neutral canvas, dark evergreen typography, restrained forest-green actions and a small citrus accent. Let layout, typography, whitespace and meaningful status color create the visual identity.

**Visual keywords:** calm, precise, warm, compact, confident, legible, friendly, composed.

**Do:**
- Use a warm off-white page background and white or near-white content surfaces.
- Use dark evergreen for primary text and a restrained forest green for primary actions.
- Use a soft yellow-green accent only for small highlights, selected states or a single point of emphasis.
- Use clean, thin borders and subtle surface contrast instead of heavy drop shadows.
- Use a purposeful geometric Campus Split mark, not a letter inside a rounded square.
- Use consistent line icons from one icon family, preferably Lucide.

**Do not:**
- Use generic purple/blue gradients, gradient text, glassmorphism or glowing blobs.
- Use emoji as interface icons.
- Put every piece of information inside a separate floating card.
- Use giant dashboard numbers without context.
- Use decorative charts that do not answer a real question.
- Use random stock photos, generic people illustrations or fake testimonials.
- Use a generic “AI-generated SaaS dashboard” composition.

### Brand mark

Create a compact abstract symbol from two offset rounded receipt/slip shapes or two interlocking halves. It should suggest splitting and settling without depicting currency, coins or a wallet. Pair it with the wordmark **Campus Split**. The mark must work in monochrome and at 16–24 px.

### Reference strategy

Use references for *qualities*, not copies:
- Consumer fintech: clear financial hierarchy, strong number formatting, trustworthy payment states.
- Modern productivity tools: restrained navigation, consistent spacing and calm information density.
- Campus utility: approachable language, quick repeat actions and low cognitive load.

Do not reproduce another product's exact layout, brand, iconography or copy. Keep a small reference board or notes file when real reference screenshots are supplied. Extract actual colors and proportions from those screenshots rather than relying only on a verbal description.

---

## 3. Design tokens

Treat these as the single source of truth. If Stitch suggests alternatives, reconcile them here before implementation. Do not invent one-off values screen by screen.

### Color tokens

| Token | Hex | Usage |
|---|---:|---|
| `canvas` | `#F5F6F1` | Main application background |
| `surface` | `#FFFFFF` | Main cards, sheets, forms and menus |
| `surface-muted` | `#EEF1EA` | Quiet panels, selected navigation background |
| `surface-raised` | `#FAFBF8` | Secondary surface or nested content |
| `ink` | `#1B2821` | Primary text and headings |
| `ink-muted` | `#68746C` | Secondary text, labels and helper copy |
| `ink-subtle` | `#879188` | Tertiary metadata only; never for essential text |
| `line` | `#DDE3DB` | Borders and dividers |
| `brand` | `#176B4B` | Primary action, active navigation and links |
| `brand-hover` | `#12573D` | Hover/pressed primary action |
| `brand-soft` | `#E7F1EA` | Selected states and subtle brand surfaces |
| `accent` | `#D6ED75` | Small highlight, limited use |
| `success` | `#24784E` | Completed/confirmed states |
| `success-soft` | `#E8F4EC` | Success background |
| `warning` | `#9A5B13` | Pending/awaiting states |
| `warning-soft` | `#FFF3DE` | Pending background |
| `danger` | `#B43F3F` | Failed, rejected or destructive state |
| `danger-soft` | `#FCECEC` | Error background |
| `info` | `#356B91` | Informational state |
| `info-soft` | `#EAF2F8` | Informational background |

Use dark text on the citrus accent. Do not use the accent as a body-text background unless contrast is verified. All text/background combinations must meet WCAG AA contrast: at least 4.5:1 for normal text and 3:1 for large text and meaningful UI boundaries where applicable. If a pairing fails, change the pairing rather than relying on visual judgement.

### Typography

- **Primary typeface:** Geist. Use a sans-serif fallback if it cannot be loaded locally.
- **Numeric UI:** Geist with tabular numerals (`font-variant-numeric: tabular-nums`).
- **Do not mix multiple display fonts.**
- Avoid italics and ultra-heavy 900 weights.
- Use balanced headings and readable body line lengths.

| Style | Size / line-height | Weight | Usage |
|---|---|---|---|
| Page title | 30 / 36 px | 600 | Primary page heading |
| Section title | 20 / 28 px | 600 | Main section heading |
| Card title | 16 / 24 px | 600 | Card and panel heading |
| Body | 14 / 20 px | 400 | Main supporting text |
| Body strong | 14 / 20 px | 500–600 | Row names and emphasized values |
| Small | 12 / 16 px | 400–500 | Metadata and timestamps |
| Button | 14 / 20 px | 600 | Button label |
| Financial amount | 24–30 / 32–36 px | 600 | Summary values, context dependent |

### Spacing scale

Use a 4 px base grid. Approved values: `4, 8, 12, 16, 24, 32, 40, 48, 64` px. Most component gaps should use 8, 12, 16 or 24 px. Page sections should use 24–32 px. Avoid arbitrary one-off spacing values.

### Radius and borders

- Small controls: 8 px.
- Inputs and standard buttons: 10 px.
- Cards and dropdowns: 14–16 px.
- Large dialogs/sheets: 20 px.
- Use a 1 px full perimeter border in `line` where separation is needed.
- Avoid partial one-sided card borders and heavy shadows.
- Use a restrained shadow only for a floating menu/dialog when elevation is necessary.

### Iconography

Use one consistent outline icon set such as Lucide. Standard sizes: 16 px for inline metadata, 18–20 px for controls, 22–24 px for navigation. Keep stroke weights consistent. Icons must reinforce a visible text label; do not make critical actions icon-only on desktop.

---

## 4. Application shell and information architecture

### Desktop shell

Target a 1440 × 900 desktop viewport first.

- Persistent left sidebar: approximately 232–248 px wide.
- Main content area: flexible, with a comfortable maximum width around 1280 px.
- Top header: approximately 64–72 px high.
- Main page padding: 32 px on wide screens; reduce to 24 px on medium screens.
- Use a 12-column content grid where it helps align panels, not as a visible grid.
- Keep the primary content column readable; avoid stretching forms and transaction rows across the full viewport.

**Sidebar order:**
1. Campus Split mark and wordmark.
2. Small campus label (configurable, e.g. “Campus workspace”).
3. Overview.
4. Expenses.
5. Groups.
6. Balances.
7. Vendors.
8. Bottom utility area: Settings and, for admins only, Admin / Manage vendors.
9. Signed-in student identity and logout affordance at the bottom.

Use a clear active navigation treatment: soft green surface, dark green icon/text and a subtle leading indicator. Do not use a large pill for every navigation item.

**Top bar:** current page context, optional breadcrumb, notification affordance only if it has a defined function, and profile control. Do not add decorative search unless a real search flow is included.

### Mobile shell

Target a 390 × 844 viewport.

- Replace the persistent sidebar with a compact top bar and bottom navigation.
- Keep four primary mobile destinations: Home, Expenses, Groups, Balances.
- Vendor discovery is reachable from a clearly visible “Pay a vendor” or “Browse vendors” action and from expense creation.
- Use full-width forms and bottom sheets where appropriate.
- Convert wide tables into stacked transaction rows/cards with the same information hierarchy.
- Keep primary actions reachable without covering content or keyboard fields.

### Navigation labels

Use simple labels: **Overview, Expenses, Groups, Balances, Vendors**. Avoid clever renamed labels that obscure meaning.

---

## 5. Screen specifications

### 5.1 Overview dashboard

**Purpose:** let a student understand their financial position and take the next action quickly.

Layout:
- Page heading: “Overview” with a short supporting line, e.g. “Your campus expenses, all in one place.”
- Primary CTA: **Split an expense**.
- Secondary action: **Pay a vendor**.
- Three clearly separate summary panels:
  1. **People owe you** — outstanding peer debt owed to the current user.
  2. **You owe people** — outstanding peer debt the current user owes to other students.
  3. **Vendor payments due** — current user's unpaid shares payable to vendors.
- Recent activity list with type, counterparty/vendor, amount, date and status.
- A compact “Your groups” panel or quick links.
- Optional small “Needs your attention” panel for overdue peer repayments or vendor shares.

Do not show a single combined “net balance” that mixes vendor liabilities with peer debt. Do not show a chart unless real seeded data creates a meaningful comparison.

Example display data for the visual mockup only:
- People owe you: ₹180.
- You owe people: ₹65.
- Vendor payments due: ₹70.
- Laundry pickup: ₹210 total, 3 participants, ₹70 pending directly to vendor.
- Dinner: ₹120 peer repayment outstanding to you.
- Print shop: ₹60 peer repayment outstanding to you.

The mock values are illustrative. The backend must later render real values from ledger and payment records.

### 5.2 Create expense — primary workflow

Design a short, clear multi-step flow. Use a stepper only if it makes the task easier; otherwise use one well-grouped page. The user should understand progress and be able to go back without losing entered data.

**Step A — Expense details**
- Vendor selector with category/icon and searchable list.
- Expense title/description.
- Total amount in rupees.
- Date (default today).
- Optional notes.

**Step B — Participants and shares**
- Select individual students or a saved group.
- Support equal split, custom amounts and percentage split.
- Show each participant's share as the amount changes.
- Validate that shares total exactly to the expense amount.
- Show an inline explanation if rounding leaves a remainder; assign remaining paise deterministically rather than silently dropping it.

**Step C — Payment arrangement**
For each participant, make the expected route explicit:
- Pay vendor directly.
- Covered by the expense creator or another participant.
- Already paid to vendor (record as reported or confirmed according to the available confirmation method).

Do not assume everyone pays the vendor directly. Mixed arrangements must be possible. Summarize the payer, recipient, share and current status before saving.

Primary CTA: **Create expense**. Secondary: **Back** or **Cancel**.

### 5.3 Expense detail

Show:
- Vendor, expense title, total amount, date and creator.
- Participants and individual shares.
- Payment status per share.
- Clear separation between amount pending to vendor and amount owed to a student.
- Payment timeline with actor, recipient, amount, timestamp and confirmation status.
- Contextual actions such as “Pay vendor”, “Record payment”, “Request repayment” or “Settle”, only when valid for the current state.

Do not show actions that would double-count a share or create a debt for an amount already paid directly to the vendor.

### 5.4 Balances

Use two visually distinct sections or tabs:

**Peer balances**
- People who owe the current user.
- People the current user owes.
- Amount per person.
- Source expense(s) and oldest relevant date.
- Partial settlement progress.
- Action: **Record settlement** or **Settle up**.

**Vendor payments**
- Vendor name.
- Expense and share amount.
- Status: Unpaid, Payment opened, Reported paid, Vendor confirmed, Failed or Cancelled.
- Action: **Pay vendor** or **View expense**.

Never combine these two lists into a single undifferentiated debt table.

### 5.5 Groups

Group list and group detail pages support roommate rooms and friend circles.

Group list:
- Group name, member avatars/initials, member count and recent activity.
- Clear create/join affordance only if those actions are implemented.

Group detail:
- Group name and members.
- Group expenses.
- Group-level summary that does not obscure individual obligations.
- CTA: **Split an expense with this group**.

Avoid turning groups into chat rooms or social feeds. Messaging is out of scope.

### 5.6 Vendors

Vendor directory:
- Search/filter by name or category.
- Simple rows or compact cards with vendor name, category, active status and clear action.
- Categories may include Laundry, Food, Stationery, Printing and Other.

Vendor detail:
- Name and category.
- UPI ID with copy affordance.
- QR code presentation when a payment amount is known.
- Recent expenses involving the vendor, where useful.
- CTA: **Pay vendor** or **Use in an expense**.

Use fictional UPI IDs and sample vendor data in the mockup. Never display real personal payment details.

### 5.7 UPI payment sheet

Provide both modes in the UI:

- **Open UPI app:** an Intent-style action that prepares the recipient, amount and note.
- **Scan QR:** show an amount-specific QR for the selected vendor and share.

For desktop, QR is the primary visual path; Intent may be shown as a secondary option. For mobile, “Open UPI app” may be primary, with QR available as an alternative.

Show recipient, UPI ID, amount and transaction note before the user leaves the app. Clearly explain that the student must complete the transaction in their UPI app.

Prototype payment states:
1. Ready to pay.
2. Payment app opened / QR displayed.
3. Student reports payment completed.
4. Awaiting vendor/admin confirmation or marked simulated.
5. Confirmed in the local demo.
6. Failed, cancelled or expired.

Use precise labels. A student tapping “I have paid” must not make the UI claim that the bank verified the transaction. Use **Reported paid** or **Awaiting confirmation** until a separate confirmation event occurs. The demo may support an admin/manual simulated confirmation.

### 5.8 Admin vendor management

Admin-only screen:
- Vendor list with active/inactive status.
- Add vendor and edit vendor form.
- Fields: name, category, description, UPI ID, optional QR image path, active status.
- Confirmation before deactivation.
- Clear success/error feedback.

Do not expose admin actions to student accounts.

### 5.9 Authentication

Keep login and registration simple and visually consistent with the app shell. Username and password only for the demo version. Do not imply official college authentication or email verification.

---

## 6. Reusable component inventory

Build reusable components rather than one-off screen elements.

- App sidebar and mobile bottom navigation.
- Page heading with optional supporting line and actions.
- Primary, secondary, ghost and destructive buttons.
- Financial summary panel with label, amount, helper text and optional trend/status (no fabricated trends).
- Status badge with icon/text and semantic color.
- Transaction row.
- Person row with fixed-size avatar/initials.
- Vendor row/card.
- Amount input with ₹ prefix and clear validation.
- Student multi-select.
- Split method selector: Equal / Custom / Percentage.
- Share allocation row with amount and status.
- Payment route selector.
- Confirmation dialog.
- Toast/inline feedback.
- Empty state with one clear next action.
- Loading skeleton for lists and summary panels.
- Error state with recovery action.
- UPI payment sheet with QR / Intent choice.

### Component behaviour

Every interactive component must have default, hover, focus-visible, pressed, disabled, loading and error states where relevant. Inputs need label, hint, invalid and success states. Avoid relying on color alone to communicate status.

---

## 7. Interaction and motion rules

Motion should communicate state changes, not decorate the dashboard.

- Typical button, hover and menu transitions: 140–220 ms.
- Use ease-out for entrances and direct manipulation. Avoid ease-in entrances.
- Animate transform and opacity rather than layout properties such as width, top or height wherever possible.
- Never use `transition: all`; list the exact properties being transitioned.
- Button pressed feedback may use a subtle scale to approximately 0.97.
- Popovers should originate visually from their trigger. Dialogs may remain centered.
- Avoid large staggered page reveals, parallax and perpetual animations.
- Respect `prefers-reduced-motion` and provide a reduced-motion experience.
- Keep number columns stable with tabular numerals.

Use motion only for:
- Opening/closing a menu, modal or bottom sheet.
- Confirming an action or state change.
- Showing a validation or success message.
- Switching between clearly related tabs/steps.

---

## 8. Content and microcopy

Tone: direct, friendly, calm and specific. Use everyday student language without sounding childish or overly corporate.

Prefer:
- “Split an expense”
- “Pay vendor”
- “People owe you”
- “You owe people”
- “Vendor payment due”
- “Reported paid”
- “Awaiting confirmation”
- “Record repayment”
- “Split with group”

Avoid:
- “Optimize your financial ecosystem”
- “Seamless payment orchestration”
- “Submit” for a meaningful action
- Vague success copy such as “Great job!” when a factual confirmation is better
- Any copy that implies payment verification when none exists

Show dates as absolute dates after they are more than a week old. Pluralize correctly (“1 member”, “3 members”). Format currency consistently in Indian rupees, e.g. `₹1,240`.

---

## 9. Responsive and accessibility requirements

- Desktop: 1440 × 900 reference canvas.
- Tablet: 768–1024 px; sidebar may collapse to an icon rail or drawer.
- Mobile: 390 × 844 reference canvas; also check 360 px width.
- No horizontal page scrolling at supported widths.
- Tables must become readable stacked rows on mobile.
- Forms must keep labels visible and controls comfortably tappable.
- Focus indicators must be visible and not removed.
- All actions must be keyboard reachable.
- Use semantic landmarks, labels and button/link elements.
- Provide text equivalents for icon-only controls and accessible names for QR/payment actions.
- Status must be communicated through text/icon as well as color.
- Respect reduced motion.
- Check contrast with a WCAG contrast tool; do not rely on visual intuition.

---

## 10. Data realism and financial UX guardrails

The visual layer must preserve the backend financial model:

- Expense shares are responsibility allocations, not proof of payment.
- Payments record who paid, how much and to whom.
- Payment allocations explain which shares a payment covers.
- Peer debt is created only when one student actually covers another student's share.
- A direct vendor payment must not create a peer debt for that same amount.
- Partial payments and partial peer settlements must be representable.
- Vendor liabilities and peer liabilities remain separate in totals, lists, labels and status treatments.
- The prototype may simulate payment confirmation, but it must label it as simulated/manual confirmation.

Use integer paise in the application data layer; the UI formats amounts as rupees. Never calculate financial truth only in browser-side state.

---

## 11. Handoff to implementation

The implementation stack is FastAPI, Jinja2, HTMX, Alpine.js, Tailwind CSS, SQLite and SQLAlchemy. The design must be implementable with server-rendered templates and small progressive enhancements. Do not design interactions that require a separate React application or a paid third-party service.

Suggested template structure:

```text
app/templates/
  base.html
  auth/
  dashboard/
  expenses/
  groups/
  balances/
  vendors/
  admin/
  components/
```

Implementation expectations:
- Define CSS custom properties for all color, spacing, radius and typography tokens.
- Map tokens into Tailwind configuration or utility classes.
- Use Jinja partials for repeated components.
- Use HTMX for server-backed form submissions, filtering and partial updates.
- Use Alpine only for small client interactions such as dropdowns, tabs and modal visibility.
- Preserve server-side validation and authorization.
- Do not hardcode mock dashboard totals into the production template; seed demo data and calculate real values through services.
- Keep financial calculations in backend services, not in templates or JavaScript.

### Design-to-code QA gate

Before calling the UI complete:
1. Compare the browser output against the approved Stitch screens at the same viewport sizes.
2. Verify typography, spacing, color, radii, navigation and component consistency.
3. Inspect every interaction state: default, hover, focus, pressed, disabled, loading, empty, error and success.
4. Check every visible action actually works or is explicitly marked as not yet implemented.
5. Check financial labels and status wording against the rules in section 10.
6. Run contrast checks and keyboard navigation checks.
7. Test desktop, tablet and mobile layouts.
8. Remove generic AI patterns: arbitrary gradients, emoji icons, decorative charts, placeholder text, dead buttons, excessive card wrappers and unneeded motion.
9. Record important keep/reject decisions in a small design decision log so later screens do not drift.

---

## 12. Design source notes

This specification adapts general methods from the following public design-skill projects; it does not reproduce their skill files verbatim:

- [emilkowalski/skills](https://github.com/emilkowalski/skills): animation judgement, restrained motion, interaction polish and practical UI details.
- [elayadesign/ai-design-skills](https://github.com/elayadesign/ai-design-skills): a defined visual system, reusable type/spacing/radius tokens, section-by-section design and consistent foundations.
- [Owl-Listener/designer-skills](https://github.com/Owl-Listener/designer-skills): user-centred UX strategy, design systems, UI design, interaction design, prototyping/testing, handoff and visual critique.
- [codeswithroh/tastemaker](https://github.com/codeswithroh/tastemaker): reference-led design, persistent project style decisions, contrast checks, app-state coverage and avoiding generic AI-generated UI patterns.

These sources informed the design workflow and QA rules. The palette, product decisions and UI specifications above are authored specifically for Campus Split.
