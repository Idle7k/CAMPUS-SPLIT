AGENTS.md — Campus Split
This file is the source of truth for all AI coding agents and human contributors working in this repository. Read it fully before inspecting, planning or editing code. Follow these rules across frontend, backend, database, testing and documentation work.
1. Product identity and purpose
Project: Campus Split

Campus Split is a campus-focused expense splitting and debt-tracking application for a university with a small, predefined set of vendors. Students can create shared expenses, pay vendors directly for their individual shares, and track amounts owed between students when someone covers another person's share.

The project is a local university submission. There is no revenue model, no production deployment requirement and no need to introduce paid infrastructure.
Core value proposition
A student should not have to collect everyone's money just because they initiated a shared purchase. Participants should be able to pay the original vendor directly. When one student covers another participant's share, that covered amount becomes a separate peer debt.
Initial product decisions
- Student identity: demo username/password accounts; no college email verification.
- Expense organization: support both individual expenses and groups.
- Groups: support use cases such as hostel rooms and friend circles.
- Payments: support UPI QR and UPI Intent initiation.
- Confirmation: simulated/manual for the local prototype; never represented as verified by a bank.
- Vendor management: administrator-managed only.
- Project name: Campus Split.
- Runtime: localhost.
- Revenue: none.
2. Non-negotiable product principles
1. Keep the product focused on shared campus expenses, vendor payments and interpersonal debt tracking.
2. Keep vendor liabilities distinct from peer-to-peer debts.
3. A participant can pay their own share directly to a vendor without creating a debt to the expense creator.
4. If one student pays for another student's share, record the covered amount as a peer debt from the share owner to the person who paid.
5. Do not make a peer debt from an expense share alone. A debt requires a payment/coverage event.
6. Preserve an understandable history of expenses, payments, allocations and settlements.
7. Make the core flows quick and straightforward. Avoid unnecessary social, marketplace, chat, AI or gamification features.
8. Do not add a revenue model, subscription, ads or payment fee.
9. The application must work locally without requiring a paid API or hosted service.
10. Never claim a feature is implemented, a payment is successful or a test passed unless it has actually been verified.
3. Technology constraints
Use the agreed stack unless a concrete technical blocker is explained and approved:
- Python
- FastAPI
- Jinja2
- HTMX
- Alpine.js
- Tailwind CSS plus project-owned CSS
- SQLite
- SQLAlchemy 2.x
- Alembic
- Pytest
- Playwright for browser-level tests
There must be no separate Node.js backend and no React/Next.js rewrite. Node.js may be used only for an optional frontend asset build toolchain if justified. Keep the local setup simple and document every required command.
4. Architecture boundaries
Keep responsibilities separated:
- Routers: HTTP concerns, parsing and response selection. Keep handlers thin.
- Services: business rules, financial operations and orchestration.
- Models: persisted entities, relationships and database constraints.
- Templates/components: presentation only; no financial calculations.
- Static assets: styling and browser interactions only.
- Tests: protect business invariants and key user journeys.
Expected service boundaries include:
- expense_service: create expenses, validate participants and shares, calculate/validate split allocations.
- payment_service: create payment attempts, record payment status, allocate payment amounts to shares and apply payment effects.
- ledger_service: calculate or record peer debts and expose balances.
- settlement_service: record full/partial peer repayments and update outstanding debts.
- vendor_service: administer and retrieve active vendors.
Avoid circular imports. Keep database transaction ownership explicit. Do not put business logic in Jinja templates or JavaScript.
5. Data model expectations
The initial domain should include these entities (supporting enums/tables are allowed where useful):
- User: demo account, password hash and role (student or admin).
- Group: named sharing group with creator/owner.
- GroupMember: user membership in a group, with uniqueness constraints.
- Vendor: name, category, description, UPI ID, optional QR image path and active status.
- Expense: creator, vendor, description, total amount in paise and timestamps/status.
- ExpenseShare: expense, participant and amount in paise.
- Payment: payer, vendor/recipient context, amount in paise, method, status, reference/idempotency key and confirmation metadata.
- PaymentAllocation: a payment and the expense share(s) it covers, with allocated amount in paise.
- LedgerEntry: a peer liability from one student (debtor) to another (creditor), linked to the expense/payment allocation that caused it where possible.
- Settlement: a repayment against an outstanding peer debt, including payer, recipient, amount, status and timestamp.
Use foreign keys, indexes, unique constraints and appropriate delete behavior. Do not cascade-delete financial history when a user, group, vendor or expense is edited or deactivated. Prefer archive/deactivate semantics for referenced records.
Money representation
- Store all amounts as integer paise (₹1 = 100 paise).
- Do not use float for money or financial comparisons.
- Convert paise to formatted rupees only at the presentation boundary.
- Validate positive amounts and prevent overflow/invalid allocations.
- Use Decimal only when a decimal representation is genuinely needed at an input/output boundary, then convert to integer paise with an explicit rounding policy.
6. Financial semantics and invariants
These rules are mandatory. Add tests for them before or alongside implementing the corresponding workflow.
6.1 Expenses and shares
- An expense has one authoritative total amount in paise.
- The sum of all its shares must equal the expense total before the expense can be finalized.
- A participant must not have duplicate shares for the same expense unless a deliberate itemized design requires it; if itemized, aggregate them deterministically.
- Equal splits must handle remainders in paise deterministically so the shares still sum exactly to the total.
- Custom amount and percentage splits must validate that the final allocations equal the total exactly.
- Only authorized participants/creators may modify an expense, and finalized financial history must not be silently rewritten.
6.2 Vendor liabilities
A vendor liability is the unpaid portion of an expense share that has not yet been covered by a recorded payment to the vendor.
- Creating an expense or generating a UPI QR/Intent does not pay the vendor.
- A pending payment attempt does not reduce an outstanding vendor balance.
- A payment allocation reduces the unpaid portion of the target share only when it reaches the prototype's defined confirmed/reported state.
- UI labels must distinguish pending, reported, simulated/confirmed and any other implemented status accurately.
6.3 Peer debts
A peer debt exists when one student has covered another student's share.

