import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

TOKEN = os.environ["8531113071xxxx:"]
CHANNEL_ID = os.environ["-1002xxx"]   # dạng -100xxxxxxxxxx

bot = Bot(TOKEN)


# Khi có thành viên mới
def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        user_id = member.id
        chat_id = update.message.chat_id

        # Khóa người mới: không cho chat
        context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions={"can_send_messages": False}
        )

        # Gửi nhiệm vụ tham gia kênh
        keyboard = [
            [InlineKeyboardButton("Tôi đã tham gia kênh", callback_data=f"verify_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"👋 Chào <b>{member.first_name}</b>!\n\n"
                "Để mở khóa chat, vui lòng tham gia kênh dưới đây:\n"
                f"👉 <a href='https://t.me/c/{str(CHANNEL_ID)[4:]}' >BẤM VÀO ĐÂY</a>\n\n"
                "Sau đó nhấn nút <b>Tôi đã tham gia kênh</b>."
            ),
            parse_mode="HTML",
            reply_markup=reply_markup
        )


# Xác minh khi người dùng nhấn nút
def verify(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    _, user_id = data.split("_")
    user_id = int(user_id)
    chat_id = query.message.chat_id

    # Chỉ xử lý nếu đúng người
    if query.from_user.id != user_id:
        query.answer("Bạn không thể xác thực hành động của người khác!")
        return

    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)

        if member.status not in ["left", "kicked"]:
            # Mở khóa chat
            context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions={"can_send_messages": True}
            )
            query.edit_message_text("✅ Bạn đã tham gia kênh — Chat của bạn đã được mở khóa!")
        else:
            query.answer("❌ Bạn CHƯA tham gia kênh!", show_alert=True)
    except:
        query.answer("⚠ Không thể kiểm tra. Hãy thử lại!", show_alert=True)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Trigger: người mới vào nhóm
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))

    # Trigger: nhấn nút verify
    dp.add_handler(CallbackQueryHandler(verify, pattern=r"verify_\d+"))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
