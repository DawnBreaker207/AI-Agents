# TechScout AI Backend API

Hệ thống Backend cung cấp các API để quản lý việc cào tin tức (Scouting), lọc tin bằng AI (Gatekeeper) và thực hiện nghiên cứu chuyên sâu (Deep Analysis).

## Cấu trúc Response chung
Tất cả các API đều trả về một định dạng thống nhất để dễ dàng tích hợp với Frontend:

```json
{
  "message": "Thông báo từ hệ thống",
  "data": { ... }, // Dữ liệu trả về (Object hoặc Array)
  "timestamp": "2024-05-17T01:56:32.123456"
}
```

---

## Danh sách Endpoints

### 1. Hệ thống & Nghiên cứu (Research)

#### `GET /health`
Kiểm tra trạng thái hoạt động của Agent.
- **Response Data:** `{"status": "running", "agent": "..."}`

#### `POST /research`
Kích hoạt hệ thống Maestro để thực hiện nghiên cứu một chủ đề mới từ đầu.
- **Request Body:** `{"topic": "Thị trường AI Việt Nam", "force_refresh": false}`
- **Response Data:** `{"status": "processing", "topic": "..."}`

#### `POST /chat`
Hỏi đáp với AI Analyst dựa trên ngữ cảnh là các báo cáo nghiên cứu mới nhất.
- **Request Body:** `{"prompt": "Tóm tắt các xu hướng AI nổi bật", "category": "all"}`
- **Response Data:** `{"answer": "Nội dung phản hồi từ AI..."}`

---

### 2. Quản lý Tin tức (News)

#### `GET /api/news/pending`
Lấy danh sách các tin tức vừa được cào về và đang chờ lọc (Status: `PENDING`).
- **Query Params:** `page` (mặc định 1), `size` (mặc định 20)
- **Response Data:** Danh sách các object `PendingNews`.

#### `GET /api/news/watch`
Lấy danh sách các tin tức được AI đánh giá là có liên quan nhưng chưa đủ mức độ ưu tiên để phân tích sâu (Status: `WATCH`).
- **Query Params:** `page`, `size`, `category` (optional)
- **Response Data:** Danh sách các object `PendingNews` đã chấm điểm.

#### `POST /api/news/{news_id}/promote`
Duyệt thủ công một tin từ trạng thái `WATCH` hoặc `TRASH` lên `KEEP` để kích hoạt Stage 3 (Phân tích sâu).
- **Response Data:** `{"news_id": 123, "status": "KEEP"}`

#### `POST /api/research/{news_id}`
Kích hoạt thủ công Stage 3 (Deep Analysis) cho một tin tức cụ thể.

---

### 3. Báo cáo chiến lược (Reports)

#### `GET /history`
Lấy danh sách lịch sử các báo cáo nghiên cứu đã hoàn thành.
- **Response Data:** Danh sách các object `ResearchReport`.

#### `GET /report/{report_id}`
Lấy chi tiết nội dung của một báo cáo cụ thể (bao gồm tech trends, job details, v.v.).

#### `GET /api/reports/strategic`
Lấy danh sách các báo cáo chiến lược mới nhất.

---

### 4. Cấu hình hệ thống (Settings)

#### `PUT /api/sources/{source_id}/toggle`
Bật hoặc tắt một nguồn RSS.
- **Response Data:** `{"id": 1, "is_active": false}`

#### `GET /api/whitelist`
Lấy danh sách các từ khóa ưu tiên (Whitelist Topics).

#### `POST /api/whitelist`
Thêm một từ khóa mới vào danh sách ưu tiên.
- **Request Body:** `{"topic": "Tên topic", "boost_score": 1.5, "force_keep": false}`

#### `DELETE /api/whitelist/{topic_id}`
Xóa một từ khóa khỏi whitelist.

---

## Hướng dẫn triển khai
1. Cấu hình file `.env` với `OPENROUTER_KEY`.
2. Chạy ứng dụng: `python app/main.py`.
3. Hệ thống sẽ tự động khởi tạo DB và nạp dữ liệu mẫu (Seed) nếu chưa có.
4. Truy cập Swagger UI để test API tại: `http://localhost:8888/docs`
