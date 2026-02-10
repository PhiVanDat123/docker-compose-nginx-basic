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