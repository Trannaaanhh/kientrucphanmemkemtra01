# Kiemtra01 Backend README

Backend cua Kiemtra01 duoc xay dung theo mo hinh microservices, trong do gateway la diem vao duy nhat cho client.

## Kien truc nhanh

Core services:
- gateway-service: auth + route request
- customer-service: catalog search va cart flow cho customer
- staff-service: quan ly san pham, audit, import asset
- laptop-service: catalog laptop
- mobile-service: catalog mobile
- pc-service: catalog pc (co field dac thu PC)
- inventory-service: ton kho
- order-service: tao don
- payment-service: thanh toan
- cart-service: gio hang
- ai-service: intent + recommendation + hybrid RAG + memory
- behavior-service: user behavior ingestion + segment prediction
- kb-service: knowledge base CRUD + retrieval ranking

Databases:
- MySQL: customer-service, staff-service
- PostgreSQL: laptop-service, mobile-service, pc-service, inventory-service, order-service, payment-service
- Redis: cart-service

## Chay nhanh

Tu thu muc backend:

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```

Dung he thong:

```bash
docker compose down
```

## Endpoint quan trong

Auth:
- POST /auth/customer/login
- POST /auth/staff/login

Catalog:
- GET /catalog/search?q=...&category=all|laptop|mobile|pc
- GET /pc/products

Staff:
- GET /staff/products?category=all|laptop|mobile|pc
- POST /staff/products
- PUT /staff/products/{product_id}

AI:
- POST /ai/chat
- GET /ai/history (staff)
- GET /ai/kb (staff)
- GET /ai/kb/debug?query=... (staff)

KB + Behavior:
- GET /kb/health
- GET /kb/search?query=...&top_k=3
- POST /behavior/events
- POST /behavior/predict

## Tai khoan demo

- Customer: customer@example.com / customer123
- Staff: staff@example.com / staff123

## Ghi chu van hanh

- Neu thay doi code service: docker compose up --build -d
- Neu thay doi model Django: tao migration va migrate trong tung service
- Seed data danh muc da theo co che idempotent (bo sung theo ID thieu)

## Tai lieu lien quan

Huong dan tong quan du an:
- ../doc/PROJECT_GUIDE.md

Huong dan deploy/van hanh:
- ../doc/DEPLOYMENT_RUNBOOK.md
