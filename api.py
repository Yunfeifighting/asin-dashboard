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
    """Extract top search keywords from a product title."""
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
    """Rule-based listing quality score 0-100 with actionable suggestions."""
    score = 100
    suggestions = []
    comp_prices = comp_prices or []

    # Title
    title = product.get("title", "")
    tlen = len(title)
    if tlen < 80:
        score -= 15
        suggestions.append({
            "priority": "critical", "area": "Title",
            "issue": "Title too short (" + str(tlen) + " chars). Aim for 80-200.",
            "action": "Add keywords, model number, use case to reach 100+ chars.",
        })
    elif tlen > 200:
        score -= 5
        suggestions.append({
            "priority": "low", "area": "Title",
            "issue": "Title too long (" + str(tlen) + " chars), may be truncated.",
            "action": "Trim to under 200 chars, keep core keywords.",
        })
    else:
        suggestions.append({
            "priority": "ok", "area": "Title",
            "issue": "Title length is good (" + str(tlen) + " chars).",
            "action": "Maintain current title.",
        })

    # Bullets
    bc = len(product.get("feature_bullets") or [])
    if bc < 3:
        score -= 15
        suggestions.append({
            "priority": "critical", "area": "Bullet Points",
            "issue": "Only " + str(bc) + " bullet points. Need at least 5.",
            "action": "Add bullets covering material, function, warranty, use case.",
        })
    elif bc < 5:
        score -= 8
        suggestions.append({
            "priority": "high", "area": "Bullet Points",
            "issue": str(bc) + " bullets — below optimal 5.",
            "action": "Expand to 5 bullets, each 100+ chars.",
        })
    else:
        suggestions.append({
            "priority": "ok", "area": "Bullet Points",
            "issue": "Good bullet count (" + str(bc) + ").",
            "action": "Maintain current bullets.",
        })

    # Images
    imgs = product.get("img_count", 0)
    if imgs < 4:
        score -= 15
        suggestions.append({
            "priority": "critical", "area": "Images",
            "issue": "Only " + str(imgs) + " images — critically low.",
            "action": "Upload 7 images: white-bg main + lifestyle + size comparison + detail + packaging.",
        })
    elif imgs < 7:
        score -= 8
        suggestions.append({
            "priority": "high", "area": "Images",
            "issue": str(imgs) + " images — below optimal 7.",
            "action": "Add lifestyle and detail shots to reach 7.",
        })
    else:
        suggestions.append({
            "priority": "ok", "area": "Images",
            "issue": "Image count is good (" + str(imgs) + ").",
            "action": "Maintain current images.",
        })

    # Rating
    rating = product.get("rating") or 0
    if rating < 3.5:
        score -= 20
        suggestions.append({
            "priority": "critical", "area": "Rating",
            "issue": "Rating " + str(rating) + " stars — critically low, hurts conversion.",
            "action": "Analyze negative reviews, improve product, follow up with buyers.",
        })
    elif rating < 4.0:
        score -= 10
        suggestions.append({
            "priority": "high", "area": "Rating",
            "issue": "Rating " + str(rating) + " stars — below 4.0 competitive threshold.",
            "action": "Proactively address negative reviews, improve after-sales.",
        })
    elif rating < 4.5:
        score -= 3
        suggestions.append({
            "priority": "medium", "area": "Rating",
            "issue": "Rating " + str(rating) + " stars — room for improvement.",
            "action": "Maintain high quality customer service.",
        })
    else:
        suggestions.append({
            "priority": "ok", "area": "Rating",
            "issue": "Excellent rating (" + str(rating) + " stars).",
            "action": "Maintain current quality.",
        })

    # Reviews
    rv = product.get("review_count") or 0
    if rv < 10:
        score -= 10
        suggestions.append({
            "priority": "critical", "area": "Reviews",
            "issue": "Only " + str(rv) + " reviews — low buyer trust.",
            "action": "Use Vine program or email follow-up to build early reviews.",
        })
    elif rv < 50:
        score -= 5
        suggestions.append({
            "priority": "high", "area": "Reviews",
            "issue": str(rv) + " reviews — below 50 target.",
            "action": "Increase review solicitation, target 50+ reviews.",
        })
    else:
        suggestions.append({
            "priority": "ok", "area": "Reviews",
            "issue": "Good review count (" + str(rv) + ").",
            "action": "Maintain current approach.",
        })

    # FBA
    if not product.get("is_fba", False):
        score -= 8
        suggestions.append({
            "priority": "high", "area": "Fulfillment",
            "issue": "Not FBA — missing Prime badge, lower competitiveness.",
            "action": "Switch to FBA to gain Prime eligibility and boost conversion.",
        })
    else:
        suggestions.append({
            "priority": "ok", "area": "Fulfillment",
            "issue": "FBA with Prime badge.",
            "action": "Maintain FBA.",
        })

    # Price vs competitors
    if comp_prices:
        my_price = product.get("current_price")
        if my_price:
            avg_comp = sum(comp_prices) / len(comp_prices)
            pct = (my_price / avg_comp - 1) * 100
            if my_price > avg_comp * 1.2:
                score -= 8
                suggestions.append({
                    "priority": "medium", "area": "Pricing",
                    "issue": "Price $" + str(round(my_price, 2)) + " is " + str(round(pct)) + "% above competitor avg $" + str(round(avg_comp, 2)) + ".",
                    "action": "Verify differentiation justifies premium, else adjust price.",
                })
            elif my_price < avg_comp * 0.7:
                score -= 3
                suggestions.append({
                    "priority": "low", "area": "Pricing",
                    "issue": "Price $" + str(round(my_price, 2)) + " is well below competitor avg $" + str(round(avg_comp, 2)) + ".",
                    "action": "Low price drives volume but watch profit margin.",
                })
            else:
                suggestions.append({
                    "priority": "ok", "area": "Pricing",
                    "issue": "Price $" + str(round(my_price, 2)) + " is competitive vs avg $" + str(round(avg_comp, 2)) + ".",
                    "action": "Maintain current pricing.",
                })

    # Q&A
    qa = product.get("answered_questions") or 0
    if qa < 5:
        score -= 5
        suggestions.append({
            "priority": "medium", "area": "Q&A",
            "issue": "Only " + str(qa) + " answered questions — buyer concerns unaddressed.",
            "action": "Submit common Q&A to address buyer hesitations proactively.",
        })
    else:
        suggestions.append({
            "priority": "ok", "area": "Q&A",
            "issue": str(qa) + " Q&As covering common buyer questions.",
            "action": "Maintain current Q&A coverage.",
        })

    return {"score": max(0, min(100, score)), "suggestions": suggestions}
