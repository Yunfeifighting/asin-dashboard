import time
import requests
from datetime import datetime, timezone

KEEPA_EPOCH = 1293840000


def _parse_keepa_csv(csv, is_bsr=False):
    if not csv or len(csv) < 2:
        return [None] * 7
    pairs = list(zip(csv[::2], csv[1::2]))
    now_km = int((time.time() - KEEPA_EPOCH) / 60)
    week_km = 7 * 24 * 60
    recent = [(t, v) for t, v in pairs if t >= now_km - week_km and v != -1]
    if not recent:
        return [None] * 7
    day_map = {}
    for t, v in recent:
        dk = (now_km - t) // (24 * 60)
        if dk <= 6:
            day_map[dk] = v
    result = []
    for i in range(6, -1, -1):
        raw = day_map.get(i)
        if raw is None:
            result.append(None)
        elif is_bsr:
            result.append(raw)
        else:
            result.append(round(raw / 100, 2))
    return result


def fetch_keepa(asin, api_key):
    url = "https://api.keepa.com/product"
    params = {"key": api_key, "domain": 1, "asin": asin, "stats": 90, "history": 1}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    products = data.get("products")
    if not products:
        raise ValueError(f"Keepa: ASIN {asin} not found")
    p = products[0]
    csv = p.get("csv") or []
    stats = p.get("stats") or {}
    current = stats.get("current") or []
    avg90 = stats.get("avg90") or []
    min90 = stats.get("min") or []
    max90 = stats.get("max") or []

    def safe_get(arr, idx, divisor=1):
        try:
            v = arr[idx]
            return round(v / divisor, 2) if v and v > 0 else None
        except (IndexError, TypeError):
            return None

    price_7d = _parse_keepa_csv(csv[1] if len(csv) > 1 else [], is_bsr=False)
    bsr_7d = _parse_keepa_csv(csv[3] if len(csv) > 3 else [], is_bsr=True)
    sales_ranks = p.get("salesRanks") or {}
    sub_bsr = {}
    for cat_id, rank_arr in sales_ranks.items():
        if rank_arr and len(rank_arr) >= 2:
            sub_bsr[cat_id] = rank_arr[-1]
    return {
        "current_price": safe_get(current, 1, 100),
        "current_bsr": safe_get(current, 3),
        "price_7d": price_7d,
        "bsr_7d": bsr_7d,
        "sub_bsr": sub_bsr,
        "monthly_sold": p.get("monthlySold") or 0,
        "price_90d_avg": safe_get(avg90, 1, 100),
        "price_90d_min": safe_get(min90, 1, 100),
        "price_90d_max": safe_get(max90, 1, 100),
        "rating": round((stats.get("rating") or 0) / 10, 1),
        "review_count": stats.get("reviewCount") or 0,
        "tokens_left": data.get("tokensLeft"),
        "liked_asins": (p.get("likedASINs") or [])[:5],
    }


def fetch_product(asin, api_key):
    url = "https://api.rainforestapi.com/request"
    params = {"api_key": api_key, "type": "product", "asin": asin, "amazon_domain": "amazon.com"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "product" not in data:
        msg = data.get("request_info", {}).get("message", "unknown error")
        raise ValueError(f"Rainforest: {msg}")
    p = data["product"]
    bsr_list = p.get("bestsellers_rank") or []
    buybox = p.get("buybox_winner") or {}
    price_obj = buybox.get("price") or {}
    return {
        "title": p.get("title", ""),
        "brand": p.get("brand", ""),
        "main_image": (p.get("main_image") or {}).get("link", ""),
        "images": [(img.get("link", "")) for img in (p.get("images") or [])[:6]],
        "current_price": price_obj.get("value"),
        "currency": price_obj.get("currency", "USD"),
        "rating": p.get("rating"),
        "review_count": p.get("ratings_total"),
        "is_prime": buybox.get("is_prime", False),
        "is_fba": buybox.get("fulfillment", {}).get("type") == "Amazon",
        "bsr": bsr_list[0]["rank"] if bsr_list else None,
        "bsr_category": bsr_list[0]["category"] if bsr_list else "",
        "all_bsr": bsr_list,
        "feature_bullets": (p.get("feature_bullets") or [])[:5],
        "variant_count": len(p.get("variants") or []),
        "img_count": len(p.get("images") or []),
        "answered_questions": p.get("answered_questions"),
    }


def fetch_competitors(search_term, api_key, exclude_asin, count=5):
    url = "https://api.rainforestapi.com/request"
    params = {
        "api_key": api_key, "type": "search", "search_term": search_term,
        "amazon_domain": "amazon.com", "sort_by": "featured", "exclude_sponsored": True,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("search_results") or []
    out = []
    for r in results:
        if r.get("asin") == exclude_asin:
            continue
        price_obj = r.get("price") or {}
        out.append({
            "asin": r.get("asin", ""),
            "title": (r.get("title") or "")[:60],
            "price": price_obj.get("value"),
            "rating": r.get("rating"),
            "review_count": r.get("ratings_total"),
            "is_prime": r.get("is_prime", False),
            "thumbnail": r.get("image", ""),
        })
        if len(out) >= count:
            break
    return out
