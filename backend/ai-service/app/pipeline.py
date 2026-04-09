from app.behavior_client import predict_behavior
from app.intent import parse_intent
from app.llm import generate_response
from app.memory_store import set_last_products
from app.rag import retrieve_context
from app.recommend import recommend_products


def run_pipeline(user_input: str, user_id: str):
    intent = parse_intent(user_input)
    behavior = predict_behavior(
        user_id,
        {
            "category_hint": "",
            "query": user_input,
        },
    )
    # Recommendation-only mode: chat suggests products from DB; customer clicks buy in UI.
    products = recommend_products(intent, user_id=user_id)
    set_last_products(user_id, products)
    predicted_segment = behavior.get("predicted_segment", "general")
    context = retrieve_context(user_input, segment=predicted_segment)
    context["behavior_segment"] = predicted_segment
    response = generate_response(user_input, products, context)

    return {
        "action": "recommend",
        "products": products,
        "response": response,
        "context": context,
        "behavior": behavior,
        "buy_mode": "click_only",
    }