Example: a ₹210 expense has three ₹70 shares. Student A pays ₹140 to the vendor, allocated as ₹70 to A's share and ₹70 to Student B's share. Student C pays their own ₹70.

Expected result:
- The vendor outstanding for the expense is ₹0.
- Student B owes Student A ₹70.
- Student C owes no one for this expense.
The peer debt must be created from the allocation of A's vendor payment to B's share. Do not create peer debt when B pays their own share directly to the vendor.

Do not create duplicate peer debt when a payment is retried or an allocation is reprocessed. Use a database transaction and idempotency/uniqueness protection.
6.4 Settlements
- A settlement is a repayment of a peer debt, not a vendor payment.
- Support partial and full settlements.
- A settlement must not exceed the outstanding amount of the debt it reduces.
- A settlement must not alter the original expense, expense share or vendor payment.
- If the prototype lets users manually mark a repayment, label it as user-reported/simulated rather than bank-verified.
- Retain settlement history; do not overwrite the original debt event.
6.5 Atomicity and concurrency
- Payment status changes, payment allocations and resulting ledger effects must happen atomically.
- Settlement creation and debt reduction must happen atomically.
- Roll back the entire operation if any validation or database write fails.
- Protect against duplicate form submissions and repeated callbacks with idempotency keys or equivalent database constraints.
- Re-check outstanding amounts inside the transaction, not only in a prior UI request.
- Use SQLite transaction handling and constraints consistently; do not assume frontend validation prevents races or duplicate requests.
6.6 Balance presentation
Show at least these as distinct concepts:
- You owe vendors: unpaid shares assigned to the current student.
- Others owe you: outstanding peer debts where the current student is creditor.
- You owe others: outstanding peer debts where the current student is debtor.
- Vendor payments pending confirmation: payment attempts not yet recorded in the prototype's confirmed/reported state.
Do not combine these into one “net balance” without a clear breakdown. Do not silently net vendor liabilities against peer debts because they are owed to different parties.
7. UPI and payment safety boundaries
The first implementation is a local payment-initiation and tracking demo, not a payment processor.
- Store each vendor's UPI ID in the admin-managed vendor record.
- Generate a valid UPI payment URI with payee, amount and concise transaction note.
- Support both QR generation from that URI and UPI Intent/deep-link initiation where the device/browser supports it.
- The QR and Intent must represent the same recipient and amount shown in the UI.
- Use fictional UPI IDs in seed data and screenshots.
- Provide a clearly labelled manual/simulated confirmation path.
- Returning from a UPI app, opening an Intent or scanning a QR is not proof that payment succeeded.
- Never ask for, store or process a UPI PIN, banking password, OTP or other banking credential.
- Never scrape UPI apps, read banking notifications or claim to verify transactions without an authorised verification integration.
- Never create a wallet, escrow, pooled balance, stored-value account or in-app transfer rail.
- Keep payment generation and status tracking in a dedicated service so a future authorised integration can replace the prototype adapter.
- Do not use a real gateway, real merchant onboarding or production payment claims in this submission.
8. Authentication and authorization
- Initial student identity is demo username/password; do not add college email verification unless explicitly requested.
- Hash passwords using a maintained password-hashing library (for example, Argon2id or a suitable maintained password context).
- Never store plaintext passwords or commit secrets.
- Use server-side sessions with appropriately configured cookies.
- Protect state-changing browser form submissions against CSRF.
- Validate authorization on the backend for every protected operation.
- Hiding a UI control is not authorization.
- Only an admin can create, edit, activate or deactivate vendors.
- A student can only view or modify records they are authorized to access.
- Seeded demo credentials must be explicitly local-only and documented; prefer environment-configurable passwords rather than hardcoded production-like secrets.
9. Frontend and design direction
Create a polished, modern fintech-style application, not a generic admin template.

