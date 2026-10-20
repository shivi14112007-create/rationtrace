# MASTER BUILD PROMPT: RATIONTRACE
## AI-Powered Public Distribution Transparency, Cross-Portal Intelligence & Audit Platform

Act as a senior full-stack engineer, product architect, UI/UX designer, data engineer, security engineer, and hackathon product strategist.

Build a complete, polished, functional, end-to-end web application named **RationTrace**.

Do not stop at a design mockup or static frontend. Build the frontend, backend, database, data ingestion pipeline, TinyFish integration, audit engine, analytics dashboards, complaint workflow, authentication, tests, documentation, and deployment configuration.

Work directly in the current workspace. First inspect the repository, existing files, dependencies, environment configuration, and installed tools. Preserve useful existing work. Then implement the application incrementally, run it, test it, and fix errors.

Do not merely describe implementation steps. Execute them.

If an external credential or government data source is unavailable, implement the complete integration interface, a clearly labelled demo mode, realistic synthetic data, and setup instructions. Never fabricate successful live integrations.

---

# 1. PRODUCT VISION

Product name: RationTrace

Product category: Public Distribution System (PDS) transparency, ration record auditing, citizen grievance management, and cross-state public-data intelligence.

Core mission:

Help ration beneficiaries understand their entitlements and available transaction records, help Fair Price Shop (FPS) dealers reconcile their authorized stock records, and help government officials identify and investigate potential distribution discrepancies.

Use TinyFish as a meaningful web-intelligence component to discover, navigate, and extract information from supported official public web portals. Normalize the extracted data and use it to power a centralized state-level analytics dashboard.

Core product principles:
- Transparency without unsupported accusations.
- Evidence-based anomaly detection.
- Clear source provenance for every extracted record.
- Accessible interfaces for users with limited digital literacy.
- Privacy-first beneficiary data handling.
- Human verification before any adverse decision.
- Honest distinction between live data, public aggregate data, authorized data, and synthetic demonstration data.

Never claim that an alert proves corruption.
Never claim access to private government databases without credentials and authorization.
Never fabricate real beneficiaries, live transaction records, government approvals, or successful external API calls.

---

# 2. REQUIRED TECHNOLOGY STACK

Use a practical, maintainable architecture.

Frontend:
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui where compatible
- React Router
- Recharts for interactive charts
- Lucide icons
- React Hook Form and Zod for forms and validation
- A suitable query/data-fetching library such as TanStack Query

Backend:
- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic migrations
- PostgreSQL for production
- SQLite as an optional local development fallback

Testing:
- Pytest for backend tests
- Vitest and React Testing Library for frontend tests
- Playwright if browser testing is available

Deployment:
- Frontend deployment compatible with Vercel or Netlify
- Backend compatible with Render or another Python hosting service
- PostgreSQL-compatible hosted database
- Environment-based configuration

Use stable, mutually compatible package versions. Generate the actual dependency files and lockfiles appropriate to the selected package managers.

Do not put API keys or secrets in frontend code.

---

# 3. DESIGN SYSTEM AND UI/UX

Build a premium, credible government-tech SaaS product rather than a generic AI dashboard.

Visual direction:
- Warm off-white backgrounds.
- Deep forest green as the primary brand color.
- Navy or charcoal text.
- Muted saffron accents for important warnings.
- Neutral cards with subtle borders.
- Generous spacing and clear typography.
- Professional data visualization.
- Responsive layouts for desktop, tablet, and mobile.

Avoid excessive gradients, glassmorphism, oversized empty hero sections, excessive rounded cards, random animations, and decorative AI-generated visuals.

Create:
- Consistent navigation.
- Breadcrumbs.
- Search and filters.
- Loading skeletons.
- Empty states.
- Error states.
- Success and warning notifications.
- Accessible color contrast.
- Clear labels and units on every chart.
- Responsive tables with pagination.
- Confirmation dialogs for sensitive actions.

Create a polished RationTrace logo using a simple grain/record/transparency-inspired icon or CSS/SVG artwork. Do not use fake government seals, government emblems, or official-looking approval badges.

Support English and Hindi using a centralized translation system. Include a visible language switcher. All primary navigation, forms, error messages, and beneficiary-facing screens should have translations.

The interface should be understandable to people with limited digital literacy.

---

# 4. USER ROLES AND ROLE-BASED ACCESS

Implement four main application roles and a read-only public analytics view.

