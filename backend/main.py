"""
SAMANVAY-WX FastAPI backend stub
Run:  uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import math, random, datetime

app = FastAPI(title="SAMANVAY-WX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

MODELS = [
    {"id": "ncumg", "name": "NCUM-G",        "type": "Physical NWP", "color": "#1a6dff"},
    {"id": "neps",  "name": "NEPS",          "type": "Ensemble",     "color": "#00b8a9"},
    {"id": "ncumr", "name": "NCUM-R",        "type": "Regional NWP", "color": "#ff6b4a"},
    {"id": "pangu", "name": "Pangu-Weather", "type": "AI/ML",        "color": "#a259ff"},
    {"id": "graph", "name": "GraphCast",     "type": "AI/ML",        "color": "#ffb000"},
]

STATE = {"ledger": []}

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "models_online": len(MODELS)}

@app.get("/models")
def models():
    return {"models": MODELS}

@app.get("/blend")
def blend(
    variable: str = Query("t2m", pattern="^(t2m|ws10|rain)$"),
    lead: int = Query(24, ge=0, le=240),
    init: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
):
    w = context_weights(variable, lead)
    val = blended_value(variable, lead, lat, lon)
    return {
        "variable": variable, "lead_hours": lead,
        "init_time": init or datetime.datetime.utcnow().isoformat(),
        "weights": {MODELS[i]["id"]: round(w[i], 4) for i in range(len(MODELS))},
        "value": round(val, 2),
        "interval_80": [round(val * 0.94, 2), round(val * 1.06, 2)],
    }

@app.get("/weights")
def weights(variable: str = "t2m", lead: int = 24, region: Optional[str] = None):
    w = context_weights(variable, lead)
    return {
        "context": {"variable": variable, "lead": lead, "region": region},
        "weights": {MODELS[i]["id"]: round(w[i], 4) for i in range(len(MODELS))},
        "reason_codes": explain_weights(variable, lead),
    }

@app.get("/ledger")
def ledger(limit: int = 50):
    if not STATE["ledger"]:
        STATE["ledger"] = generate_ledger()
    return {"rows": STATE["ledger"][:limit]}

@app.get("/trustguard")
def trustguard(lat: float = 22.5, lon: float = 78.5, lead: int = 24):
    safety = safety_score(lat, lon, lead)
    decision = "publish" if safety > 0.65 else "defer"
    return {
        "safety_score": round(safety, 3),
        "decision": decision,
        "signals": {
            "trust_confidence": round(0.5 + safety * 0.5, 3),
            "disagreement": round(random.uniform(0.1, 0.9), 3),
            "ood_score": round(random.uniform(0.0, 0.8), 3),
            "source_health": 0.94,
        },
        "robustness": round(safety * 1.03, 3),
        "reason_codes": (
            ["regime_match_active_monsoon", "sample_confidence_high"]
            if decision == "publish"
            else ["high_disagreement", "ood_context"]
        ),
    }

@app.get("/verification")
def verification(variable: str = "t2m"):
    leads = [6, 24, 48, 72, 120]
    return {
        "leads": leads,
        "models": {
            "ncumg": {"rmse": [0.90, 1.42, 1.95, 2.55, 3.30], "bias":  0.21},
            "neps":  {"rmse": [0.85, 1.35, 1.80, 2.40, 3.10], "bias": -0.08},
            "pangu": {"rmse": [0.80, 1.28, 1.70, 2.28, 2.95], "bias":  0.05},
            "blend": {"rmse": [0.72, 1.11, 1.48, 2.02, 2.60], "bias":  0.02},
        },
    }

def context_weights(variable, lead):
    base = {
        "t2m":  [0.14, 0.22, 0.12, 0.30, 0.22],
        "ws10": [0.18, 0.20, 0.24, 0.20, 0.18],
        "rain": [0.10, 0.28, 0.10, 0.26, 0.26],
    }.get(variable, [0.2] * 5)
    s = min(0.08, lead / 240 * 0.08)
    w = [base[0] - s, base[1], base[2] - s, base[3] + s, base[4] + s]
    tot = sum(w)
    return [x / tot for x in w]

def blended_value(variable, lead, lat, lon):
    lat = lat or 22.5; lon = lon or 78.5
    base = {"t2m": 32.0, "ws10": 8.5, "rain": 42.0}[variable]
    noise = math.sin(lat * 0.7) * math.cos(lon * 0.7) * 2.5
    return base + noise * (1 + lead / 120)

def explain_weights(variable, lead):
    rc = ["sample_confidence_high", "regime_match_active_monsoon"]
    if lead > 72:
        rc.append("ai_models_gain_weight_long_lead")
    if variable == "rain":
        rc.append("extreme_head_active_precip")
    return rc

def generate_ledger():
    rows = []
    regions = ["North-West India", "Central India", "Peninsular India"]
    for m in MODELS:
        for i, r in enumerate(regions):
            rmse = 0.9 + i * 0.1 + random.uniform(0, 0.3)
            rows.append({
                "model": m["name"], "region": r,
                "rmse": round(rmse, 3),
                "bias": round(random.uniform(-0.3, 0.3), 3),
                "samples": random.randint(800, 5000),
            })
    return rows

def safety_score(lat, lon, lead):
    s = 0.95 - 0.001 * lead
    s -= 0.05 * abs(math.sin(lat * 0.3) * math.cos(lon * 0.3))
    return max(0.1, min(0.99, s))
