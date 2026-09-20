from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.llm import LLMError, ask_llm, extract_requirements, generate_response
from app.products import PRODUCTS, search_products
from app.recommendations import recommend_products
from app.schemas import ChatRequest, ChatResponse


app = FastAPI(
    title="SportsBuddy API",
    description="Sports shop recommendation chatbot API",
    version="1.0.0",
)

# Allow the local Vite dev server to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# How many ranked products to ground the final LLM response in / return to
# the caller, instead of dumping the entire catalogue into the prompt.
MAX_PRODUCTS_IN_RESPONSE = 5


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "SportsBuddy API is running"
    }


@app.get("/products")
def get_products() -> dict[str, Any]:
    return {
        "total": len(PRODUCTS),
        "products": PRODUCTS,
    }


@app.get("/products/search")
def get_product_search(
    query: str | None = Query(default=None),
    sport: str | None = Query(default=None),
    category: str | None = Query(default=None),
    subcategory: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    max_price: float | None = Query(default=None),
) -> dict[str, Any]:

    results = search_products(
        query=query,
        sport=sport,
        category=category,
        subcategory=subcategory,
        brand=brand,
        max_price=max_price,
    )

    ranked_results = recommend_products(results, query=query)

    return {
        "total": len(ranked_results),
        "products": ranked_results,
    }


@app.get("/test-llm")
def test_llm():
    try:
        response = ask_llm(
            "You are a sports shop assistant. "
            "Explain in one sentence why choosing the correct "
            "badminton racket matters."
        )
    except LLMError:
        raise HTTPException(
            status_code=503,
            detail="The AI assistant is currently unavailable. Please try again shortly.",
        )

    return {
        "response": response
    }


def _product_summary(product: dict[str, Any]) -> dict[str, Any]:
    """Trimmed fields sent to the LLM prompt, to keep it small and grounded."""
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "brand": product.get("brand"),
        "sport": product.get("sport"),
        "category": product.get("category"),
        "subcategory": product.get("subcategory"),
        "price": product.get("price"),
        "currency": product.get("currency"),
        "rating": product.get("rating"),
        "reviewCount": product.get("reviewCount"),
        "inStock": product.get("inStock"),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        requirements = extract_requirements(request.message)
    except LLMError:
        raise HTTPException(
            status_code=503,
            detail="The AI assistant is currently unavailable. Please try again shortly.",
        )

    # The extraction model can misclassify `intent` even when it correctly
    # filled in concrete filters (e.g. sport/brand/price). Trusting `intent`
    # alone in that case would skip search and let the final LLM answer
    # ungrounded, which risks it hallucinating products. So treat the
    # presence of any concrete filter as a product search too.
    has_filters = any(
        [
            requirements.sport,
            requirements.category,
            requirements.subcategory,
            requirements.brand,
            requirements.max_price is not None,
            requirements.query,
        ]
    )
    is_product_search = requirements.intent == "product_search" or has_filters

    if not is_product_search:
        try:
            reply = ask_llm(
                "You are SportsBuddy, a friendly sports shop assistant. "
                "Reply briefly and conversationally to this message. If it "
                "seems relevant, mention you can help find sporting goods "
                "such as shoes, rackets, balls, apparel and equipment.\n\n"
                f"User: {request.message}"
            )
        except LLMError:
            reply = (
                "Hi! I'm SportsBuddy. Tell me what sport or product you're "
                "looking for and I'll help you find it."
            )

        return ChatResponse(
            message=reply,
            requirements=requirements,
            products=[],
            total_matches=0,
        )

    try:
        matches = search_products(
            query=requirements.query,
            sport=requirements.sport,
            category=requirements.category,
            subcategory=requirements.subcategory,
            brand=requirements.brand,
            max_price=requirements.max_price,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Product search failed unexpectedly.")

    ranked = recommend_products(matches, query=requirements.query)
    top_products = ranked[:MAX_PRODUCTS_IN_RESPONSE]

    try:
        reply = generate_response(
            request.message,
            requirements,
            [_product_summary(product) for product in top_products],
        )
    except LLMError:
        if top_products:
            reply = (
                f"I found {len(ranked)} matching product(s), but couldn't "
                "generate a written summary right now."
            )
        else:
            reply = (
                "No matching products were found for those requirements. "
                "Try adjusting your budget, brand, or sport."
            )

    return ChatResponse(
        message=reply,
        requirements=requirements,
        products=top_products,
        total_matches=len(ranked),
    )
