from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _score_product(product: dict[str, Any], query: str | None) -> float:
    score = 0.0

    score += _safe_float(product.get("rating")) * 10
    score += min(_safe_float(product.get("reviewCount")), 500) / 10

    if product.get("inStock"):
        score += 50
    else:
        score -= 100

    if product.get("isBestSeller"):
        score += 20

    if product.get("isNew"):
        score += 5

    price = _safe_float(product.get("price"))
    original_price = _safe_float(product.get("originalPrice"))
    if original_price > price > 0:
        score += 5

    if query:
        search_text = query.lower().strip()
        name = str(product.get("name", "")).lower()
        brand = str(product.get("brand", "")).lower()
        subcategory = str(product.get("subcategory", "")).lower()
        sport = str(product.get("sport", "")).lower()

        if search_text in name:
            score += 30
        elif (
            search_text in brand
            or search_text in subcategory
            or search_text in sport
        ):
            score += 15
        elif search_text in str(product.get("description", "")).lower() or any(
            search_text in str(feature).lower()
            for feature in product.get("features", [])
        ):
            score += 5

    return score


def recommend_products(
    products: list[dict[str, Any]],
    query: str | None = None,
) -> list[dict[str, Any]]:
    """Rank already-matching products; does not filter anything out."""
    return sorted(
        products,
        key=lambda product: _score_product(product, query),
        reverse=True,
    )