Visual direction:
- Warm off-white/neutral background.
- Deep charcoal typography.
- Restrained green accent.
- Clear type scale and spacing.
- Subtle borders and restrained shadows.
- Rounded cards and controls without excessive pill styling.
- Responsive desktop and mobile layouts.
- Consistent reusable Jinja2 components.
UX requirements:
- Make “Split an expense” a prominent, quick action.
- Make payment recipient, amount and status obvious before opening a UPI app.
- Distinguish vendor payments from peer settlements visually and textually.
- Include empty states, loading/processing feedback, validation messages and recoverable errors.
- Use semantic HTML, accessible labels, keyboard focus states and adequate contrast.
- Do not fabricate dashboard balances, activity or payment states. Use explicit empty states or clearly labelled demo seed data.
- Keep client-side JavaScript lightweight. HTMX/Alpine interactions must not become the source of truth for financial state.
10. Privacy, configuration and repository hygiene
- Keep configuration in environment variables loaded through a settings module.
- Commit .env.example; never commit .env.
- Add SQLite database files, virtual environments, caches, local uploads and secrets to .gitignore as appropriate.
- Avoid collecting unnecessary personal information.
- Use fictional campus/student/vendor data unless the project owner explicitly supplies test data.
- Validate file uploads and restrict upload types/size if vendor QR image uploads are implemented.
- Do not expose password hashes, secrets, session tokens or sensitive configuration in logs or error pages.
- Provide useful structured application logs without logging credentials or unnecessary personal data.
11. Testing standards
All financial logic must be testable independently of HTTP routes and templates.
Required backend coverage
- Share totals and rounding/remainder handling.
- Equal, custom and percentage split validation.
- Payment allocation against one or multiple shares.
- Partial vendor payments.
- Direct-to-vendor payment by each participant.
- One participant covering another participant's share.
- Correct peer debtor/creditor direction.
- Partial and full peer settlements.
- Reject over-allocation and over-settlement.
- Duplicate/idempotent payment submissions.
- Transaction rollback when ledger creation fails.
- Authorization for group, expense and admin operations.
- No peer debt from a participant paying their own share.
Testing rules
- Use isolated temporary test databases.
- Do not rely on real UPI apps, bank accounts, external APIs or network services in automated tests.
- Use deterministic test data and fixed expected amounts.
- Test service functions directly and key journeys through FastAPI's test client.
- Use Playwright for the core browser journey once the frontend is implemented.
- Never report tests as passing unless they were actually run and the output was checked.
12. Required phased workflow
Work incrementally. Complete and verify one phase before moving to the next.
Phase 1 — Foundation
- Project skeleton and configuration.
- SQLite, SQLAlchemy and Alembic.
- Initial domain models and relationships.
- Demo registration/login/logout and role authorization.
- Admin-managed vendor directory and fictional seed vendors.
- Base Jinja2 layout and a minimal dashboard shell.
- Tests for database setup, authentication, authorization and vendor management.
Do not implement expense splitting, ledger calculations, UPI generation or settlement workflows in Phase 1.
Phase 2 — Groups and expense engine
- Group creation and membership.
- Individual and group expense creation.
- Equal, custom-amount and percentage splits (item-based splits only if they fit the schedule cleanly).
- Expense share validation and display.
- Tests for all split calculations and permissions.
Do not implement peer debt creation from expense creation alone.
Phase 3 — Payment allocation and financial ledger
- Vendor payment records and payment allocations.
- Vendor outstanding calculation.
- Peer debt creation only when one participant's payment covers another participant's share.
- Clear debtor/creditor direction.
- Partial payment and allocation support.
- Settlement records and partial/full repayment.
- Idempotency, atomic database transactions and financial invariant tests.
Review the accounting rules in Section 6 before coding this phase. Do not improvise a different debt model.
Phase 4 — UPI QR and Intent prototype
- UPI URI generation.
- QR generation.
- Intent/deep-link launch where supported.
- Simulated/manual confirmation and accurate statuses.
- No live payment gateway or bank verification.
Phase 5 — Frontend completion
- Dashboard backed by real service-derived balances.
- Expense creation and detail views.
- Group views.
- Vendor directory and vendor details.
- Payment initiation/status views.
- Personal peer ledger and settlement flow.
- Activity history and responsive polish.
Phase 6 — QA and submission
- Full backend and browser regression tests.
- Fix accessibility and responsive issues.
- Verify clean local installation from README instructions.
- Complete README and demo instructions.
- Remove secrets, local databases and generated artifacts from Git.
- Ensure repository is ready for university evaluation.
13. Agent operating procedure
For every task:
1. Read this file and inspect the relevant existing code before making changes.
2. Summarize the intended changes and identify impacted modules.
3. Preserve working behavior and existing conventions unless a change is necessary.
4. Implement the smallest coherent change that completes the requested phase.
5. Add or update tests for the behavior changed.
6. Run the relevant tests, migrations, lint/type checks if configured, and application smoke checks.
7. Inspect the final diff for accidental deletions, unrelated refactors, secrets and generated files.
8. Update README/documentation when commands, setup or behavior changes.
9. Report what changed, commands run, test outcomes and known limitations honestly.
10. Stop at the requested phase. Do not autonomously begin the next phase.
Before changing the database
- Inspect current models and migrations.
- Do not edit an already-applied migration to change historical schema; create a new migration.
- Generate and inspect Alembic migrations; do not assume autogenerated migrations are correct.
- Preserve existing user and financial records.
- Test both fresh database creation and upgrade from the previous migration where feasible.
Before changing financial code
- Identify the exact invariant being implemented.
- Define the expected before/after balances with integer paise.
- Add a focused service-level test.
- Ensure the operation is atomic and idempotent.
- Confirm that vendor balances and peer balances remain separate.
Do not
- Generate the entire application in one unreviewed pass.
- Move financial logic into route handlers, templates or JavaScript.
- Use floats for money.
- Treat QR creation or UPI Intent launch as payment confirmation.
- Add peer debt solely because an expense share exists.
- Silently net unrelated balances.
- Delete or rewrite transaction history to repair a balance.
- Add real payment processing, wallet functionality or payment gateway dependencies.
- Add unnecessary frameworks or services.
- Introduce fake placeholder behavior and present it as complete.
- Change unrelated modules during a narrowly scoped task.
- Proceed to the next phase without completing the current phase's acceptance criteria.
14. Definition of done
A task or phase is complete only when:
- The requested behavior exists end-to-end within the stated scope.
- Data persists correctly and schema migrations are valid.
- Authorization and validation are enforced server-side.
- Financial rules and edge cases have automated tests where relevant.
- Relevant tests and smoke checks have actually been run.
- The UI communicates real status without misleading the user.
- Documentation and local run instructions are current.
- No secrets or unintended generated/local files are included in the diff.
- The agent reports any remaining limitations rather than claiming full completion.
When in doubt, preserve accounting correctness, user clarity and the agreed product scope over implementation speed or visual novelty.