# Campus Split

Campus Split is a campus-focused expense-splitting and settlement web application. It is designed for a university environment where students regularly share small purchases and use a limited directory of campus vendors.

The key idea is that students can **pay a vendor directly for their own share** instead of routing every payment through the person who initiated the expense. When one student covers another student's share, Campus Split records the resulting peer-to-peer debt separately.

> **Project status:** Local university project / MVP in development. Features described below are the intended product scope; a feature should not be considered implemented until it exists in the codebase and passes its tests.

## Product goals

- Let students create individual shared expenses or expenses inside groups such as hostel rooms and friend circles.
- Support equal, custom-amount, percentage and (where practical) item-based splits.
- Maintain a campus vendor directory managed by an administra
tor.
- Let each participant pay their own share directly to the vendor using a UPI QR code or UPI Intent where supported.
- Track vendor amounts that are still unpaid separately from money one student owes another.
- Let students record full or partial repayments of peer debts.
- Keep a clear, auditable activity history.
- Run entirely on a developer's computer for demonstration and evaluation.

## What makes Campus Split different?

A conventional expense splitter often assumes that one person pays the bill and collects reimbursements from everyone else. Campus Split also supports a vendor-first flow:

1. A student creates an expense for a campus vendor.
2. The expense is divided into participant shares.
3. Each participant can pay their own share directly to the vendor.
4. If one student pays more than their own share, the amount they covered for another participant becomes a peer debt.
5. A peer repayment reduces that interpersonal debt without changing the original expense or vendor payment history.

**Vendor liabilities and peer debts are different balances and must never be combined into one ambiguous “you owe” figure.**

## Decisions for the initial version

| Area | Decision |
|---|---|
| Project name | Campus Split |
| Student identity | Demo usernames and passwords; no college email verification |
| Expense organization | Both individual expenses and groups |
| Payment experience | UPI QR and UPI Intent flows |
| Payment confirmation | Simulated/manual confirmation for the local prototype; not bank-verified |
| Vendor management | Admin-managed directory |
| Database | SQLite |
| Hosting | Localhost; no deployment requirement |
| Revenue model | None |

## Technology stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python, FastAPI | Application and HTTP routes |
| Server-rendered UI | Jinja2 | HTML templates |
| Interactive UI | HTMX and Alpine.js | Small dynamic interactions without a separate SPA |
| Styling | Tailwind CSS and project CSS | Responsive visual system |
| Database | SQLite | Local persistent storage |
| ORM | SQLAlchemy 2.x | Database models and queries |
| Migrations | Alembic | Versioned schema changes |
| Testing | Pytest | Unit and integration tests |
| Browser testing | Playwright | End-to-end UI flows |

There is no separate Node.js backend. A Node-based asset build step may be used for CSS tooling if the implementation needs it, but running the application should only require the Python backend and documented local dependencies.

## Core concepts and accounting rules

Campus Split must distinguish these concepts:

- **Expense:** The original bill or purchase, including its creator, vendor, total and participants.
- **Expense share:** The amount assigned to one participant.
- **Vendor payment:** Money a participant reports paying directly to the vendor. The local prototype may simulate confirmation, but it must not claim bank verification.
- **Payment allocation:** The portion of a payment applied to a particular expense share.
- **Peer debt:** Money one participant owes another because that other participant covered their share.
- **Settlement:** A repayment that reduces an existing peer debt.

### Example: everyone pays the vendor directly

A laundry expense is ₹210, split equally among three students:

| Participant | Share | Payment to laundry |
|---|---:|---:|
| You | ₹70 | ₹70 |
| Roommate A | ₹70 | ₹70 |
| Roommate B | ₹70 | ₹70 |

Result: the vendor has received ₹210. No student owes another student anything.

### Example: one student covers another student's share

The same ₹210 expense is created. You pay ₹140 to the laundry, allocated as ₹70 for your share and ₹70 for Roommate A's share. Roommate B pays ₹70 directly.

