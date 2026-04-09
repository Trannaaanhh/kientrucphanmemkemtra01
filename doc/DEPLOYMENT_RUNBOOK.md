# DEPLOYMENT RUNBOOK

## 1. Scope

Runbook nay dung de deploy va van hanh he thong e-commerce microservices (gateway + business services + AI/RAG services) tren Docker Compose.

## 2. Services in Production Stack

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

Infra:
- mysql-db
- postgres-db
- redis-db

## 3. Pre-deploy Checklist

1. Docker va Docker Compose da duoc cai.
2. Copy env template:
   - `cp backend/.env.example backend/.env`
3. Thay doi secrets trong `backend/.env`:
   - `JWT_SECRET`
   - `MYSQL_ROOT_PASSWORD`
   - `MYSQL_PASSWORD`
   - `POSTGRES_PASSWORD`
4. Xac nhan port 8080, 3306, 5432, 6379 chua bi chiem.

## 4. Deploy

Tu thu muc `backend`:

```bash
docker compose pull
docker compose up --build -d
docker compose ps
```

Kiem tra health:

```bash
docker compose ps
docker compose logs --tail=100 gateway-service ai-service behavior-service kb-service
```

## 5. Smoke Tests

```bash
curl http://localhost:8080/health
curl http://localhost:8080/ai/health
curl http://localhost:8080/behavior/health
curl http://localhost:8080/kb/health
```

Functional checks:

1. Dang nhap customer/staff.
2. Search catalog `category=pc|laptop|mobile`.
3. Chat endpoint `/ai/chat` tra ve recommendation + context.
4. Kiem tra KB search `/kb/search?query=...`.

## 6. Rolling Update

Deploy mot nhom service:

```bash
docker compose up --build -d ai-service behavior-service kb-service gateway-service
```

Rollback nhanh (ve image cu):

```bash
docker compose stop ai-service behavior-service kb-service gateway-service
docker compose up -d ai-service behavior-service kb-service gateway-service
```

## 7. Data and Recovery

Volumes:
- `mysql_data`
- `postgres_data`

Backup tham khao:

```bash
docker exec -t mysql-db mysqldump -uroot -p$MYSQL_ROOT_PASSWORD --all-databases > mysql_backup.sql
docker exec -t postgres-db pg_dumpall -U $POSTGRES_USER > postgres_backup.sql
```

## 8. Common Issues

1. New DB init script khong chay do volume cu:
   - Khoi tao DB thu cong trong container postgres hoac dung bootstrap logic cua service.
2. Code da doi nhung behavior khong doi:
   - Chay lai `docker compose up --build -d`.
3. Service start truoc DB:
   - Compose da co healthcheck + condition, cho den khi DB healthy.

## 9. Monitoring Basics

Theo doi:
- Latency `/ai/chat`
- Error rate cua `ai-service`, `behavior-service`, `kb-service`
- Resource usage `docker stats`
- Container restart count `docker compose ps`
