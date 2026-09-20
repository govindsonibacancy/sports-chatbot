import json
from pathlib import Path
from typing import Any


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sports-shop-products.json"
)


def load_products() -> list[dict[str, Any]]:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Failed to load product catalogue: {error}")
        return []

    # Supports either:
    # [
    #   {...},
    #   {...}
    # ]
    #
    # or:
    # {
    #   "products": [
    #       {...}
    #   ]
    # }
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return data.get("products", [])

    return []


PRODUCTS = load_products()

# Vocabulary of real values present in the catalogue, used to ground the
# LLM's structured extraction so it doesn't invent sports/categories/brands.
KNOWN_SPORTS = sorted({str(p["sport"]) for p in PRODUCTS if p.get("sport")})
KNOWN_CATEGORIES = sorted({str(p["category"]) for p in PRODUCTS if p.get("category")})
KNOWN_BRANDS = sorted({str(p["brand"]) for p in PRODUCTS if p.get("brand")})


def _safe_price(product: dict[str, Any]) -> float:
    try:
        return float(product.get("price", 0))
    except (TypeError, ValueError):
        return 0.0


def search_products(
    query: str | None = None,
    sport: str | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    brand: str | None = None,
    max_price: float | None = None,
) -> list[dict[str, Any]]:
    results = PRODUCTS

    if query:
        search_text = query.lower().strip()

        results = [
            product
            for product in results
            if search_text in str(product.get("name", "")).lower()
            or search_text in str(product.get("sport", "")).lower()
            or search_text in str(product.get("category", "")).lower()
            or search_text in str(product.get("subcategory", "")).lower()
            or search_text in str(product.get("brand", "")).lower()
            or search_text in str(product.get("description", "")).lower()
            or any(
                search_text in str(feature).lower()
                for feature in product.get("features", [])
            )
        ]

    if sport:
        results = [
            product
            for product in results
            if str(product.get("sport", "")).lower() == sport.lower()
        ]

    if category:
        results = [
            product
            for product in results
            if str(product.get("category", "")).lower() == category.lower()
        ]

    if subcategory:
        results = [
            product
            for product in results
            if str(product.get("subcategory", "")).lower()
            == subcategory.lower()
        ]

    if brand:
        results = [
            product
            for product in results
            if str(product.get("brand", "")).lower() == brand.lower()
        ]

    # NOTE: the current catalogue has no skill_level field, so that filter
    # is intentionally not supported yet. Re-add it here if the dataset is
    # ever extended with real skill-level data.

    if max_price is not None:
        results = [
            product
            for product in results
            if _safe_price(product) <= max_price
        ]

    return results