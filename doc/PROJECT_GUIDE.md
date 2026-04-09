# PROJECT GUIDE

## 1. Muc tieu du an

Kiemtra01 la he thong thuong mai dien tu theo mo hinh microservices.

Muc tieu chinh:
- Tach domain nghiep vu thanh service doc lap de de mo rong va bao tri.
- Dong bo phat trien frontend, backend va AI service.
- Chuan hoa van hanh bang Docker Compose.
- Dat nen tang cho catalog da danh muc (laptop, mobile, pc) va AI recommendation.

## 2. Tong quan workspace

Workspace duoc chia thanh 3 khoi:
- Assets: tai nguyen dung chung.
- backend: tat ca microservices va docker-compose.
- frontend: ung dung Vite + TypeScript.

Thu muc quan trong:
- backend/docker-compose.yml: khai bao ket noi toan bo service.
- backend/ai-service: intent + recommendation + hybrid RAG + memory.
- backend/*-service: moi service la mot Django/FastAPI project rieng theo domain.
- backend/db-init: script khoi tao CSDL MySQL/PostgreSQL.
- doc: tai lieu ky thuat.

## 3. Danh sach service backend

- gateway-service
- customer-service
- staff-service
- laptop-service
- mobile-service
- pc-service
- inventory-service
- cart-service
- order-service
- payment-service
- ai-service
- behavior-service
- kb-service

## 4. Kien truc va data flow

Luong tong quan:
1. Frontend gui request qua gateway (Nginx/API gateway).
2. Gateway route den service nghiep vu theo prefix.
3. Moi service tu quan ly logic va database.
4. AI service xu ly goi y san pham va context (hybrid RAG).

Database:
- MySQL: customer-service, staff-service
- PostgreSQL: laptop-service, mobile-service, pc-service, order-service, payment-service, inventory-service, behavior-service, kb-service
- Redis: cart-service

## 5. Chuc nang hien co

Catalog san pham:
- laptop-service
- mobile-service
- pc-service
- inventory-service

Nguoi dung va nhan su:
- customer-service
- staff-service

Gio hang va don hang:
- cart-service
- order-service
- payment-service

Gateway:
- auth customer/staff
- route catalog/category
- route pc endpoint

AI:
- parse intent
- recommendation tu catalog live
- hybrid RAG (KB + live catalog summary)
- memory lich su hoi thoai
- endpoint quan tri KB: /ai/kb va /ai/kb/debug (staff token)

Behavior + KB:
- behavior-service thu thap event va du doan segment
- kb-service quan ly tri thuc, rank tai lieu va phuc vu retrieval cho RAG

## 6. API chinh

Auth:
- POST /auth/customer/login
- POST /auth/staff/login

Catalog:
- GET /catalog/search?q=...&category=all|laptop|mobile|pc

PC qua gateway:
- GET /pc/products
- POST /pc/products (staff)
- PUT /pc/products/{product_id} (staff)

Staff:
- GET /staff/products?category=all|laptop|mobile|pc
- POST /staff/products
- PUT /staff/products/{product_id}

AI:
- POST /ai/chat
- GET /ai/history (staff)
- GET /ai/kb (staff)
- GET /ai/kb/debug?query=... (staff)

Behavior:
- POST /behavior/events
- POST /behavior/predict
- GET /behavior/profile/{user_id}

KB:
- GET /kb/documents
- GET /kb/search?query=...&top_k=3

## 7. Cach chay du an

Yeu cau:
- Da cai Docker va Docker Compose.

Khoi dong backend (tu backend):
1. docker compose up --build -d
2. docker compose ps
3. docker compose logs -f

Dung he thong:
- docker compose down

Chay frontend (tu frontend):
1. npm install
2. npm run dev
3. npm run build

## 8. Tai khoan demo

- Customer: customer@example.com / customer123
- Staff: staff@example.com / staff123

## 9. Luu y phat trien

- Khi thay doi code backend trong container, can build lai: docker compose up --build -d.
- Khi thay doi model Django, can tao migration va migrate dung service.
- Seed data da duoc thiet ke idempotent theo ID (chi bo sung ban ghi thieu).

## 10. Dinh huong mo rong

- Bo sung observability: logging tap trung, metrics, tracing.
- Bo sung bo test tich hop lien service.
- Cai tien ranker trong RAG bang embedding/vector database.
- Bo sung governance cho knowledge base (versioning va review workflow).

Tai lieu van hanh/deploy:
- DEPLOYMENT_RUNBOOK.md
