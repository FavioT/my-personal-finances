# My Personal Finances Dashboard

A personal finance dashboard that processes bank account summaries (`.xls`/`.xlsx`) and credit card statements (`.pdf`) to display your transactions and spending in a web interface.

## Stack

- **Backend:** Python 3.11+, FastAPI, pandas, pdfplumber, SQLAlchemy, SQLite/PostgreSQL
- **Frontend:** Angular 18+, TypeScript, Angular Material, ng2-charts (Chart.js)
- **Deployment:** Vercel (Python serverless + static Angular)

## Deploying to Vercel

### 1. Database (Neon PostgreSQL)
Create a free [Neon](https://neon.tech) project and copy the connection string.

### 2. Vercel Environment Variables
Set these in your Vercel project → Settings → Environment Variables:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require` |
| `FRONTEND_ORIGIN` | Your Vercel deployment URL (for CORS) | `https://my-personal-finances.vercel.app` |

### 3. Deploy
```bash
# Install Vercel CLI if needed
npm install -g vercel

# From the project root
vercel
```

Or connect the GitHub repo to Vercel for automatic deployments on push.

### How it works
- `api/index.py` exposes the FastAPI app as a Vercel Python serverless function
- Routes matching `/api/*` are forwarded to the Python function
- Angular is built via `frontend/package.json`'s `vercel-build` script and served as static files
- Angular's client-side routing is handled by the fallback `/(.*) → index.html` route

---

## Requirements

- Python 3.11+
- Node.js 18+ and npm
- Angular CLI 18+ (`npm install -g @angular/cli@18`)

## Running the Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # en lugar de "source"
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## Running the Frontend

```bash
cd frontend
npm install
ng serve
```

The app will be available at `http://localhost:4200`.

## File Upload Notes

> **Important:** The XLS and PDF parsers are implemented as "best-effort" generic parsers. Because every bank and credit card provider formats their files differently, you may need to adapt the parsers in `backend/parsers/` to match your specific bank's column names and layout.

### XLS Parser (`backend/parsers/xls_parser.py`)
Tries to auto-detect columns using common names: `fecha`/`date`, `descripción`/`description`, `importe`/`amount`, `débito`/`crédito`.  
If columns cannot be detected, the endpoint returns a `400` error listing the detected column names so you can update the mapping.

### PDF Parser (`backend/parsers/pdf_parser.py`)
Extracts the first table found in the PDF using pdfplumber and applies the same column mapping logic.

## Project Structure

```
my-personal-finances/
├── README.md
├── .gitignore
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py
│   │   └── transactions.py
│   └── parsers/
│       ├── __init__.py
│       ├── xls_parser.py
│       └── pdf_parser.py
└── frontend/
    └── (Angular 18 project)
```
 
