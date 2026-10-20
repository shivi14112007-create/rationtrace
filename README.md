# RationTrace (राशनट्रेस) 🌾
### Evidence-Based Public Food Security Reconciliation & Autonomous PDS Intelligence

RationTrace is a transparent, audit-ready public distribution monitoring and reconciliation platform. It combines autonomous web intelligence agents (**TinyFish**) with deterministic inventory ledger rules (Rule A & Rule B) to identify stock shortfalls, phantom distributions, and record anomalies across Public Distribution System (PDS) Fair Price Shops (FPS) without making unsupported accusations.

---

## 🌟 Key Features

1. **Autonomous Public Portal Intelligence (TinyFish Agent)**:
   - Configurable source registry with admin-approved allowlist domain enforcement (`nfsa.gov.in`, `epos.bihar.gov.in`, etc.).
   - Strict output schema validation (depth $\le 10$, size $\le 64\text{ KB}$, rejection of unsupported keywords).
   - Cryptographic SHA-256 integrity hashes for each extracted data point.
   - Genuine live extraction with exponential backoff retries; fallback to clearly labelled `DEMO` fixtures when offline (never faking a live success).

2. **Deterministic Mathematical Reconciliation Engine**:
   - **Rule A (Balanced Stock Equation)**: $\text{Opening Stock} + \text{Received} - \text{Distributed} = \text{Closing Stock}$. Discrepancies $\ge 500\text{ kg}$ trigger HIGH alerts; $\ge 1,000\text{ kg}$ trigger CRITICAL alerts.
   - **Rule B (Negative Stock & Over-Distribution)**: $\text{Closing Stock} < 0$ or $\text{Distributed} > \text{Available Stock}$.

3. **Dual-Language Accessibility & Design System**:
   - Palette: Warm off-white background (`#fcfaf7`), Forest Green primary (`#1b5e3a`), Saffron warnings (`#d97706`).
   - English / Hindi (हिन्दी) real-time language switcher across all core views.
   - 100% accessible tabular alternatives for every visualization chart in State Analytics.

4. **Multi-Role Portals**:
   - **Beneficiaries**: Card quota vs. recorded slip receipts, digital dispute filing with unique tracking reference (`RT-2026-COMP-XXXX`).
   - **Inspectors / Officials**: Audit queue, formula inspector, voucher verification and dispute resolution workflows.
   - **Public / State Analytics**: Commodity allocations, state distributions, and data provenance.

---

## 🔑 Demo Credentials

All test accounts share the same password for zero-friction evaluation.

| Role | Username | Password | Intended Workflow |
| :--- | :--- | :--- | :--- |
| **Beneficiary** | `beneficiary_demo` | `Demo123!` | View ration cards, slips, and file official grievances |
| **Official (Auditor)** | `official_demo` | `Demo123!` | Run audit engine, inspect math formulas, resolve cases |
| **Dealer (Shop Owner)** | `dealer_demo` | `Demo123!` | View shop stock reconciliation and audit queries |
| **Administrator** | `admin_demo` | `Demo123!` | System configuration, source registry, and jobs |

> *Tip: The Login page includes 1-click quick-fill buttons for each role.*

---

## 🚀 Quickstart & Setup Guide

### System Requirements
- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 18.x or 20.x+ (with `npm`)

---

### Windows Setup (PowerShell)

#### 1. Clone & Enter Project Root
```powershell
git clone <repo-url> rationtrace
cd rationtrace
```

#### 2. Backend Setup
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
Copy-Item backend\.env.example backend\.env

# (Optional) If you have a TinyFish API key:
# Edit backend\.env and set TINYFISH_API_KEY=sk-tinyfish-...

# Seed database and start FastAPI server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend automatically creates and seeds `rationtrace.db` on first boot.*

#### 3. Frontend Setup (Open a second PowerShell window)
```powershell
cd rationtrace/frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
*Frontend opens at `http://localhost:5173/`.*

---

### macOS & Linux Setup (Bash / Zsh)

#### 1. Clone & Enter Project Root
```bash
git clone <repo-url> rationtrace
cd rationtrace
```

#### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp backend/.env.example backend/.env

# (Optional) Set TINYFISH_API_KEY in backend/.env if available

# Start FastAPI server
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 3. Frontend Setup (Open a second terminal window)
```bash
cd rationtrace/frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## ⏱️ 3-Minute Judge-Friendly Demo Script (Spec Section 12)

Follow this 10-step sequence to demonstrate the complete reconciliation workflow:

### **Minute 1: Public Transparency & Autonomous Intelligence**
1. **Open State Analytics (`/analytics`)**:
   - View Allocation vs. Distribution across Delhi, Uttar Pradesh, and Bihar.
   - Click **"Switch to Accessible Table"** to show accessibility compliance and data provenance disclaimers.
   - Switch language to **हिन्दी** in the top bar to show bilingual localization, then back to English.
2. **Open TinyFish Intelligence Center (`/tinyfish`)**:
   - Review the **Live Key indicator**, **Base URL**, and **Approved Source Registry**.
   - Click **"+ Trigger Extraction Job"**, choose `DEMO` (or `AUTO` / `LIVE`), and execute.
   - Click **"Inspect Evidence / Records"** on Job #1 to show the 32 parsed records, cryptographic **SHA-256 integrity hashes**, and structured JSON payload.

### **Minute 2: Deterministic Audit Engine & Evidence Verification**
3. **Log in as Official**:
   - Navigate to `/login` and click the **"Official (Auditor / Inspector)"** 1-click button.
4. **Open Official Audit Dashboard (`/audits`)**:
   - Click **"⚡ Run Full Audit Engine"** to trigger real-time re-evaluation of inventory registers.
   - In the Discrepancy Queue, click **"Inspect Evidence"** on an open alert (e.g., `FPS-UP-0881` or `FPS-DL-0142`).
   - Highlight the **formula breakdown**: `Opening + Received - Distributed vs Closing Stock`.
   - In the resolution panel, select `REGISTER_VOUCHERS_VERIFIED`, type *"Inspector verified physical transit vouchers against central allotment"*, and click **"Record Verified Outcome"**.
   - Notice the status immediately switches to **RESOLVED** with an audit event recorded.

### **Minute 3: Beneficiary Empowerment & Grievance Redressal**
5. **Log in as Beneficiary**:
   - Click **Sign Out** and on `/login`, click the **"Beneficiary"** 1-click button (`beneficiary_demo`).
6. **Beneficiary Portal (`/beneficiary`)**:
   - View assigned NFSA entitlement cards (Wheat / Rice quota) and past electronic distribution slips.
   - Click **"File Grievance / Report Discrepancy"**.
   - Select Category **"Foodgrain Quality Defect"** and type *"Received discolored wheat grains with moisture smell"*.
   - Click **"Submit Official Grievance"** and highlight the generated reference tracking code (`RT-2026-COMP-XXXX`).
   - Confirm that the grievance immediately appears in the investigation timeline.

---

## 🧪 Running Tests

The test suite validates backend API endpoints, TinyFish domain allowlist security, output schema validation, retry handling, and ledger math:

```bash
# Run backend tests
pytest backend/tests/ -v
```

Expected output:
```
33 passed in 2.8s
```

Frontend production bundle verification:
```bash
cd frontend
npm run build
```

---

## ⚖️ Legal & Non-Defamation Commitment

RationTrace operates strictly on objective, verifiable electronic records. Discrepancies are flagged as statistical variances requiring physical inspection, never as criminal accusations. Demonstration fixtures are clearly watermarked as synthetic to prevent confusion with official government orders.
