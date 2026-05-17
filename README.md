# 🚢 TechScout Market Intelligence — Docker Compose Deployment

TechScout đã được đóng gói hoàn toàn bằng **Docker** và **Docker Compose**, giúp bạn triển khai và khởi chạy cả hai dịch vụ Frontend và Backend chỉ với một câu lệnh duy nhất. Dữ liệu được bảo toàn vẹn toàn bằng SQLite Database volume persistence.

---

## 🏗️ Kiến Trúc Hệ Thống Trong Docker

*   **techscout-frontend** (`node:20-alpine`): Chạy ứng dụng React Router (SSR enabled) lắng nghe tại cổng **`3000`**.
*   **techscout-backend** (`python:3.11-slim`): Chạy FastAPI API backend kết hợp scheduler (quét tin tự động) lắng nghe tại cổng **`8888`**.
*   **techscout-backend-data** (Docker local volume): Lưu trữ SQLite database (`app.db`) an toàn, bảo đảm dữ liệu tin tuyển dụng, watchlists và báo cáo AI không bị mất khi khởi động lại container.

---

## ⚡ Hướng Dẫn Khởi Chạy Nhanh (Quick Start)

### 1. Chuẩn bị file môi trường (`.env`)
Đảm bảo bạn đã cấu hình key API đầy đủ trong file `./backend/.env` (tham khảo file `./backend/.example.env`). Các key này sẽ tự động được tải vào container của Backend.

```bash
# Ví dụ cấu hình tối thiểu trong ./backend/.env
OPENROUTER_KEY=your-openrouter-key-here
RAPIDAPI_KEY=your-optional-rapidapi-key-for-jsearch
ADZUNA_APP_ID=your-optional-adzuna-app-id
ADZUNA_API_KEY=your-optional-adzuna-api-key
```

### 2. Khởi chạy toàn bộ hệ thống bằng Docker Compose
Mở terminal tại thư mục gốc của dự án (thư mục chứa file `docker-compose.yml`) và chạy:

```bash
docker compose up -d --build
```

Lệnh này sẽ:
*   Build image cho cả Frontend và Backend từ các file Dockerfile tương ứng.
*   Tự động tải các dependency và thiết lập môi trường.
*   Khởi chạy các container dưới dạng background (`-d`).

### 3. Kiểm tra trạng thái các dịch vụ
```bash
docker compose ps
```

---

## 🌐 Địa Chỉ Truy Cập Dịch Vụ

*   **Bảng điều khiển Frontend:** [http://localhost:3000](http://localhost:3000)
*   **Backend API Swagger UI:** [http://localhost:8888/docs](http://localhost:8888/docs)
*   **Luồng dữ liệu Realtime SSE:** [http://localhost:8888/api/news/stream](http://localhost:8888/api/news/stream)

---

## ⚙️ Hướng Dẫn Triển Khai Lên Server Riêng (VPS / Cloud)

Nếu bạn deploy ứng dụng này lên một VPS hoặc Cloud Server có IP công cộng hoặc tên miền riêng (ví dụ: `mytechscout.com`):

1.  Mở file `docker-compose.yml` ở thư mục gốc.
2.  Tại cấu hình của service `frontend`, thay đổi biến môi trường `VITE_API_URL` trỏ tới IP hoặc tên miền của Server của bạn:
    ```yaml
    environment:
      - PORT=3000
      - API_BASE_URL=http://backend:8888
      - VITE_API_URL=http://<YOUR_SERVER_IP_OR_DOMAIN>:8888
    ```
3.  Rebuild và khởi chạy lại dịch vụ:
    ```bash
    docker compose up -d --build
```

---

## 📋 Các Câu Lệnh Quản Trị Hữu Ích

*   **Xem logs thời gian thực:**
    ```bash
    docker compose logs -f
    ```
*   **Xem logs của riêng Backend:**
    ```bash
    docker compose logs -f backend
    ```
*   **Dừng hệ thống (giữ nguyên dữ liệu DB):**
    ```bash
    docker compose down
    ```
*   **Dừng hệ thống và XÓA SẠCH dữ liệu DB (Làm mới hoàn toàn):**
    ```bash
    docker compose down -v
    ```

---

## 🚀 Tích Hợp Jenkins CI/CD Pipeline

Dự án đã cấu hình sẵn file [Jenkinsfile](file:///d:/Code/AI-Agents/Jenkinsfile) theo chuẩn **Declarative Pipeline** để tự động hóa toàn bộ quy trình từ checkout, bảo mật, build, cho đến deploy lên server.

### 🔑 Các Credentials cần thêm trong Jenkins Store:
Để đảm bảo các API keys quan trọng không bị lộ trên git, pipeline sẽ tự động truy xuất các credentials từ Jenkins Store và inject vào file `.env` khi build:
1.  `techscout-openrouter-key` (Secret text): Token OpenRouter để phân tích AI.

### 🛠️ Các giai đoạn tự động hóa trong Pipeline:
*   **Clean & Checkout**: Dọn dẹp workspace và lấy code mới từ repository.
*   **Inject Secrets**: Tạo file cấu hình bảo mật `.env` từ credentials an toàn.
*   **Testing & Linters**: Kiểm tra lỗi biên dịch Python và Frontend build test để đảm bảo chất lượng.
*   **Build Docker Images**: Build song song và gắn thẻ tag image tương ứng với build number (`techscout-backend:${BUILD_NUMBER}`).
*   **Deploy**: Dừng các container cũ và khởi chạy bản cập nhật mới (Zero database loss), sau đó tự dọn dẹp các image không sử dụng (`docker image prune -f`) giúp tiết kiệm dung lượng đĩa.

