# Task Manager API

API quản lý công việc xây dựng bằng FastAPI + Docker.

## Các chức năng

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
| GET | `/tasks` | Lấy danh sách task (filter theo `done`, `priority`, `search`) |
| POST | `/tasks` | Tạo task mới |
| GET | `/tasks/{id}` | Xem chi tiết task |
| PATCH | `/tasks/{id}` | Cập nhật task (partial update) |
| DELETE | `/tasks/{id}` | Xoá task |
| POST | `/tasks/{id}/toggle` | Đánh dấu done / undone |
| GET | `/tasks/stats/summary` | Thống kê task theo priority |

**General**
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/health` | Kiểm tra trạng thái server |

## Yêu cầu

- Docker & Docker Compose

## Chạy nhanh

```bash
git clone <your-repo-url>
cd <repo-name>
docker-compose up --build
```

Truy cập:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Dừng

```bash
docker-compose down
```

## Hoặc dùng Docker thủ công

```bash
docker build -t task-manager-api .
docker run -d -p 8000:8000 --name task-api task-manager-api
```

Dừng và xoá container:

```bash
docker stop task-api
docker rm task-api
```
Hướng dẫn sử dụng
📝 Sử dụng qua Swagger UI (Giao diện web)

Truy cập http://localhost:8000/docs
Thực hiện các bước sau:

Bước 1: Đăng ký tài khoản

Mở endpoint POST /auth/register
Click Try it out
Nhập thông tin:

json{
  "username": "testuser",
  "password": "123456",
  "full_name": "Nguyễn Văn A"
}

Click Execute

Bước 2: Đăng nhập

Mở endpoint POST /auth/login
Click Try it out
Nhập:

json{
  "username": "testuser",
  "password": "123456"
}

Click Execute
Copy access_token từ response

Bước 3: Xác thực (Authorize)

Click nút Authorize 🔓 ở góc trên bên phải
Nhập: <access_token> (dán token vừa copy)
Click Authorize
Click Close

Bước 4: Tạo task

Mở endpoint POST /tasks
Click Try it out
Nhập:

json{
  "title": "Học Docker",
  "description": "Hoàn thành khóa học Docker cơ bản",
  "priority": "high",
  "due_date": "2026-02-20"
}

Click Execute

Bước 5: Xem danh sách tasks

Mở endpoint GET /tasks
Click Try it out
Click Execute

🔧 Sử dụng qua cURL
1. Đăng ký
bashcurl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456",
    "full_name": "Nguyễn Văn A"
  }'
2. Đăng nhập
bashcurl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456"
  }'
Response sẽ trả về:
json{
  "access_token": "abc123...",
  "token_type": "bearer",
  "user_id": "xyz789"
}
Lưu token vào biến môi trường:
bash# Linux/Mac
export TOKEN="abc123..."

# Windows PowerShell
$env:TOKEN="abc123..."
3. Tạo task
bashcurl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Học Docker",
    "description": "Hoàn thành khóa học Docker",
    "priority": "high",
    "due_date": "2026-02-20"
  }'
4. Lấy danh sách tasks
bash# Tất cả tasks
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Lọc task chưa hoàn thành
curl -X GET "http://localhost:8000/tasks?done=false" \
  -H "Authorization: Bearer $TOKEN"

# Lọc theo priority
curl -X GET "http://localhost:8000/tasks?priority=high" \
  -H "Authorization: Bearer $TOKEN"

# Tìm kiếm
curl -X GET "http://localhost:8000/tasks?search=docker" \
  -H "Authorization: Bearer $TOKEN"
5. Xem chi tiết task
bashcurl -X GET http://localhost:8000/tasks/{task_id} \
  -H "Authorization: Bearer $TOKEN"
6. Cập nhật task
bashcurl -X PATCH http://localhost:8000/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Học Docker & Kubernetes",
    "priority": "medium"
  }'
7. Đánh dấu hoàn thành/chưa hoàn thành
bashcurl -X POST http://localhost:8000/tasks/{task_id}/toggle \
  -H "Authorization: Bearer $TOKEN"
8. Xoá task
bashcurl -X DELETE http://localhost:8000/tasks/{task_id} \
  -H "Authorization: Bearer $TOKEN"
9. Xem thống kê
bashcurl -X GET http://localhost:8000/tasks/stats/summary \
  -H "Authorization: Bearer $TOKEN"
10. Xem thông tin tài khoản
bashcurl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
11. Đăng xuất
bashcurl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"