Result:

- Vendor outstanding for this expense: ₹0.
- Roommate A owes you ₹70.
- Roommate B owes nobody for this expense.

The peer debt must be created from the payment allocation that covered Roommate A's share; it must not be created merely because Roommate A has a ₹70 expense share.

### Non-negotiable accounting invariants

1. Store money as integer paise. Never use binary floating-point values for money.
2. The sum of an expense's shares must equal its total amount.
3. A payment allocation must not exceed the payment amount or the unpaid amount of its target share.
4. A share must not be marked vendor-paid merely because an expense was created or a payment intent/QR was generated.
5. A peer debt is created only when a participant's confirmed/reported payment actually covers another participant's share, according to the app's explicit prototype confirmation rules.
6. A participant paying their own share directly to the vendor creates no peer debt.
7. A peer settlement reduces an existing peer debt; it does not modify the original expense or vendor payment.
8. Payment confirmation, allocation, and the corresponding ledger effect must be committed atomically in one database transaction.
9. Duplicate submissions must not create duplicate payments, allocations, ledger entries or settlements. Use an idempotency key or equivalent uniqueness strategy where appropriate.
10. Preserve the history of transactions. Do not silently overwrite or delete financial events to “fix” a balance; use a reversal/correction record or a documented controlled correction path.
11. Show payment status honestly. A user-reported or simulated payment is not bank-verified payment.
12. Derive balances from persisted financial records or a carefully maintained ledger, not from client-side arithmetic.

## Intended data model

The initial relational model is expected to include:

| Model | Responsibility |
|---|---|
| `User` | Student or administrator account |
| `Group` | A room, friend circle or other expense-sharing group |
| `GroupMember` | Membership and role within a group |
| `Vendor` | Admin-managed campus vendor and UPI details |
| `Expense` | Original bill, creator, vendor and total |
| `ExpenseShare` | Each participant's responsibility for an expense |
| `Payment` | A payment attempt or reported payment to a vendor |
| `PaymentAllocation` | Amount of a payment applied to an expense share |
| `LedgerEntry` | Peer debt created when one student covers another's share |
| `Settlement` | Full or partial repayment of a peer debt |

The implementation may introduce supporting enums, audit/event records or additional join tables where needed. It must not collapse vendor liabilities and peer debts into one field.

## Main user journeys

### Student

1. Register or sign in with a demo username.
2. View the dashboard and balances.
3. Browse campus vendors.
4. Create an individual expense or create/select a group.
5. Choose the vendor, amount and participants.
6. Split equally or enter custom shares.
7. Generate a UPI Intent or QR for the relevant participant's amount.
8. Record the prototype payment status honestly.
9. View outstanding vendor amounts and peer debts separately.
10. Record a full or partial repayment of a peer debt.

### Administrator

1. Sign in with an admin account.
2. Add and edit vendors.
3. Manage vendor category, UPI ID, QR image and active status.
4. Ensure only administrators can access vendor-management routes.

## UPI prototype boundaries

The first version is a **payment-initiation and tracking demonstration**, not a payment processor.

- Store vendor UPI IDs as vendor data and validate their basic format before use.
- Generate a standards-compatible UPI payment URI with the recipient, amount and a short transaction note.
- Offer a QR representation of the same URI.
- Where supported, offer a link/button that opens a compatible UPI app through an Intent/deep link.
- Provide a clear manual/simulated confirmation path for the local demo.
- Track states such as `pending`, `reported_paid`, `confirmed_demo`, `failed` or `cancelled` as appropriate to the implementation.
- Clearly label simulated/manual confirmations in the interface and database.
- Do not scrape UPI apps, read banking notifications, collect UPI PINs, or claim that returning from a UPI app proves payment success.
- Do not build a wallet, escrow, pooled account, payment gateway, settlement rail or stored-value balance.
- Do not include real vendor UPI identifiers in a public repository. Use fictional demo values in seed data.

