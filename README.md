# Telegram Gatekeeper Bot (Python + Flask + Webhook)

Bot này tự động:
- Chào thành viên mới vào nhóm
- Khoá chat của họ
- Yêu cầu họ tham gia một channel
- Kiểm tra xem họ đã tham gia thật chưa
- Nếu có → mở khoá chat

---

## 1. Chuẩn bị Telegram Bot

1. Mở @BotFather
2. /newbot → lấy token → lưu lại
3. Lấy ID channel (dạng `-100xxxxxxxxxx`) bằng cách:
   - Add bot @getidsbot vào channel
   - Nó sẽ trả về ID

---

## 2. Cài đặt biến môi trường trên Railway

Bạn cần 2 env:

| ENV | Giá trị |
|-----|---------|
| TELEGRAM_TOKEN | token từ BotFather |
| CHANNEL_ID | ID channel dạng -100xxxxxxxxxx |

---

## 3. Deploy lên Railway

1. Push code lên GitHub
2. Vào https://railway.app → New Project
3. Chọn **Deploy from GitHub repo**
4. Chọn repo chứa bot
5. Railway sẽ tự build & deploy
6. Vào tab **Variables** và thêm:
