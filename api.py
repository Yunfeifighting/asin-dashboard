import time
import re
import requests
from datetime import datetime, timezone

KEEPA_EPOCH = 1293840000


def _parse_keepa_csv(csv, is_bsr=False):
    """Parse Keepa CSV pairs into 7-day daily values with forward-fill."""
    if not csv or len(csv) < 2:
        return [None] * 7
    pairs = [(t, v) for t, v in zip(csv[::2], csv[1::2]) if v != -1]
    if not pairs:
        return [None] * 7
    now_km = int((time.time() - KEEPA_EPOCH) / 60)
    result = []
    for day in range(6, -1, -1):
        day_end_km = now_km - day * 24 * 60
        candidates = [(t, v) for t, v in pairs if t <= day_end_km]
        if candidates:
            _, raw = max(candidates, key=lambda x: x[0])
            result.append(raw if is_bsr else round(raw / 100, 2))
        else:
            result.append(None)
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
        "api_key": api_key,
        "type": "search",
        "search_term": search_term,
        "amazon_domain": "amazon.com",
        "sort_by": "featured",
        "exclude_sponsored": True,
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


def extract_keywords(title, brand="", n=5):
    """Extract top keywords from product title for ranking lookup."""
    stop = {
        "for", "with", "and", "the", "a", "an", "in", "on", "at", "to", "of", "by",
        "is", "are", "was", "be", "been", "or", "but", "as", "if", "this", "that",
        "it", "its", "from", "up", "out", "into", "compatible", "fits", "fit",
        "works", "use", "used", "using", "made", "new", "pack", "set", "pair",
        "piece", "pcs", "pc", "lot", "includes", "include", "comes", "come",
        "great", "perfect", "ideal", "heavy", "duty", "high", "quality",
    }
    words = re.sub(r"[^\w\s]", " ", title).split()
    content = [w for w in words if w.lower() not in stop and len(w) > 2 and not w.isdigit()]
    keywords = []
    if brand:
        others = [w for w in content if w.lower() != brand.lower()]
        if others:
            keywords.append(brand + " " + " ".join(others[:2]))
    if len(content) >= 3:
        keywords.append(" ".join(content[:3]))
    if len(content) >= 5:
        keywords.append(" ".join(content[1:4]))
    if len(content) >= 6:
        keywords.append(" ".join(content[-3:]))
    seen, result = set(), []
    for kw in keywords:
        k = kw.lower().strip()
        if k not in seen and len(k) > 5:
            seen.add(k)
            result.append(kw)
    return result[:n]


def fetch_keyword_rankings(asin, keywords, competitor_asins, rf_key):
    """Search Amazon for each keyword and find rank of asin + competitors."""
    results = []
    comp_list = competitor_asins or []
    for kw in keywords:
        try:
            params = {
                "api_key": rf_key,
                "type": "search",
                "search_term": kw,
                "amazon_domain": "amazon.com",
            }
            resp = requests.get("https://api.rainforestapi.com/request", params=params, timeout=30)
            resp.raise_for_status()
            items = resp.json().get("search_results") or []
            my_rank = None
            comp_ranks = {}
            for i, item in enumerate(items):
                ia = item.get("asin", "")
                if ia == asin:
                    my_rank = i + 1
                for ca in comp_list:
                    if ia == ca and ca not in comp_ranks:
                        comp_ranks[ca] = i + 1
            top5 = [
                {
                    "asin": r.get("asin", ""),
                    "title": (r.get("title") or "")[:50],
                    "price": (r.get("price") or {}).get("value"),
                }
                for r in items[:5]
            ]
            results.append({
                "keyword": kw,
                "my_rank": my_rank,
                "comp_ranks": comp_ranks,
                "top5": top5,
                "total": len(items),
            })
        except Exception as e:
            results.append({
                "keyword": kw,
                "my_rank": None,
                "comp_ranks": {},
                "top5": [],
                "total": 0,
                "error": str(e),
            })
    return results


def generate_listing_score(product, comp_prices=None):
    """Rule-based listing quality score (0-100) with actionable suggestions."""
    score = 100
    suggestions = []
    comp_prices = comp_prices or []

    title = product.get("title", "")
    title_len = len(title)
    if title_len < 80:
        score -= 15
        suggestions.append({"priority": "critical", "area": "\u6807\u9898",
            "issue": f"\u6807\u9898\u8fc7\u77ed\uff08{title_len}\u5b57\u7b26\uff09\uff0c\u5efa\u800680-200\u5b57\u7b26",
            "action": "\u8865\u5145\u5173\u952e\u8bcd\u3001\u89c4\u683c\u578b\u53f7\u3001\u4f7f\u7528\u573a\u666f\uff0c\u6269\u5c55\u81f3100+\u5b57\u7b26"})
    elif title_len > 200:
        score -= 5
        suggestions.append({"priority": "low", "area": "\u6807\u9898",
            "issue": f"\u6807\u9898\u8fc7\u957f\uff08{title_len}\u5b57\u7b26\uff09\uff0c\u8d85\u8fc7200\u5b57\u7b26\u53ef\u80fd\u88ab\u622a\u65ad",
            "action": "\u7cbe\u7b80\u81f3200\u5b57\u7b26\u4ee5\u5185\uff0c\u4fdd\u7559\u6838\u5fc3\u5173\u952e\u8bcd"})
    else:
        suggestions.append({"priority": "ok", "area": "\u6807\u9898",
            "issue": f"\u6807\u9898\u957f\u5ea6\u5408\u9002\uff08{title_len}\u5b57\u7b26\uff09", "action": "\u4fdd\u6301\u73b0\u72b6"})

    bullets = product.get("feature_bullets") or []
    bc = len(bullets)
    if bc < 3:
        score -= 15
        suggestions.append({"priority": "critical", "area": "Bullet Points",
            "issue": f"\u6838\u5fc3\u5356\u70b9\u53ea\u6709{bc}\u6761\uff0c\u5efa\u8bae\u81f3\u5c115\u6761",
            "action": "\u8865\u5145\u5356\u70b9\uff0c\u7a81\u51fa\u6750\u8d28\u3001\u529f\u80fd\u3001\u9002\u7528\u573a\u666f\u3001\u4fdd\u4fee\u7b49"})
    elif bc < 5:
        score -= 8
        suggestions.append({"priority": "high", "area": "Bullet Points",
            "issue": f"\u6838\u5fc3\u5356\u70b9{bc}\u6761\uff0c\u672a\u8fbe\u6700\u4f515\u6761",
            "action": "\u589e\u52a0\u52305\u6761\uff0c\u6bcf\u6761100\u5b57\u7b26\u4ee5\u4e0a"})
    else:
        suggestions.append({"priority": "ok", "area": "Bullet Points",
            "issue": f"Bullet Points\u6570\u91cf\u5145\u8db3\uff08{bc}\u6761\uff09", "action": "\u4fdd\u6301\u73b0\u72b6"})

    img_count = product.get("img_count", 0)
    if img_count < 4:
        score -= 15
        suggestions.append({"priority": "critical", "area": "\u4e3b\u56fe/\u526f\u56fe",
            "issue": f"\u56fe\u7247\u53ea\u6709{img_count}\u5f20\uff0c\u4e25\u91cd\u4e0d\u8db3",
            "action": "\u4e0a\u4f20\u81f3\u5c717\u5f20\u56fe\uff1a\u4e3b\u56fe\u767d\u5e95+\u751f\u6d3b\u573a\u666f+\u5c3a\u5bf8\u5bf9\u6bd4+\u7ec6\u8282\u56fe+\u5305\u88c5\u56fe"})
    elif img_count < 7:
        score -= 8
        suggestions.append({"priority": "high", "area": "\u4e3b\u56fe/\u526f\u56fe",
            "issue": f"\u56fe\u7247{img_count}\u5f20\uff0c\u672a\u8fbe\u6700\u4f517\u5f20",
            "action": "\u8865\u5145\u81f37\u5f20\uff0c\u5305\u62ec\u4f7f\u7528\u573a\u666f\u548c\u4ea7\u54c1\u7ec6\u8282"})
    else:
        suggestions.append({"priority": "ok", "area": "\u4e3b\u56fe/\u526f\u56fe",
            "issue": f"\u56fe\u7247\u6570\u91cf\u5145\u8db3\uff08{img_count}\u5f20\uff09", "action": "\u4fdd\u6301\u73b0\u72b6"})

    rating = product.get("rating") or 0
    if rating < 3.5:
        score -= 20
        suggestions.append({"priority": "critical", "area": "\u8bc4\u5206",
            "issue": f"\u8bc4\u5206\u504f\u4f4e\uff08{rating}\u661f\uff09\uff0c\u4e25\u91cd\u5f71\u54cd\u8f6c\u5316",
            "action": "\u5206\u6790\u5dee\u8bc4\u539f\u56e0\uff0c\u6539\u8fdb\u4ea7\u54c1\u8d28\u91cf\uff0c\u901a\u8fc7\u90ae\u4ef6\u8bf7\u6c42\u597d\u8bc4"})
    elif rating < 4.0:
        score -= 10
        suggestions.append({"priority": "high", "area": "\u8bc4\u5206",
            "issue": f"\u8bc4\u5206{rating}\u661f\uff0c\u4f4e\u4e8e4.0\u7ade\u4e89\u529b\u5f31",
            "action": "\u4e3b\u52a8\u8ddf\u8fdb\u5dee\u8bc4\uff0c\u6539\u5584\u552e\u540e\u4f53\u9a8c"})
    elif rating < 4.5:
        score -= 3
        suggestions.append({"priority": "medium", "area": "\u8bc4\u5206",
            "issue": f"\u8bc4\u5206{rating}\u661f\uff0c\u8fd8\u6709\u63d0\u5347\u7a7a\u95f4",
            "action": "\u7ee7\u7eed\u7ef4\u6301\u9ad8\u8d28\u91cf\u552e\u540e"})
    else:
        suggestions.append({"priority": "ok", "area": "\u8bc4\u5206",
            "issue": f"\u8bc4\u5206\u4f18\u79c0\uff08{rating}\u661f\uff09", "action": "\u4fdd\u6301\u73b0\u72b6"})

    review_count = product.get("review_count") or 0
    if review_count < 10:
        score -= 10
        suggestions.append({"priority": "critical", "area": "\u8bc4\u8bba\u6570",
            "issue": f"\u8bc4\u8bba\u6570\u8fc7\u5c11\uff08{review_count}\u6761\uff09\uff0c\u65b0\u54c1\u4fe1\u4efb\u5ea6\u4e0d\u8db3",
            "action": "\u901a\u8fc7Vine\u8ba1\u5212\u6216\u90ae\u4ef6\u7d22\u8bc4\u79ef\u累\u65e9\u671f\u8bc4\u8bba"})
    elif review_count < 50:
        score -= 5
        suggestions.append({"priority": "high", "area": "\u8bc4\u8bba\u6570",
            "issue": f"\u8bc4\u8bba\u6570{review_count}\u6761\uff0c\u504f\u5c11",
            "action": "\u52a0\u5f3a\u7d22\u8bc4\uff0c\u76ee\u680750\u6761\u4ee5\u4e0a"})
    else:
        suggestions.append({"priority": "ok", "area": "\u8bc4\u8bba\u6570",
            "issue": f"\u8bc4\u8bba\u6570\u5145\u8db3\uff08{review_count}\u6761\uff09", "action": "\u4fdd\u6301\u73b0\u72b6"})

    is_fba = product.get("is_fba", False)
    if not is_fba:
        score -= 8
        suggestions.append({"priority": "high", "area": "\u914d\u9001\u65b9\u5f0f",
            "issue": "\u975eFBA\u53d1\u8d27\uff0c\u5931\u53bbPrime\u5fbd\u7ae0\u7ade\u4e89\u529b",
            "action": "\u5207\u6362\u4e3aFBA\uff0c\u83b7\u5f97Prime\u8d44\u683c\uff0c\u63d0\u5347\u8f6c\u5316\u7387"})
    else:
        suggestions.append({"priority": "ok", "area": "\u914d\u9001\u65b9\u5f0f",
            "issue": "FBA\u53d1\u8d27\uff0c\u62e5\u6709Prime\u5fbd\u7ae0", "action": "\u4fdd\u6301FBA"})

    if comp_prices:
        my_price = product.get("current_price")
        if my_price:
            avg_comp = sum(comp_prices) / len(comp_prices)
            if my_price > avg_comp * 1.2:
                score -= 8
                suggestions.append({"priority": "medium", "area": "\u5b9a\u4ef7",
                    "issue": f"\u4ef7\u683c${my_price:.2f}\u6bd4\u7ade\u5bf9\u5747\u4ef7${avg_comp:.2f}\u9ad8\u51fa{(my_price/avg_comp-1)*100:.0f}%",
                    "action": "\u8bc4\u4f30\u662f\u5426\u6709\u5dee\u5f02\u5316\u4f18\u52bf\u652f\u6491\u6ea2\u4ef7\uff0c\u5426\u5219\u8003\u8651\u8c03\u6574\u5b9a\u4ef7"})
            elif my_price < avg_comp * 0.7:
                score -= 3
                suggestions.append({"priority": "low", "area": "\u5b9a\u4ef7",
                    "issue": f"\u4ef7\u683c${my_price:.2f}\u660e\u663e\u4f4e\u4e8e\u7ade\u5bf9\u5747\u4ef7${avg_comp:.2f}",
                    "action": "\u4f4e\u4ef7\u5438\u91cf\u53ef\u63a5\u53d7\uff0c\u4f46\u6ce8\u610f\u5229\u6da6\u7a7a\u95f4"})
            else:
                suggestions.append({"priority": "ok", "area": "\u5b9a\u4ef7",
                    "issue": f"\u4ef7\u683c${my_price:.2f}\u4e0e\u7ade\u5bf9\u5747\u4ef7${avg_comp:.2f}\u76f8\u8fd1\uff0c\u6709\u7ade\u4e89\u529b",
                    "action": "\u4fdd\u6301\u73b0\u72b6"})

    qa = product.get("answered_questions") or 0
    if qa < 5:
        score -= 5
        suggestions.append({"priority": "medium", "area": "Q&A",
            "issue": f"\u95ee\u7b54\u53ea\u6709{qa}\u6761\uff0c\u4e70\u5bb6\u7591\u8651\u672a\u5f97\u5230\u89e3\u7b54",
            "action": "\u4e3b\u52a8\u63d0\u4ea4\u5e38\u89c1\u95ee\u9898Q&A\uff0c\u6d88\u9664\u4e70\u5bb6\u987e\u8651"})
    else:
        suggestions.append({"priority": "ok", "area": "Q&A",
            "issue": f"Q&A {qa}\u6761\uff0c\u8986\u76d6\u4e70\u5bb6\u5e38\u89c1\u95ee\u9898", "action": "\u4fdd\u6301\u73b0\u72b6"})

    score = max(0, min(100, score))
    return {"score": score, "suggestions": suggestions}
