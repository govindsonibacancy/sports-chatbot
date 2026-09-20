import json
from typing import Any

import ollama
from pydantic import ValidationError

from app.products import KNOWN_BRANDS, KNOWN_CATEGORIES, KNOWN_SPORTS
from app.schemas import ChatRequirements

MODEL = "llama3.2:3b"


class LLMError(Exception):
    """Raised when the local Ollama LLM cannot be reached or fails to respond."""


def ask_llm(prompt: str) -> str:
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
    except Exception as error:
        raise LLMError(f"Failed to reach the LLM: {error}") from error

    return response["message"]["content"]


EXTRACTION_SYSTEM_PROMPT = (
    "You are the requirement-extraction module for SportsBuddy, a sports shop "
    "chatbot. Read the user's message and extract structured shopping "
    "requirements as JSON matching the required schema.\n\n"
    f"Known sports: {', '.join(KNOWN_SPORTS)}\n"
    f"Known categories: {', '.join(KNOWN_CATEGORIES)}\n"
    f"Known brands: {', '.join(KNOWN_BRANDS)}\n\n"
    "Rules:\n"
    "- intent is \"product_search\" when the user is looking for, asking about, "
    "or comparing products.\n"
    "- intent is \"general_question\" for greetings, small talk, or questions "
    "about the shop itself rather than a specific product.\n"
    "- intent is \"unknown\" only if the message truly cannot be classified.\n"
    "- Only set sport, category, or brand to a value from the known lists "
    "above, spelled exactly as shown there. Use null if nothing matches.\n"
    "- subcategory may be a short best-effort guess (e.g. \"Rackets\") or null.\n"
    "- Only set max_price if the user states a numeric budget; strip any "
    "currency symbols or words and return a plain number.\n"
    "- user_skill_level should capture a stated skill level (e.g. "
    "\"beginner\", \"intermediate\", \"advanced\") if mentioned, otherwise null.\n"
    "- Never invent a sport, category, or brand that is not implied by the "
    "message."
)


def extract_requirements(message: str) -> ChatRequirements:
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            format=ChatRequirements.model_json_schema(),
        )
    except Exception as error:
        raise LLMError(f"Failed to reach the LLM for extraction: {error}") from error

    content = response["message"]["content"]

    try:
        requirements = ChatRequirements.model_validate_json(content)
    except (ValidationError, ValueError):
        # Malformed/unparseable model output: fall back to a safe default
        # instead of guessing at partial data.
        return ChatRequirements(intent="unknown", query=message)

    return _normalize_requirements(requirements)


_KNOWN_BRANDS_LOWER = {brand.lower(): brand for brand in KNOWN_BRANDS}
_KNOWN_CATEGORIES_LOWER = {category.lower() for category in KNOWN_CATEGORIES}
_NULL_STRINGS = {"null", "none", "n/a", ""}

_STRING_FIELDS = (
    "query",
    "sport",
    "category",
    "subcategory",
    "brand",
    "user_skill_level",
)


def _clean_str(value: str | None) -> str | None:
    """The model occasionally returns the literal string "null" instead of
    JSON null. Treat that (and blank/"none") as no value."""
    if value is None:
        return None
    cleaned = value.strip()
    return None if cleaned.lower() in _NULL_STRINGS else cleaned


def _normalize_requirements(requirements: ChatRequirements) -> ChatRequirements:
    """Correct a few known shapes of small-model extraction error so the
    backend's search stays reliable, without changing anything the model
    got right."""
    for field in _STRING_FIELDS:
        setattr(requirements, field, _clean_str(getattr(requirements, field)))

    # A known brand name sometimes lands in subcategory/category/query
    # instead of brand.
    if not requirements.brand:
        for field in ("subcategory", "category", "query"):
            value = getattr(requirements, field)
            if value and value.lower() in _KNOWN_BRANDS_LOWER:
                requirements.brand = _KNOWN_BRANDS_LOWER[value.lower()]
                setattr(requirements, field, None)
                break

    # `category` must be one of the catalogue's actual categories; if the
    # model put a subcategory-shaped value there instead (e.g. "Rackets"),
    # shift it down rather than filtering on a category that can't match.
    if requirements.category and requirements.category.lower() not in _KNOWN_CATEGORIES_LOWER:
        if not requirements.subcategory:
            requirements.subcategory = requirements.category
        requirements.category = None

    return requirements


def generate_response(
    message: str,
    requirements: ChatRequirements,
    products: list[dict[str, Any]],
) -> str:
    products_json = json.dumps(products, indent=2) if products else "[]"

    system_prompt = (
        "You are SportsBuddy, a friendly sports shop assistant.\n"
        "The JSON list below is the complete and only set of matching "
        "products from the shop's catalogue for this reply.\n\n"
        "Rules:\n"
        "- Use only the product data supplied below. Do not invent products, "
        "brands, prices, ratings, or specifications.\n"
        "- Do not mention or suggest any product or brand name that is not "
        "in the list, even as a general suggestion - if you don't have "
        "brand/product data for it here, don't name it.\n"
        "- If the list is empty, tell the user no matching products were "
        "found and suggest adjusting the budget, brand, or sport in general "
        "terms only - do not name specific alternative brands or products.\n"
        "- Keep the reply short and conversational (2-4 sentences).\n"
    )

    if requirements.user_skill_level:
        system_prompt += (
            f"- The user described their skill level as "
            f"\"{requirements.user_skill_level}\". You may reflect this in "
            "tone, but the catalogue has no skill-level data, so do not "
            "claim any product is or isn't suited to a skill level.\n"
        )

    system_prompt += f"\nMatching products (JSON):\n{products_json}"

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
        )
    except Exception as error:
        raise LLMError(f"Failed to reach the LLM for the final response: {error}") from error

    return response["message"]["content"]