A. BENEFICIARY
- View only their own authorized beneficiary profile and records.
- View applicable entitlement information when reliable data is available.
- View available recorded distribution transactions.
- Compare expected entitlement with recorded distribution.
- Report a discrepancy.
- Attach an optional supporting document if enabled.
- Track their complaint reference number and status.
- Read explanations in Hindi or English.

B. FPS DEALER / LOCAL DISTRIBUTOR
- Access only authorized shop-level records.
- View stock received, recorded distribution, and expected closing balance.
- Review flagged stock or transaction inconsistencies.
- Submit explanations and supporting documents.
- Track assigned audit queries.
- Never access unrelated beneficiaries' private data.

C. GOVERNMENT OFFICIAL / PDS INSPECTOR
- View assigned shops, complaints, and flagged discrepancies according to permissions.
- Inspect evidence and source records.
- Assign cases to authorized staff.
- Add investigation notes.
- Request additional information.
- Update cases through an auditable workflow.
- Record a verified outcome and explanation.

D. DEPARTMENT ANALYST / ADMINISTRATOR
- View authorized aggregate data and state-level analytics.
- Manage permitted data sources and ingestion jobs.
- Inspect extraction history and source reliability.
- Review audit trends, reporting coverage, and complaint statistics.
- Manage roles and access according to explicit permissions.
- Configure thresholds and supported regions.

E. PUBLIC ANALYTICS VISITOR
- View only public aggregate statistics and charts.
- Filter by state, district, commodity, and reporting period where data exists.
- Inspect source URLs, extraction timestamps, reporting periods, and data limitations.
- Never view private beneficiary information.

Implement strict backend authorization. Hiding a button in the frontend is not authorization.

Create development demo accounts for each role only when DEMO_MODE is enabled. Use clearly labelled demo identities and document the credentials in the README. Never enable shared demo credentials in production.

---

# 5. APPLICATION PAGES

Build every page below with real frontend-to-backend interactions.

## A. Public Landing Page

Include:
- RationTrace logo and navigation.
- Hero heading: "Every Entitlement Deserves Transparency."
- Supporting copy explaining ration transparency, record auditing, and accountable grievance resolution.
- CTA: Explore Public Dashboard.
- CTA: Sign In.
- Explanation of how RationTrace works.
- Feature sections for beneficiaries, distributors, and officials.
- Live-data versus demo-data status indicator.
- A concise privacy and data limitations section.
- Footer with About, Data Sources, Privacy, and Help.

Do not present synthetic statistics as real-world impact.

## B. Authentication

Create:
- Sign-in page.
- Sign-out.
- Role-based redirects.
- Session management.
- Protected routes.
- Proper password hashing.
- Secure cookie or token handling.
- Login validation and error messages.

Use a practical, secure authentication approach. Do not store plain-text passwords or long-lived sensitive tokens in localStorage.

## C. Beneficiary Dashboard

Display:
- Beneficiary's masked identifier.
- Applicable entitlement by commodity and reporting period.
- Recorded transactions.
- Distribution dates and quantities.
- A comparison between expected and recorded amounts.
- Any unresolved discrepancy reports.
- Complaint status and reference numbers.
- Clear explanations of where data came from.

If personal data is unavailable, use a labelled synthetic beneficiary account.

Include a prominent "Report a Discrepancy" action.

## D. Beneficiary Transaction History

Include:
- Search and date filters.
- Commodity filters.
- Transaction date.
- Recorded quantity.
- Unit.
- Source and reporting period.
- Pagination.
- Export only when authorized.
- Clear distinction between official recorded quantities and beneficiary-reported quantities.

## E. Complaint Management

Create a complete workflow:
- Submit a complaint.
- Choose issue category.
- Select the related transaction or shop if applicable.
- Add a description.
- Upload an optional permitted attachment.
- Generate a unique reference number.
- Display the current status.
- Show a status timeline.
- Allow authorized officials to request information.
- Allow officials to record resolution details.

Suggested statuses:
SUBMITTED
UNDER_REVIEW
INFORMATION_REQUESTED
INVESTIGATION
RESOLVED
CLOSED
REJECTED_WITH_REASON

Require a reason for rejection or closure where appropriate.

Do not send a complaint to a real government authority unless an explicitly configured, authorized integration exists. In demo mode, clearly state that it is a simulated complaint.

## F. Dealer Dashboard

Display:
- Assigned shop.
- Reporting period.
- Opening stock where available.
- Stock received.
- Recorded distribution.
- Expected closing stock.
- Recorded closing stock.
- Unexplained difference.
- Flagged records.
- Audit-query status.

