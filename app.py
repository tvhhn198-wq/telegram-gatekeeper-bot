import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CallbackQueryHandler, MessageHandler, Filters

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]  # dạng -100xxxxxxxxxx

bot = Bot(TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)


# Khi có thành viên mới vào nhóm
def welcome(update, context):
    for member in update.message.new_chat_members:
        user_id = member.id
        chat_id = update.message.chat_id

        # Khóa người mới: không cho chat
        context.bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions={"can_send_messages": False}
        )

        # Gửi nhiệm vụ + nút xác nhận
        keyboard = [
            [InlineKeyboardButton("Tôi đã tham gia kênh", callback_data=f"verify_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=chat_id,
            text=f"👋 Chào {member.first_name}!\n"
                 f"Để được phép chat trong nhóm, bạn cần tham gia kênh:\n"
                 f"👉 https://t.me/{CHANNEL_ID.replace('-100', '')}\n\n"
                 f"Sau đó bấm nút bên dưới:",
            reply_markup=reply_markup
        )


# Khi người dùng bấm nút xác thực
def verify(update, context):
    query = update.callback_query
    data = query.data
    _, user_id_str = data.split("_")
    user_id = int(user_id_str)

    # Nút chỉ dành cho đúng người
    if query.from_user.id != user_id:
        query.answer("Nút này không dành cho bạn.", show_alert=True)
        return

    # Kiểm tra xem user đã join channel chưa
    member = context.bot.get_chat_member(CHANNEL_ID, user_id)

    if member.status in ["member", "administrator", "creator"]:
        # Mở khóa chat
        context.bot.restrict_chat_member(
            query.message.chat_id,
            user_id,
            permissions={
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_other_messages": True
            }
        )
        query.edit_message_text("🎉 Bạn đã tham gia kênh! Chat đã được mở khóa.")
    else:
        query.answer("⚠️ Bạn CHƯA tham gia kênh. Hãy join rồi thử lại!", show_alert=True)


# đăng ký handlers
dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
dispatcher.add_handler(CallbackQueryHandler(verify, pattern="^verify_"))


# Webhook cho Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return "OK"


@app.route("/")
def index():
    return "Bot đang chạy!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