If real payment verification is ever considered, it must be treated as a separate future project requiring an authorised provider/bank integration and proper merchant onboarding. It is outside the scope of this local submission.

## Design direction

The UI should feel like a polished, approachable fintech product rather than a generic college administration portal.

- Warm off-white or neutral surfaces.
- Deep charcoal text with a restrained green accent.
- Clear typography and strong hierarchy.
- Subtle borders, restrained shadows and rounded surfaces.
- Responsive layouts for desktop and mobile.
- Accessible labels, focus states, contrast and keyboard interaction.
- Consistent reusable Jinja2 components.
- Use meaningful empty, loading, validation, success and error states.

Avoid decorative complexity that makes the core expense and payment flows harder to understand.

## Local development

The commands below define the intended developer workflow. If the implementation uses different module paths, update this section and keep the commands consistent with the actual repository.

### Requirements

- Python 3.11 or newer (use the version pinned or documented by the project).
- Git.
- A modern browser.
- Optional: Node.js only if the chosen frontend asset pipeline requires it.

### Windows PowerShell

```powershell
# Clone the repository, then enter it
cd campus-split

# Create and activate a virtual environment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create local environment configuration
Copy-Item .env.example .env

# Apply database migrations
alembic upgrade head

# Seed local demo users and fictional vendors
python -m app.seed

# Start the development server
uvicorn app.main:app --reload
```

Open the local URL printed by Uvicorn (expected default: `http://127.0.0.1:8000`).

### macOS / Linux

```bash
cd campus-split
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Tests

```bash
pytest -q
```

Browser tests may require a one-time Playwright browser installation:

```bash
python -m playwright install chromium
```

Then run the browser test suite using the command documented by the implementation (for example, `pytest tests/e2e -q`).

### Demo accounts

The seed process (`python -m app.seed`) populates one administrator account and three demonstration student accounts with fictional, local-only credentials:

| Username | Password | Role | Description |
|---|---|---|---|
| `admin` | `admin123` | Administrator | Can manage, add, edit, and activate/deactivate campus vendors |
| `aarav` | `student123` | Student | Campus student account for expense splitting and directory browsing |
| `diya` | `student123` | Student | Campus student account |
| `rohan` | `student123` | Student | Campus student account |

*Note: Demo login page also includes one-click autofill buttons for these demonstration accounts for streamlined local evaluation.*
***Never reuse demo credentials outside localhost or commit real credentials/secrets.***

## Repository structure

The intended layout is:

```text
campus-split/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── templates/
│   ├── static/
│   └── seed.py
├── migrations/
├── tests/
├── .env.example
├── .gitignore
├── AGENTS.md
├── README.md
├── requirements.txt
└── alembic.ini
```

The exact structure may evolve, but keep routing, persistence, business rules and presentation separated.

## Development workflow

Work in small, reviewable phases:

1. Foundation, authentication and admin vendor directory.
2. Groups, expenses and share allocation.
3. Payment allocations and peer ledger.
4. UPI Intent/QR initiation and simulated confirmation.
5. Dashboard, activity, balances and UI polish.
6. Automated testing, documentation and submission cleanup.

Do not start a later phase until the current phase's acceptance criteria and tests pass. Read [`AGENTS.md`](AGENTS.md) before making changes.

## Security and privacy basics

Although this is a local academic project:

- Hash passwords using a modern password-hashing library; never store plaintext passwords.
- Keep secrets in `.env`, not source code.
- Commit `.env.example`, never `.env`.
- Use secure, appropriately configured session cookies and CSRF protection for state-changing browser forms.
- Validate and authorize every server-side action; hiding a button is not access control.
- Restrict admin routes on the backend.
- Avoid collecting unnecessary personal data.
- Do not store raw UPI PINs, banking credentials or payment-app secrets.
- Use fictional student and vendor data in screenshots, seed scripts and demonstrations.

## License

No license has been selected yet. Add one only when the project owners decide how the code may be reused.