Provide an explanation-submission workflow for discrepancies.

Do not allow dealers to modify imported source records directly. Any corrections must be separate, attributable, and auditable.

## G. Official Audit Dashboard

Build a strong operational interface with:
- Total records ingested.
- Number of validated records.
- Number of records requiring review.
- Open complaints.
- Cases awaiting verification.
- Cases resolved in the selected reporting period.
- State and district filters where supported.
- Shop-level investigation queue where authorized data exists.
- Severity and confidence indicators.
- Searchable, sortable discrepancy table.
- Source evidence panel.
- Case assignment.
- Investigation notes.
- Verification outcome.
- Full audit history.

Clearly distinguish:
- Data-quality issues.
- Accounting discrepancies.
- Beneficiary-reported discrepancies.
- Potentially suspicious patterns.

Do not label any case as confirmed fraud merely because a rule triggered.

## H. State-Level Public Intelligence Dashboard

This is a major product differentiator.

Build a centralized dashboard designed to aggregate comparable data from multiple official state portals.

Required filters:
- State.
- District, when available.
- Commodity.
- Reporting period.
- Source portal.
- Data freshness.
- Live versus demo dataset.

Charts:
1. State-wise reported allocation.
2. State-wise reported offtake or distribution, when the metric is available.
3. Monthly trends.
4. Commodity-level distribution.
5. Stock received versus stock distributed where definitions and periods match.
6. Source coverage and last extraction time.
7. Data-quality issues.
8. Discrepancy counts in the dataset, with a visible note explaining how each count was calculated.

Every chart must have:
- A meaningful title.
- Units.
- Reporting period.
- Data source.
- Last updated timestamp.
- Tooltips.
- Loading, empty, and error states.
- An accessible tabular alternative.
- A note when data is incomplete or non-comparable.

Do not compare metrics that have different definitions or reporting periods without an explicit qualification.

Do not infer shop-level corruption from aggregate state statistics.

## I. TinyFish Intelligence Center

Make TinyFish a first-class, visible product component.

Create a dedicated page containing:
- Configured source portals.
- Source status.
- Source URL.
- Source category.
- Last successful extraction.
- Latest attempted extraction.
- Extraction job status.
- Extracted record count.
- Validation errors.
- Data freshness.
- Source provenance.
- Manual "Run Extraction" action for authorized administrators.
- Extraction history.
- Structured JSON preview.
- Error messages and retry actions.

Provide a configuration screen for approved source URLs and extraction goals.

Do not let arbitrary user-supplied URLs automatically trigger server-side browsing. Restrict sources to an administrator-approved allowlist and validate URLs to reduce SSRF and unsafe-navigation risks.

---

# 6. TINYFISH INTEGRATION — MANDATORY

Use the official TinyFish Web Agent API and current official documentation.

Official resources to consult:
https://docs.tinyfish.ai/
https://tinyfish.ai/

Before implementation:
1. Inspect the current official API documentation.
2. Identify the correct endpoint, authentication mechanism, request payload, supported execution mode, and response structure.
3. Verify whether the selected extraction workflow supports structured JSON output and asynchronous job handling.
4. Implement against the actual documented API. Do not invent endpoint paths or request fields.

Store the API key in the backend environment variable:

TINYFISH_API_KEY=

Create a configurable TinyFish integration service, separate from API route handlers and business logic.

Suggested modules:
backend/app/integrations/tinyfish_client.py
backend/app/services/extraction_service.py
backend/app/services/data_normalization_service.py
backend/app/services/audit_service.py

The TinyFish workflow should:

1. Navigate an administrator-approved official public portal.
2. Locate the requested reporting page.
3. Extract only information visibly or programmatically available to the agent.
4. Return structured records containing fields such as:
   - source_url
   - source_name
   - state
   - district, if available
   - shop_identifier, only if lawfully available
   - commodity
   - metric_name
   - quantity
   - unit
   - reporting_period
   - extraction_timestamp
   - evidence_text or relevant source reference
5. Return null for unavailable fields.
6. Preserve source provenance.
7. Store the extraction job and its result.
8. Validate the result before it is used by analytics or auditing.

Implement:
- API timeout handling.
- Retry with bounded exponential backoff where appropriate.
- Rate limiting.
- Structured logging without secrets.
- Job status tracking.
- Duplicate detection.
- Idempotent ingestion.
- Schema validation.
- Partial-result handling.
- Error reporting.
- A configurable polling or completion mechanism if the documented API requires it.

