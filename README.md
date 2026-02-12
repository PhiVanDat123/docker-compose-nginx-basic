# Task Manager API — Multi-container + Nginx

API quản lý công việc chạy trên **3 container FastAPI** phía sau **Nginx load balancer**.

```
Client
  │
  ▼
Nginx :80  (round-robin)
  ├─► todo-api-1 :8000
  ├─► todo-api-2 :8000
  └─► todo-api-3 :8000
```

---

## Cấu trúc project

```
.
├── main.py                # FastAPI application (không đổi)
├── requirements.txt       # Python dependencies (không đổi)
├── Dockerfile             # Image gốc (không đổi)
├── docker-compose.yml     # 3 app + 1 nginx
└── nginx/
    └── nginx.conf         # Upstream + proxy config
```

---

## Yêu cầu

- Docker ≥ 20.10
- Docker Compose ≥ 2.x (`docker compose` hoặc `docker-compose`)

---

## Chạy nhanh

```bash
# Build image một lần, khởi động toàn bộ cụm
docker compose up --build -d
```

Truy cập:
- **API / Swagger UI**: http://localhost/docs  
- **Health check**: http://localhost/health  
- Header `X-Upstream-Addr` trong mỗi response cho biết container nào xử lý.

---

## Scale thêm / bớt container

### Thêm container lên 5 (không cần sửa file)

```bash
# Sao chép khối app3 trong docker-compose.yml thành app4, app5
# rồi thêm server app4:8000; server app5:8000; vào nginx.conf
docker compose up -d --build
```

### Dừng một instance để bảo trì

```bash
docker compose stop todo-api-2
# Nginx tự động ngừng gửi request đến container này.
# Khởi động lại:
docker compose start todo-api-2
```

---

## Dừng toàn bộ

```bash
docker compose down
```

---

## Xem logs

```bash
# Tất cả services
docker compose logs -f

# Chỉ Nginx
docker compose logs -f nginx

# Chỉ app1
docker compose logs -f app1
```

---

## Kiểm tra load balancing

Chạy lệnh sau nhiều lần và quan sát header `X-Upstream-Addr` thay đổi xoay vòng:

```bash
for i in $(seq 1 6); do
  curl -s -o /dev/null -D - http://localhost/health | grep -i x-upstream
done
```

---

## Đổi thuật toán load balancing

Mở `nginx/nginx.conf`, bỏ comment dòng `least_conn;` để Nginx ưu tiên gửi
request đến server ít kết nối nhất (phù hợp hơn khi request có độ trễ không đều):

```nginx
upstream fastapi_cluster {
    least_conn;          # ← bỏ comment dòng này
    server app1:8000;
    server app2:8000;
    server app3:8000;
}
```

Sau đó reload Nginx (không cần restart):

```bash
docker compose exec nginx nginx -s reload
```

---

## Lưu ý quan trọng

> **In-memory storage**: Mỗi container giữ dữ liệu riêng trong RAM.  
> Khi client gửi request đến các container khác nhau, dữ liệu (user, task, token)
> **sẽ không đồng bộ**.  
>
> Để production-ready, cần thay in-memory store bằng database dùng chung
> (PostgreSQL, Redis…) và mount qua `volumes` hoặc service riêng.

---

## Endpoints

**Auth**

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/auth/register` | Đăng ký tài khoản |
| POST | `/auth/login` | Đăng nhập, nhận Bearer token |
| POST | `/auth/logout` | Đăng xuất, huỷ token |
| GET | `/auth/me` | Xem thông tin tài khoản hiện tại |

**Tasks** *(yêu cầu `Authorization: Bearer <token>`)*

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/tasks` | Lấy danh sách task (filter: `done`, `priority`, `search`) |
| POST | `/tasks` | Tạo task mới |
| GET | `/tasks/{id}` | Xem chi tiết task |
| PATCH | `/tasks/{id}` | Cập nhật task (partial) |
| DELETE | `/tasks/{id}` | Xoá task |
| POST | `/tasks/{id}/toggle` | Toggle done / undone |
| GET | `/tasks/stats/summary` | Thống kê theo priority |

**General**

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/health` | Kiểm tra trạng thái server |
| GET | `/docs` | Swagger UI |