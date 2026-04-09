from app.models import KBDocument


DEFAULT_DOCUMENTS = [
    {
        "doc_id": "kb_001",
        "title": "Catalog overview",
        "content": (
            "He thong co 3 nhom danh muc chinh: laptop, mobile, pc. Moi nhom co endpoint products va products/search "
            "de tra cuu nhanh theo ten, hang va cau hinh."
        ),
        "tags": ["catalog", "laptop", "mobile", "pc"],
    },
    {
        "doc_id": "kb_002",
        "title": "Laptop cho sinh vien IT",
        "content": (
            "Laptop cho sinh vien IT nen uu tien CPU 4-8 core, RAM tu 16GB, SSD 512GB tro len, trong luong nhe va pin tot. "
            "Neu lap trinh va di hoc nhieu, chon 13-14 inch se tien loi hon."
        ),
        "tags": ["laptop", "student", "programming", "it"],
    },
    {
        "doc_id": "kb_003",
        "title": "PC gaming va workstation",
        "content": (
            "PC gaming can GPU rieng, nguon on dinh va tan nhiet tot. Workstation can uu tien CPU, RAM va do on dinh "
            "khi render, design, va xu ly du lieu."
        ),
        "tags": ["pc", "gaming", "workstation", "gpu", "cpu"],
    },
    {
        "doc_id": "kb_004",
        "title": "Shopping guidance",
        "content": (
            "Nguoi dung co the mo ta nhu cau theo ngan sach, thuong hieu, loai san pham. AI uu tien tra ve san pham co trong kho "
            "va phu hop bo loc gia."
        ),
        "tags": ["budget", "shopping", "recommendation"],
    },
    {
        "doc_id": "kb_005",
        "title": "Checkout and inventory note",
        "content": (
            "Khi checkout, he thong can tru ton kho theo tung category. PC su dung co che select_for_update de tranh race condition "
            "khi dat hang dong thoi."
        ),
        "tags": ["checkout", "inventory", "concurrency"],
    },
]


def seed_documents(session) -> int:
    existing_ids = {row[0] for row in session.query(KBDocument.doc_id).all()}
    inserted = 0
    for item in DEFAULT_DOCUMENTS:
        if item["doc_id"] in existing_ids:
            continue
        session.add(
            KBDocument(
                doc_id=item["doc_id"],
                title=item["title"],
                content=item["content"],
                tags=item.get("tags", []),
                embedding=[],
                source="seed",
            )
        )
        inserted += 1
    if inserted:
        session.commit()
    return inserted
