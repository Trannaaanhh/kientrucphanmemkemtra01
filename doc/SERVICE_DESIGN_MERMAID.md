# SERVICE DESIGN (MERMAID)

Tai lieu nay mo ta thiet ke tong quan cho tung service backend cua Kiemtra01.

Ghi chu:
- So do la thiet ke muc he thong (high-level class design), khong phai UML implementation 1:1.
- Ten class/doi tuong duoc dat theo code hien tai de de doi chieu.

## 1) gateway-service

Chuc nang chinh:
- Auth customer/staff
- Route/proxy request den service nghiep vu
- Tong hop catalog search
- Route rieng cho PC endpoint

```mermaid
classDiagram
class RootView
class HealthView
class ServiceInfoView
class CustomerLoginView
class StaffLoginView
class CatalogSearchView
class CartCreateView
class CartAddView
class CartGetView
class CustomerCheckoutView
class StaffAddProductView
class StaffUpdateProductView
class StaffImportAssetView
class InventoryProxyView
class InventoryCheckProxyView
class OrderProxyView
class PaymentProxyView
class PaymentCreateProxyView
class PcProductView
class PcProductDetailView
class PcInventoryCheckView
class PcInventoryDeductView
class JwtAuthUtils {
  +build_token()
  +decode_token()
  +require_role()
}
CatalogSearchView --> JwtAuthUtils
StaffAddProductView --> JwtAuthUtils
StaffUpdateProductView --> JwtAuthUtils
PcProductDetailView --> JwtAuthUtils
```

## 2) customer-service

Chuc nang chinh:
- Customer login
- Catalog search (all|laptop|mobile|pc)
- Quan ly cart customer
- Checkout customer

```mermaid
classDiagram
class HealthView
class ServiceInfoView
class CustomerLoginView
class CatalogSearchView
class CartCreateView
class CartAddView
class CartGetView
class CartClearView
class CustomerCheckoutView
class JwtAuthUtils {
  +build_token()
  +decode_token()
  +require_role()
}
class CartMemoryStore {
  +CARTS
}
CustomerLoginView --> JwtAuthUtils
CatalogSearchView --> JwtAuthUtils
CartAddView --> CartMemoryStore
CartGetView --> CartMemoryStore
CartClearView --> CartMemoryStore
CustomerCheckoutView --> JwtAuthUtils
CustomerCheckoutView --> CartMemoryStore
```

## 3) staff-service

Chuc nang chinh:
- Staff login
- Quan ly san pham cho laptop/mobile/pc
- Import asset image
- Ghi va xem audit log

```mermaid
classDiagram
class HealthView
class ServiceInfoView
class StaffLoginView
class StaffAddProductView
class StaffUpdateProductView
class StaffImportAssetView
class StaffAuditAddView
class StaffAuditUpdateView
class StaffAuditListView
class JwtAuthUtils {
  +build_token()
  +decode_token()
  +require_role()
}
class AuditLogStore {
  +AUDIT_LOGS
}
StaffLoginView --> JwtAuthUtils
StaffAddProductView --> JwtAuthUtils
StaffUpdateProductView --> JwtAuthUtils
StaffImportAssetView --> JwtAuthUtils
StaffAuditAddView --> AuditLogStore
StaffAuditUpdateView --> AuditLogStore
StaffAuditListView --> AuditLogStore
```

## 4) laptop-service

Chuc nang chinh:
- CRUD san pham laptop
- Search laptop
- Seed du lieu idempotent

```mermaid
classDiagram
class LaptopProduct {
  +id
  +name
  +category
  +brand
  +specs
  +price
  +stock
  +image
  +to_dict()
}
class HealthView
class ServiceInfoView
class LaptopProductListCreateView
class LaptopProductUpdateView
class LaptopProductSearchView
class LaptopSeed {
  +SEED_PRODUCTS
  +ensure_seed_data()
  +next_product_id()
}
LaptopProductListCreateView --> LaptopProduct
LaptopProductUpdateView --> LaptopProduct
LaptopProductSearchView --> LaptopProduct
LaptopProductListCreateView --> LaptopSeed
LaptopProductUpdateView --> LaptopSeed
LaptopProductSearchView --> LaptopSeed
```

## 5) mobile-service

Chuc nang chinh:
- CRUD san pham mobile
- Search mobile
- Seed du lieu idempotent

```mermaid
classDiagram
class MobileProduct {
  +id
  +name
  +category
  +brand
  +specs
  +price
  +stock
  +image
  +to_dict()
}
class HealthView
class ServiceInfoView
class MobileProductListCreateView
class MobileProductUpdateView
class MobileProductSearchView
class MobileSeed {
  +SEED_PRODUCTS
  +ensure_seed_data()
  +next_product_id()
}
MobileProductListCreateView --> MobileProduct
MobileProductUpdateView --> MobileProduct
MobileProductSearchView --> MobileProduct
MobileProductListCreateView --> MobileSeed
MobileProductUpdateView --> MobileSeed
MobileProductSearchView --> MobileSeed
```