Never expose the TinyFish API key to the browser.

Never treat a model-generated value as a verified government record unless the source evidence supports it.

Never use an unrestricted crawler to collect private personal information.

Never fabricate a successful live TinyFish run if no API key is configured.

## TinyFish demonstration mode

If TINYFISH_API_KEY is missing:
- Display "TinyFish not configured — demo mode" in the UI.
- Use an explicitly labelled sample extraction fixture.
- Demonstrate the same extraction-job and validation workflow using synthetic records.
- Show that the result is simulated.
- Do not describe the fixture as live extraction.

When credentials are configured, provide a genuine live extraction test against a selected, accessible official public portal.

Do not require an external API call for the application to boot.

---

# 7. OFFICIAL DATA SOURCES

Investigate available public sources, including:

NFSA:
https://nfsa.gov.in/

NFSA Public Allocation Dashboard:
https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx

IMPDS:
https://impds.nic.in/sale/

Delhi Food Security:
https://nfs.delhigovt.nic.in/

These are candidate starting points. Verify current accessibility, terms of use, and the specific information each page actually exposes.

Do not assume all portals expose downloadable shop-level records or public beneficiary-level transaction data.

Create an administrator-configurable source registry. Each source should include:
- Name.
- Approved URL.
- State or jurisdiction.
- Data categories available.
- Extraction instructions.
- Expected output schema.
- Last checked timestamp.
- Access and reliability notes.

Use TinyFish to extract publicly accessible data where supported.

If a portal exposes data through a documented open API or downloadable dataset, prefer a reliable supported integration when appropriate, while keeping TinyFish meaningfully integrated into the required web-intelligence workflow.

For data that is inaccessible or incomplete:
- Record the limitation.
- Do not bypass authentication.
- Do not fabricate a successful extraction.
- Use synthetic data for demonstration and clearly identify it as synthetic.

Build an initial useful dataset with a small number of well-structured sample records. Do not create enormous fake datasets merely to make charts look impressive.

---

# 8. DATABASE DESIGN

Create normalized SQLAlchemy models and Alembic migrations.

Suggested entities:

User:
- id
- full_name
- email or username
- password_hash
- role
- preferred_language
- status
- created_at

BeneficiaryProfile:
- id
- user_id
- masked_beneficiary_identifier
- authorized_region
- data_source_id

FairPriceShop:
- id
- shop_identifier
- state
- district
- authorized_metadata

DataSource:
- id
- name
- source_url
- jurisdiction
- source_type
- is_approved
- is_enabled
- last_checked_at

ExtractionJob:
- id
- source_id
- job_status
- started_at
- completed_at
- records_extracted
- records_validated
- error_summary
- mode (LIVE or DEMO)

SourceRecord:
- id
- source_id
- extraction_job_id
- region
- commodity
- metric_name
- quantity
- unit
- reporting_period
- evidence_reference
- extracted_at
- record_hash
- validation_status

StockRecord:
- id
- shop_id
- reporting_period
- opening_stock
- received_quantity
- distributed_quantity
- recorded_closing_stock
- source_record_id

DistributionTransaction:
- id
- beneficiary_reference
- shop_id
- transaction_date
- commodity
- recorded_quantity
- unit
- source_record_id

Discrepancy:
- id
- category
- severity
- status
- related_shop_id
- related_transaction_id
- expected_value
- observed_value
- difference
- reason
- evidence_summary
- created_at
- reviewed_at

Complaint:
- id
- reference_number
- beneficiary_id
- related_shop_id
- related_transaction_id
- category
- description
- status
- created_at
- updated_at
- resolution_summary

InvestigationEvent:
- id
- complaint_id or discrepancy_id
- actor_id
- event_type
- note
- created_at

AuditLog:
- id
- actor_id
- action
- entity_type
- entity_id
- timestamp
- safe metadata

Adapt the schema as needed. Add foreign keys, indexes, constraints, relationships, and suitable decimal types for quantities.

Do not store unnecessary identity information. Avoid storing full ration-card numbers or Aadhaar numbers unless a separately authorized, justified, and secured requirement exists. Never use Aadhaar as a casual demo identifier.

Use synthetic identities in the development seed data.

---

# 9. DATA VALIDATION AND ANOMALY DETECTION

Implement a transparent rule-based audit engine first.

Rule A — Stock reconciliation:
Expected closing stock = opening stock + received quantity - distributed quantity - documented adjustments.

Compare expected closing stock with recorded closing stock.

