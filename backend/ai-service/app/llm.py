import re
from typing import Dict, List


def _extract_budget_text(user_input: str) -> str:
    text = user_input.lower()
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(tr|triệu|trieu|m)\b", text)
    if not match:
        return ""
    return f"{match.group(1).replace('.', ',')} triệu"


SEGMENT_STYLE = {
    "gaming": "Ưu tiên FPS ổn định, tản nhiệt tốt và khả năng nâng cấp.",
    "office": "Ưu tiên tính ổn định, pin tốt và trọng lượng gọn.",
    "design": "Ưu tiên màn hình tốt, GPU đủ mạnh và RAM lớn.",
    "general": "Ưu tiên cân bằng hiệu năng, giá và độ bền.",
}


def _format_doc_hints(context: Dict) -> str:
    docs = context.get("documents", []) if isinstance(context, dict) else []
    if not docs:
        return ""

    hints: List[str] = []
    for doc in docs[:2]:
        title = str(doc.get("title", "")).strip()
        text = str(doc.get("text", "")).strip()
        if not title or not text:
            continue
        short_text = text[:130].rstrip()
        if len(text) > 130:
            short_text += "..."
        hints.append(f"- {title}: {short_text}")
    return "\n".join(hints)


def _build_consulting_prompt(user_input: str, products: List[Dict], context: Dict) -> str:
    segment = str(context.get("behavior_segment") or context.get("segment") or "general")
    style = SEGMENT_STYLE.get(segment, SEGMENT_STYLE["general"])
    docs = _format_doc_hints(context)
    product_lines = [
        f"- {p.get('name', 'San pham')}: {p.get('price', 0)} VND"
        for p in products[:3]
    ]

    return (
        "You are an ecommerce consultant.\n"
        f"User segment: {segment}\n"
        f"Guidance: {style}\n"
        f"User question: {user_input}\n"
        "Top products:\n"
        + ("\n".join(product_lines) if product_lines else "- Chua co san pham phu hop")
        + "\n"
        + (f"Knowledge snippets:\n{docs}\n" if docs else "")
        + "Answer in Vietnamese with practical buying advice."
    )


def generate_response(user_input: str, products: List[Dict], context: Dict) -> str:
    segment = str(context.get("behavior_segment") or context.get("segment") or "general")
    style_hint = SEGMENT_STYLE.get(segment, SEGMENT_STYLE["general"])
    docs_hint = _format_doc_hints(context)
    _ = _build_consulting_prompt(user_input, products, context)

    if not products:
        budget_text = _extract_budget_text(user_input)
        if budget_text:
            return (
                f"Hiện chưa có sản phẩm phù hợp trong mức ngân sách khoảng {budget_text}. "
                f"Theo hồ sơ hiện tại: {style_hint} "
                "Bạn có thể tăng ngân sách hoặc đổi nhu cầu (ví dụ: giảm yêu cầu gaming) để mình lọc lại."
            )
        return "Mình chưa tìm thấy sản phẩm phù hợp trong kho hiện có, bạn có thể mô tả rõ hơn nhu cầu không?"

    top = products[0]
    second = products[1] if len(products) > 1 else None
    knowledge_line = ""
    if docs_hint:
        first_hint = docs_hint.splitlines()[0].replace("- ", "")
        knowledge_line = f"\nTham chiếu tri thức: {first_hint}."

    compare_line = ""
    if second:
        compare_line = (
            f"\nBạn có thể so sánh thêm với {second.get('name')} ({second.get('price')} VND) "
            "để chọn cấu hình phù hợp hơn."
        )

    return (
        f"Mình gợi ý {len(products)} sản phẩm theo hướng {segment}. "
        f"Nổi bật: {top.get('name')} giá {top.get('price')} VND. "
        f"Tư vấn nhanh: {style_hint}"
        f"{knowledge_line}"
        f"{compare_line}"
        "\nBạn có thể bấm 'Mua gợi ý' để thêm sản phẩm vào giỏ."
    )
