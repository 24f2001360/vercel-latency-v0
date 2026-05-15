from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.middleware("http")
async def add_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response

@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "*",
        },
    )

# Load dataset
with open("q-vercel-latency.json", "r") as f:
    DATA = json.load(f)

class Request(BaseModel):
    regions: List[str]
    threshold_ms: float

def p95(vals):
    s = sorted(vals)
    idx = 0.95 * (len(s) - 1)

    lo = int(idx)
    hi = lo + 1
    frac = idx - lo

    if hi >= len(s):
        return round(s[lo], 2)

    return round(
        s[lo] + frac * (s[hi] - s[lo]),
        2
    )

@app.post("/")
@app.post("")
def analyze(req: Request):
    result = []

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
            continue

        lats = [r["latency_ms"] for r in rows]
        ups = [r["uptime_pct"] for r in rows]

        result.append({
            "region": region,
            "avg_latency": round(sum(lats) / len(lats), 2),
            "p95_latency": p95(lats),
            "avg_uptime": round(sum(ups) / len(ups), 3),
            "breaches": sum(
                1 for l in lats
                if l > req.threshold_ms
            )
        })

    return {"regions": result}

@app.get("/")
def root():
    return {"status": "ok"}