Rule B — Negative stock:
Flag records whose calculated or recorded stock becomes negative, subject to reporting-period and adjustment checks.

Rule C — Missing or duplicate transactions:
Detect duplicate transaction identifiers where available and incomplete records that prevent reliable reconciliation.

Rule D — Entitlement comparison:
Compare applicable entitlement with recorded distribution only when the beneficiary eligibility, reporting period, commodity, and entitlement rules are known.

Rule E — Unusual patterns:
Optionally flag repeated identical quantities, sudden shifts, or statistically unusual values for human review.

For every alert, store:
- Rule that triggered.
- Input records used.
- Calculation.
- Difference and unit.
- Reporting period.
- Evidence/source references.
- Confidence or data-quality assessment.
- Verification status.

Distinguish missing data from a real zero value.

Never assume a missing field equals zero.

Do not call an anomaly confirmed fraud.

Build automated unit tests for all rules and edge cases.

---

# 10. API ENDPOINTS

Implement documented REST APIs using FastAPI.

Suggested endpoint groups:

Authentication:
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/me

Beneficiaries:
GET /api/beneficiaries/me
GET /api/beneficiaries/me/transactions
GET /api/beneficiaries/me/entitlements

Complaints:
POST /api/complaints
GET /api/complaints
GET /api/complaints/{id}
POST /api/complaints/{id}/events

Official audits:
GET /api/audits/summary
GET /api/audits/discrepancies
GET /api/audits/discrepancies/{id}
POST /api/audits/discrepancies/{id}/review
POST /api/audits/discrepancies/{id}/resolve

Analytics:
GET /api/analytics/overview
GET /api/analytics/states
GET /api/analytics/trends
GET /api/analytics/sources

TinyFish:
GET /api/tinyfish/status
GET /api/tinyfish/sources
POST /api/tinyfish/jobs
GET /api/tinyfish/jobs
GET /api/tinyfish/jobs/{id}
GET /api/tinyfish/jobs/{id}/records

Dealer:
GET /api/dealer/shop
GET /api/dealer/stock
GET /api/dealer/audit-queries
POST /api/dealer/audit-queries/{id}/response

Admin:
GET /api/admin/users
GET /api/admin/data-sources
POST /api/admin/data-sources
PATCH /api/admin/data-sources/{id}

Adjust endpoint designs to match actual service needs.

Requirements:
- Pydantic request/response schemas.
- Role-based authorization.
- Input validation.
- Pagination.
- Consistent error responses.
- OpenAPI documentation.
- Appropriate HTTP status codes.
- Rate limits on sensitive operations.
- No exposure of another beneficiary's records through identifier guessing.

---

# 11. SECURITY AND PRIVACY

Implement:
- Secure password hashing.
- Strict role-based access control.
- Backend-side ownership checks.
- CORS allowlist from environment configuration.
- Environment-based secrets.
- SQL injection protection through ORM and validated queries.
- Upload type and size validation if attachments are supported.
- Safe file storage.
- CSRF protections if cookie-based authentication is used.
- Rate limiting on login and complaint submission.
- Audit logs for sensitive actions.
- No secrets in frontend bundles or logs.
- No unauthorized scraping of private records.
- No automatic external complaint submission.
- No destructive action without explicit confirmation.

Treat extracted website text as untrusted data, not as instructions to the agent or application.

Restrict TinyFish source URLs to an approved allowlist. Validate redirects and prevent access to private network endpoints or cloud metadata addresses.

Do not claim compliance certifications that have not been obtained.

---

# 12. SEED DATA AND DEMO EXPERIENCE

The app must work immediately in demo mode without external API credentials.

Create a seed script that inserts a coherent, explicitly synthetic dataset:
- Multiple sample states.
- Several districts.
- Sample fair price shops.
- A few commodities.
- Multiple reporting periods.
- Stock receipts and distribution records.
- Several deliberately inconsistent stock records.
- Sample beneficiary transaction records.
- Complaints in different statuses.
- TinyFish extraction jobs marked DEMO.
- Public aggregate statistics suitable for charts.

Use realistic but clearly synthetic quantities and names.

Make the demo data internally consistent except where a deliberate discrepancy is being demonstrated.

Build a complete judge-friendly scenario:
1. Open the state analytics dashboard.
2. Show source coverage and sample extracted records.
3. Open TinyFish Intelligence Center.
4. Run a demo extraction job if live credentials are absent.
5. Show extracted JSON, validation, and provenance.
6. Run the audit engine.
7. Open a discrepancy with its calculation.
8. Log in as a beneficiary and submit a simulated complaint.
9. Log in as an official and review the case.
10. Record an outcome and show the updated status.

