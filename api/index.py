from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json, os, statistics

app = FastAPI()

# Load data — embed it directly since Vercel can't read files
DATA = [{"region":"apac","service":"analytics","latency_ms":188.96,"uptime_pct":98.132,"timestamp":20250301},{"region":"apac","service":"recommendations","latency_ms":226.56,"uptime_pct":98.042,"timestamp":20250302},{"region":"apac","service":"payments","latency_ms":188.22,"uptime_pct":98.003,"timestamp":20250303},{"region":"apac","service":"payments","latency_ms":131.29,"uptime_pct":98.877,"timestamp":20250304},{"region":"apac","service":"recommendations","latency_ms":182.67,"uptime_pct":99.491,"timestamp":20250305},{"region":"apac","service":"recommendations","latency_ms":210.17,"uptime_pct":98.838,"timestamp":20250306},{"region":"apac","service":"support","latency_ms":199.19,"uptime_pct":97.434,"timestamp":20250307},{"region":"apac","service":"support","latency_ms":155.44,"uptime_pct":98.514,"timestamp":20250308},{"region":"apac","service":"support","latency_ms":221.65,"uptime_pct":99.252,"timestamp":20250309},{"region":"apac","service":"payments","latency_ms":175.33,"uptime_pct":98.184,"timestamp":20250310},{"region":"apac","service":"analytics","latency_ms":134.51,"uptime_pct":98.658,"timestamp":20250311},{"region":"apac","service":"analytics","latency_ms":158.74,"uptime_pct":99.025,"timestamp":20250312},{"region":"emea","service":"checkout","latency_ms":105.13,"uptime_pct":97.282,"timestamp":20250301},{"region":"emea","service":"recommendations","latency_ms":127.69,"uptime_pct":98.128,"timestamp":20250302},{"region":"emea","service":"analytics","latency_ms":112.36,"uptime_pct":97.593,"timestamp":20250303},{"region":"emea","service":"support","latency_ms":138.13,"uptime_pct":97.43,"timestamp":20250304},{"region":"emea","service":"support","latency_ms":189.7,"uptime_pct":98.376,"timestamp":20250305},{"region":"emea","service":"catalog","latency_ms":174.41,"uptime_pct":99.065,"timestamp":20250306},{"region":"emea","service":"payments","latency_ms":220.88,"uptime_pct":98.787,"timestamp":20250307},{"region":"emea","service":"recommendations","latency_ms":147.6,"uptime_pct":99.017,"timestamp":20250308},{"region":"emea","service":"analytics","latency_ms":209.26,"uptime_pct":97.251,"timestamp":20250309},{"region":"emea","service":"catalog","latency_ms":130.46,"uptime_pct":97.149,"timestamp":20250310},{"region":"emea","service":"payments","latency_ms":120.78,"uptime_pct":99.48,"timestamp":20250311},{"region":"emea","service":"analytics","latency_ms":122.43,"uptime_pct":97.264,"timestamp":20250312},{"region":"amer","service":"checkout","latency_ms":226.23,"uptime_pct":99.04,"timestamp":20250301},{"region":"amer","service":"recommendations","latency_ms":162.65,"uptime_pct":97.39,"timestamp":20250302},{"region":"amer","service":"support","latency_ms":140.47,"uptime_pct":97.535,"timestamp":20250303},{"region":"amer","service":"analytics","latency_ms":190.3,"uptime_pct":98.939,"timestamp":20250304},{"region":"amer","service":"support","latency_ms":211.26,"uptime_pct":98.894,"timestamp":20250305},{"region":"amer","service":"payments","latency_ms":223.5,"uptime_pct":98.193,"timestamp":20250306},{"region":"amer","service":"payments","latency_ms":214.46,"uptime_pct":97.687,"timestamp":20250307},{"region":"amer","service":"support","latency_ms":191.86,"uptime_pct":99.261,"timestamp":20250308},{"region":"amer","service":"payments","latency_ms":175.4,"uptime_pct":97.668,"timestamp":20250309},{"region":"amer","service":"payments","latency_ms":153.41,"uptime_pct":97.893,"timestamp":20250310},{"region":"amer","service":"payments","latency_ms":156.96,"uptime_pct":97.475,"timestamp":20250311},{"region":"amer","service":"payments","latency_ms":217.1,"uptime_pct":97.515,"timestamp":20250312}]

class Request(BaseModel):
    regions: List[str]
    threshold_ms: float

def p95(vals):
    s = sorted(vals)
    idx = 0.95 * (len(s) - 1)
    lo, hi = int(idx), int(idx) + 1
    frac = idx - lo
    if hi >= len(s): return round(s[lo], 2)
    return round(s[lo] + frac * (s[hi] - s[lo]), 2)

@app.post("/")
def analyze(req: Request):
    result = []
    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            continue
        lats = [r["latency_ms"] for r in rows]
        ups  = [r["uptime_pct"]  for r in rows]
        result.append({
            "region":      region,
            "avg_latency": round(sum(lats)/len(lats), 2),
            "p95_latency": p95(lats),
            "avg_uptime":  round(sum(ups)/len(ups), 3),
            "breaches":    sum(1 for l in lats if l > req.threshold_ms)
        })
    return {"regions": result}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
