"""Optional Python FastAPI learning backend. Currently serves synthetic sample JSON.

Run from backend/: fastapi dev main.py
The Next.js frontend currently uses its own /api routes. This Python server
is a separate starting point for a future SEC ingestion and cost-estimation service.
"""
from pathlib import Path
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Money Research API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample.json"


def demo_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@app.get("/api/health")
def health():
    return {"status": "ok", "data_mode": "synthetic_demo"}


@app.get("/api/managers")
def managers():
    data = demo_data()
    return {"demo": True, "disclaimer": data["disclaimer"], "managers": [
        {key: value for key, value in item.items() if key != "holdings"}
        for item in data["managers"]
    ]}


@app.get("/api/holdings")
def holdings(ticker: str | None = Query(default=None), manager: str | None = Query(default=None)):
    data = demo_data()
    records = [
        {**position, "managerId": fund["id"], "managerName": fund["name"]}
        for fund in data["managers"]
        for position in fund["holdings"]
    ]
    if ticker:
        records = [record for record in records if record["ticker"] == ticker.upper().strip()]
    if manager:
        records = [record for record in records if record["managerId"] == manager]
    return {"demo": True, "disclaimer": data["disclaimer"], "holdings": records}