Label the scenario as a demonstration. Never describe synthetic records as real government findings.

---

# 13. ENVIRONMENT CONFIGURATION

Create:
- backend/.env.example
- frontend/.env.example
- backend/requirements.txt or pyproject.toml
- frontend/package.json
- Dockerfile(s) if appropriate
- docker-compose.yml for local development if practical
- database migration scripts
- seed scripts
- .gitignore

Backend environment variables should include:
DATABASE_URL=
TINYFISH_API_KEY=
TINYFISH_BASE_URL=
APP_ENV=development
DEMO_MODE=true
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=
UPLOAD_DIR=

Only use a TinyFish base URL if the official documentation confirms the configuration. Never invent undocumented environment options or endpoints.

Provide safe local defaults for non-secret settings. Fail with clear errors if a required production secret is missing.

Never commit actual .env files or secrets.

---

# 14. TESTING AND QUALITY ASSURANCE

Write tests covering:
- Login and role permissions.
- Beneficiary ownership boundaries.
- Complaint creation and status updates.
- Stock reconciliation calculations.
- Duplicate and missing data handling.
- TinyFish fixture parsing.
- TinyFish error and timeout handling.
- Data-source validation.
- Analytics filters.
- Demo-mode labeling.
- Database migrations.
- Frontend critical user flows.

Run:
- Backend tests.
- Frontend tests.
- TypeScript type checks.
- Linting.
- Production frontend build.
- Database migration checks.
- API smoke tests.

Fix errors instead of simply reporting them.

Do not claim tests passed unless they were actually executed.

---

# 15. DEPLOYMENT AND DOCUMENTATION

Create a comprehensive README containing:
- Product overview.
- Architecture diagram using Mermaid.
- Features by user role.
- Tech stack.
- Folder structure.
- Local setup instructions for Windows PowerShell and macOS/Linux.
- Environment setup.
- Database initialization.
- Seed-data setup.
- Demo credentials and their permitted environment.
- TinyFish API setup based on official documentation.
- How to configure an approved source portal.
- How to run a live extraction.
- How to interpret discrepancies.
- How to deploy frontend and backend.
- Limitations and data privacy notes.
- Troubleshooting.

Include a concise demo script for a 3–5 minute SIH presentation.

Provide example API requests and responses where useful.

Ensure the project can be started using documented commands. Do not hard-code localhost URLs throughout the application; configure the API base URL using environment variables.

---

# 16. IMPLEMENTATION PLAN

Work through the following phases without abandoning the project halfway.

Phase 1: Inspect the workspace, plan the architecture, create the folder structure and dependencies.

Phase 2: Build database models, migrations, seed data, and core backend APIs.

Phase 3: Build authentication and role-based permissions.

Phase 4: Build the public landing page, shared layout, language switching and all dashboards.

Phase 5: Implement TinyFish integration using verified official API documentation.

Phase 6: Implement source normalization, data provenance, stock reconciliation, anomaly detection and analytics.

Phase 7: Implement complaint management and official verification workflows.

Phase 8: Run tests, launch the app, inspect the UI, fix errors, and verify the end-to-end demo.

Phase 9: Complete README, environment examples, and deployment configuration.

Do not stop after producing a plan. Continue implementing phases until the available environment prevents further work.

If you encounter an external dependency that cannot be accessed, implement the remaining work using a clearly labelled mock adapter and document precisely what is still required for live operation.

---

# 17. DEFINITION OF DONE

The project is complete only when:
- The frontend starts successfully.
- The backend starts successfully.
- Database migrations and seeding work.
- Every navigation item leads to a functioning page.
- Main dashboards display data from backend APIs.
- The charts are filterable and show data provenance.
- Beneficiaries can submit and track demo complaints.
- Authorized officials can review cases and record outcomes.
- Dealers can view authorized sample shop records.
- The audit engine detects deliberate test discrepancies correctly.
- TinyFish integration uses verified API details.
- Demo mode works without an API key and is visibly labelled.
- Live mode does not falsely report success when credentials are absent.
- Access controls are enforced on the backend.
- Automated tests and production builds have been run.
- README setup instructions match the actual implementation.

Begin by inspecting the current workspace and official TinyFish documentation. Then build the application end-to-end. Prioritize a reliable, integrated product over unnecessary complexity, and report the actual implementation status, test results, and remaining external setup requirements at the end.