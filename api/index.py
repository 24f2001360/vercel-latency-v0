from http.server import BaseHTTPRequestHandler
import json

DATA = [{"region":"apac","latency_ms":188.96,"uptime_pct":98.132},{"region":"apac","latency_ms":226.56,"uptime_pct":98.042},{"region":"apac","latency_ms":188.22,"uptime_pct":98.003},{"region":"apac","latency_ms":131.29,"uptime_pct":98.877},{"region":"apac","latency_ms":182.67,"uptime_pct":99.491},{"region":"apac","latency_ms":210.17,"uptime_pct":98.838},{"region":"apac","latency_ms":199.19,"uptime_pct":97.434},{"region":"apac","latency_ms":155.44,"uptime_pct":98.514},{"region":"apac","latency_ms":221.65,"uptime_pct":99.252},{"region":"apac","latency_ms":175.33,"uptime_pct":98.184},{"region":"apac","latency_ms":134.51,"uptime_pct":98.658},{"region":"apac","latency_ms":158.74,"uptime_pct":99.025},{"region":"emea","latency_ms":105.13,"uptime_pct":97.282},{"region":"emea","latency_ms":127.69,"uptime_pct":98.128},{"region":"emea","latency_ms":112.36,"uptime_pct":97.593},{"region":"emea","latency_ms":138.13,"uptime_pct":97.43},{"region":"emea","latency_ms":189.7,"uptime_pct":98.376},{"region":"emea","latency_ms":174.41,"uptime_pct":99.065},{"region":"emea","latency_ms":220.88,"uptime_pct":98.787},{"region":"emea","latency_ms":147.6,"uptime_pct":99.017},{"region":"emea","latency_ms":209.26,"uptime_pct":97.251},{"region":"emea","latency_ms":130.46,"uptime_pct":97.149},{"region":"emea","latency_ms":120.78,"uptime_pct":99.48},{"region":"emea","latency_ms":122.43,"uptime_pct":97.264},{"region":"amer","latency_ms":226.23,"uptime_pct":99.04},{"region":"amer","latency_ms":162.65,"uptime_pct":97.39},{"region":"amer","latency_ms":140.47,"uptime_pct":97.535},{"region":"amer","latency_ms":190.3,"uptime_pct":98.939},{"region":"amer","latency_ms":211.26,"uptime_pct":98.894},{"region":"amer","latency_ms":223.5,"uptime_pct":98.193},{"region":"amer","latency_ms":214.46,"uptime_pct":97.687},{"region":"amer","latency_ms":191.86,"uptime_pct":99.261},{"region":"amer","latency_ms":175.4,"uptime_pct":97.668},{"region":"amer","latency_ms":153.41,"uptime_pct":97.893},{"region":"amer","latency_ms":156.96,"uptime_pct":97.475},{"region":"amer","latency_ms":217.1,"uptime_pct":97.515}]

def p95(vals):
    s = sorted(vals)
    idx = 0.95 * (len(s) - 1)
    lo = int(idx)
    hi = lo + 1
    frac = idx - lo
    if hi >= len(s): return round(s[lo], 2)
    return round(s[lo] + frac * (s[hi] - s[lo]), 2)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)

        result = []
        for region in regions:
            rows = [r for r in DATA if r["region"] == region]
            if not rows:
                continue
            lats = [r["latency_ms"] for r in rows]
            ups  = [r["uptime_pct"]  for r in rows]
            result.append({
                "region": region,
                "avg_latency": round(sum(lats)/len(lats), 2),
                "p95_latency": p95(lats),
                "avg_uptime":  round(sum(ups)/len(ups), 3),
                "breaches":    sum(1 for l in lats if l > threshold)
            })

        response = json.dumps({"regions": result}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)
