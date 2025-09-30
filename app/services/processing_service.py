# backend/app/services/processing_service.py
import logging
from typing import List, Dict, Any
from rapidfuzz import fuzz  # optional, if installed
logger = logging.getLogger(__name__)

def _score_by_keyword_similarity(query: str, text: str) -> float:
    # optional use of rapidfuzz for robust fuzzy matching, fallback to simple ratio
    try:
        return fuzz.token_sort_ratio(query, text) / 100.0
    except Exception:
        # fallback simple check
        q = query.lower()
        t = text.lower()
        return 1.0 if q in t else 0.0

def _source_trust_score(source: str) -> float:
    # simple trust mapping — tune this to actual providers
    trusted = {"mock_crop_db": 1.0, "trusted_univ": 0.95, "mock_weather": 0.7}
    return trusted.get(source, 0.5)

def _normalize_result(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source": r.get("source"),
        "type": r.get("type"),
        "title": r.get("title") or "",
        "body": r.get("body") or "",
        "score_hint": float(r.get("score_hint") or 0.0),
        "meta": r.get("meta") or {}
    }

def process_results(query: str, raw_results: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Normalize, dedupe, score and rank results.
    Returns top_k ranked results with added 'score' field.
    """
    normalized = [_normalize_result(r) for r in raw_results]

    # dedupe by body/title exact match (very simple)
    seen = set()
    deduped = []
    for r in normalized:
        key = (r["title"].strip().lower(), r["body"].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    scored = []
    for r in deduped:
        # base from score_hint
        score = r.get("score_hint", 0.0)
        # boost by source trust
        score += 0.4 * _source_trust_score(r["source"])
        # boost by keyword similarity between query and title/body
        sim = max(_score_by_keyword_similarity(query, r["title"]), _score_by_keyword_similarity(query, r["body"]))
        score += 0.6 * sim
        # clamp
        score = min(max(score, 0.0), 1.0)
        out = r.copy()
        out["score"] = round(score, 3)
        scored.append(out)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
