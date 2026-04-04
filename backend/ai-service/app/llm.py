from typing import Dict, List
import re


def _extract_budget_text(user_input: str) -> str:
    text = user_input.lower()
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(tr|triệu|trieu|m)\b", text)
    if not match:
        return ""
    return f"{match.group(1).replace('.', ',')} triệu"


def generate_response(user_input: str, products: List[Dict], context: Dict) -> str:
    if not products:
        budget_text = _extract_budget_text(user_input)
        if budget_text:
            return (
                f"Hiện chưa có sản phẩm phù hợp trong mức ngân sách khoảng {budget_text}. "
                "Bạn có thể tăng ngân sách hoặc đổi nhu cầu (ví dụ: bỏ từ khóa gaming) để mình lọc lại."
            )
        return "Mình chưa tìm thấy sản phẩm phù hợp trong kho hiện có, bạn có thể mô tả rõ hơn nhu cầu không?"

    top = products[0]
    return (
        f"Mình gợi ý {len(products)} sản phẩm. Nổi bật: "
        f"{top.get('name')} giá {top.get('price')} VND. "
        "Bạn chọn sản phẩm trong bảng gợi ý và bấm 'Mua gợi ý' để thêm vào giỏ."
    )
