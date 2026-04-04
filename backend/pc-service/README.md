# PC Service

A REST API service for managing PC products in the Kiemtra01 e-commerce system.

## Features

- **PC Product Management**: Create, read, update PC products with PC-specific fields
- **Catalog Search**: Search PC products by name, brand, or specs
- **PC-Specific Fields**: 
  - `form_factor`: desktop, gaming_pc, mini_pc, all_in_one, workstation
  - `cpu_cores`: Number of CPU cores
  - `gpu_vram_gb`: GPU VRAM in GB
  - `usb_ports`: Number of USB ports
  - `hdmi_ports`: Number of HDMI ports
- **Auto-sync Status**: Stock automatically syncs with product status (available/out_of_stock)
- **Inventory Management**: Check and deduct stock with race condition protection using `select_for_update()`

## API Endpoints

### Public Endpoints

- `GET /products` - List all PC products
- `GET /products/search?q=<query>` - Search PC products
- `GET /products/<product_id>` - Get PC product details
- `GET /health` - Health check
- `GET /info` - Service info

### Staff-Only Endpoints (via gateway @ `/pc/*`)

- `POST /products` - Create new PC product
- `PUT /products/<product_id>` - Update PC product

### Internal-Only Endpoints (via gateway @ `/pc/*`)

- `POST /inventory/check` - Check PC inventory stock
- `POST /inventory/deduct` - Deduct PC product stock

## Database

Uses PostgreSQL (shared with laptop-service and mobile-service):
- Database: `pc_db`
- Table: `pc_products`

## Environment Variables

```
DB_ENGINE=postgres
DB_NAME=pc_db
DB_USER=appuser
DB_PASSWORD=apppass
DB_HOST=postgres-db
DB_PORT=5432
DJANGO_DEBUG=1
```

## Data Model

### PcProduct

```python
{
    "id": "PC001",
    "name": "ASUS ROG Strix GA15DK",
    "category": "pc",
    "brand": "ASUS",
    "specs": "Intel Core i9-12900K, RTX 4090, ...",
    "price": 89990000,  # in VND
    "stock": 100,
    "image": "/assets/pc-asus-rog-strix-ga15dk.png",
    "form_factor": "gaming_pc",
    "cpu_cores": 16,
    "gpu_vram_gb": 24,
    "usb_ports": 8,
    "hdmi_ports": 2,
    "status": "available",  # auto-synced based on stock
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

## Build & Run

### Docker

```bash
# Build and start all services
docker compose up --build -d

# Run migrations
docker compose exec pc-service python manage.py migrate

# Create superuser (optional)
docker compose exec pc-service python manage.py createsuperuser
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database
export DB_ENGINE=sqlite

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## Integration Points

- **Gateway**: Forwards `/pc/*` requests with role-based access control
- **Catalog Search**: Gateway aggregates PC search results with laptop/mobile results
- **Order Service**: Calls PC inventory endpoints to check/deduct stock
- **AI Service**: Can recommend PC products based on context

## Race Condition Protection

All inventory operations use Django's `select_for_update()` to prevent race conditions:

```python
with transaction.atomic():
    product = PcProduct.objects.select_for_update().get(id=product_id)
    product.stock -= quantity
    product.save()
```

This ensures inventory is consistent even under high concurrent load.

## Status Auto-sync

Product status is automatically updated based on stock level:
- `stock > 0` → `status = "available"`
- `stock <= 0` → `status = "out_of_stock"`

This happens in the model's `save()` method.
