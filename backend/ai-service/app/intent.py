import re
from typing import Dict


def parse_intent(user_input: str) -> Dict[str, str]:
    """Simple intent parser for product references and action hints."""
    text = user_input.lower()
    match = re.search(r"\b((?:pc\d{3})|(?:[lm]\d{3}))\b", text)
    product_id = match.group(1).upper() if match else None

    return {
        "raw": user_input,
        "product_id": product_id,
        "intent": "checkout" if ("mua" in text or "thanh toan" in text or "thanh toán" in text) else "browse",
    }
