# Smart Money Intelligence — Interactive Starter

A local, functional Next.js demo for a future investment research web app. **Every investor profile, holding, share count, market price, change, and cost range in the UI is SYNTHETIC.** This prototype does not fetch current stock prices or real SEC 13F filings and must not be used for investment decisions.

## 1. Requirements

- Node.js recent LTS compatible with current Next.js (see https://nextjs.org/docs/app/getting-started/installation).
- npm, VS Code (optional), modern browser.

## 2. Start the website

Open a terminal in **this extracted folder** (the one with `package.json`):

```bash
npm install
npm run dev
```

Open http://localhost:3000 . If you see the dashboard, the frontend is working.

> If you have already used `create-next-app`, you do not need to nest this project inside that project. Open this folder as an alternative ready-made starter.

## 3. Things you can do immediately

- Search by symbol (e.g. NVDA), company or fictional fund name.
- Click any fictional manager to filter the table.
- Change sorting and filter choices.
- Click a star to track tickers during the current page session (not persisted).
- Inspect working mock API endpoints:
  - http://localhost:3000/api/managers
  - http://localhost:3000/api/holdings?ticker=NVDA
  - http://localhost:3000/api/holdings?manager=harbor

## 4. Main project files

- `app/page.tsx`: interactive UI (client state, filters, watchlist toggle).
- `app/globals.css`: responsive desktop-first visual styling.
- `data/sample.json`: **fake** sample data, shared by the Next.js and Python example API.
- `app/api/*/route.ts`: functioning Next.js JSON endpoints for the demo.
- `backend/main.py`: optional future FastAPI service (currently demo data only).
- `database/schema.sql`: proposed normalized PostgreSQL schema (not installed).
- `docs/data-quality.md`: critical SEC 13F modeling limitations.

## 5. Optional: run a separate Python API

From the extracted project root:

**macOS/Linux**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

**Windows PowerShell**
```powershell
cd backend
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m fastapi dev main.py
```

Open http://127.0.0.1:8000/docs . The frontend does NOT automatically use this Python API yet; it uses the Next.js mock endpoints. This deliberate separation keeps the first run simple.

## 6. Suggested implementation sequence

- **Iteration 1:** Get mock UI running; test search, sorting, filters and mobile view.
- **Iteration 2:** Load a small list of *real* managers with SEC CIKs; build a scheduled ingestion process for SEC Form 13F data. Store raw accession IDs, report periods, and filing dates. Include amended filings.
- **Iteration 3:** Move data to PostgreSQL (e.g. Supabase), replace both demo endpoints with verified read queries, and preserve original SEC filing URLs.
- **Iteration 4:** Add historical adjusted market prices (with appropriate license), implement a range-based cost estimation method with versioned assumptions and validation.
- **Iteration 5:** Introduce source-cited financial research. AI must distinguish reported facts from inference and predictions.
- **Iteration 6:** Deploy the Next.js app (e.g. Vercel), Python worker separately, enable monitoring/auth where needed and test with real users.

## Source references

- SEC official 13F datasets: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
- SEC developer resources: https://www.sec.gov/about/developer-resources
- SEC access guidance: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- Next.js docs: https://nextjs.org/docs/app/getting-started/installation
- FastAPI docs: https://fastapi.tiangolo.com/tutorial/first-steps/

## Risk and legal notes

This is research/education software. Avoid individualized trading advice or automatic orders. Validate data licensing, financial-marketing claims, cybersecurity and relevant investment adviser requirements before commercial launch. No account keys are needed for this demo; keep any future credentials server-side.