## 6) pc-service

Chuc nang chinh:
- CRUD san pham PC
- Search PC
- Inventory check/deduct an toan dong thoi
- Auto-sync status theo stock

```mermaid
classDiagram
class PcProduct {
  +id
  +name
  +category
  +brand
  +specs
  +price
  +stock
  +image
  +form_factor
  +cpu_cores
  +gpu_vram_gb
  +usb_ports
  +hdmi_ports
  +status
  +save()
  +to_dict()
}
class HealthView
class ServiceInfoView
class PcProductListCreateView
class PcProductUpdateView
class PcProductSearchView
class InventoryCheckView
class InventoryDeductView
class PcSeed {
  +SEED_PRODUCTS
  +ensure_seed_data()
  +next_product_id()
}
PcProductListCreateView --> PcProduct
PcProductUpdateView --> PcProduct
PcProductSearchView --> PcProduct
InventoryCheckView --> PcProduct
InventoryDeductView --> PcProduct
PcProductListCreateView --> PcSeed
```

## 7) inventory-service

Chuc nang chinh:
- Quan ly ton kho tong quat
- Check stock va deduct stock
- API listing/detail ton kho

```mermaid
classDiagram
class Stock {
  +product_id
  +quantity
  +updated_at
}
class InventoryCheckView
class InventoryDeductView
class InventoryListView
class InventoryDetailView
InventoryCheckView --> Stock
InventoryDeductView --> Stock
InventoryListView --> Stock
InventoryDetailView --> Stock
```

## 8) cart-service

Chuc nang chinh:
- Quan ly gio hang theo user/session
- Add/update/remove item
- Doc gio hang

```mermaid
classDiagram
class CartGetView
class CartAddView
class CartUpdateView
class CartRemoveView
class CartRedisRepository {
  +get_cart()
  +set_cart()
  +remove_item()
}
CartGetView --> CartRedisRepository
CartAddView --> CartRedisRepository
CartUpdateView --> CartRedisRepository
CartRemoveView --> CartRedisRepository
```

## 9) order-service

Chuc nang chinh:
- Tao don hang
- Checkout flow
- Luu order + order items

```mermaid
classDiagram
class Order {
  +id
  +customer_id
  +total_amount
  +status
  +created_at
}
class OrderItem {
  +id
  +order
  +product_id
  +quantity
  +unit_price
}
class OrderCreateView
class OrderCheckoutView
class OrderDetailView
OrderCreateView --> Order
OrderCreateView --> OrderItem
OrderCheckoutView --> Order
OrderCheckoutView --> OrderItem
OrderDetailView --> Order
OrderDetailView --> OrderItem
```

## 10) payment-service

Chuc nang chinh:
- Tao giao dich thanh toan
- Confirm thanh toan
- Listing lich su payment

```mermaid
classDiagram
class Payment {
  +id
  +order_id
  +transaction_id
  +amount
  +status
  +created_at
}
class PaymentListView
class PaymentCreateView
class PaymentConfirmView
PaymentListView --> Payment
PaymentCreateView --> Payment
PaymentConfirmView --> Payment
```

## 11) ai-service

Chuc nang chinh:
- Chat recommendation
- Parse intent
- Recommend san pham tu catalog live
- Hybrid RAG (KB + live catalog summary)
- Memory history theo user
- Staff API de xem KB va debug RAG

```mermaid
classDiagram
class FastAPIApp {
  +health()
  +chat()
  +history()
  +history_by_user()
  +kb()
  +kb_debug()
}
class Pipeline {
  +run_pipeline()
}
class Intent {
  +parse_intent()
}
class Recommend {
  +recommend_products()
}
class Rag {
  +retrieve_context()
  +get_kb_documents()
  +build_rag_debug()
}
class LLM {
  +generate_response()
}
class MemoryStore {
  +append_history()
  +get_user_history()
  +list_histories()
  +set_last_products()
}
FastAPIApp --> Pipeline
Pipeline --> Intent
Pipeline --> Recommend
Pipeline --> Rag
Pipeline --> LLM
Pipeline --> MemoryStore
FastAPIApp --> MemoryStore
FastAPIApp --> Rag
```

## 12) Service relation overview

```mermaid
flowchart LR
  FE[Frontend]
  GW[gateway-service]
  CUS[customer-service]
  STF[staff-service]
  LAP[laptop-service]
  MOB[mobile-service]
  PC[pc-service]
  INV[inventory-service]
  CART[cart-service]
  ORD[order-service]
  PAY[payment-service]
  AI[ai-service]

  FE --> GW
  GW --> CUS
  GW --> STF
  GW --> LAP
  GW --> MOB
  GW --> PC
  GW --> INV
  GW --> ORD
  GW --> PAY
  GW --> AI
  CUS --> LAP
  CUS --> MOB
  CUS --> PC
  STF --> LAP
  STF --> MOB
  STF --> PC
  AI --> LAP
  AI --> MOB
  AI --> PC
  ORD --> INV
  ORD --> PAY
```
