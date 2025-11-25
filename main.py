import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ChatMemberHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Lấy các biến môi trường
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME')

# Hàm xử lý khi có thành viên mới tham gia nhóm
def handle_new_member(update: Update, context: CallbackContext):
    """Kiểm tra khi có thành viên mới và gửi thông báo chào mừng."""
    # Chỉ xử lý trong các nhóm, tránh xử lý trong chat riêng
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    for member in update.message.new_chat_members:
        # Nếu thành viên mới chính là bot, bỏ qua
        if member.id == context.bot.id:
            continue

        user_id = member.id
        user_name = member.first_name

        # 1. HẠN CHẾ THÀNH VIÊN MỚI (chỉ cho phép xem)
        context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
        )

        # 2. TẠO NÚT ĐĂNG KÝ
        keyboard = [
            [InlineKeyboardButton("✅ Đăng ký Kênh", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("🔐 Đã Tham Gia", callback_data=f"check_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 3. GỬI TIN NHẮN CHÀO MỪNG
        welcome_text = (
            f"Chào mừng {user_name} đến với nhóm!\n\n"
            "⚠️ Để mở khóa quyền chat, vui lòng:\n"
            "1️⃣ Nhấn nút 'Đăng ký Kênh' bên dưới.\n"
            "2️⃣ Tham gia kênh của chúng tôi.\n"
            "3️⃣ Quay lại đây và nhấn 'Đã Tham Gia' để xác minh."
        )
        update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )

# Hàm xử lý khi người dùng nhấn nút "Đã Tham Gia"
def handle_verification_button(update: Update, context: CallbackContext):
    """Kiểm tra xem user đã tham gia kênh chưa."""
    query = update.callback_query
    user_id = int(query.data.split('_')[1])  # Lấy user_id từ callback_data
    callback_user_id = query.from_user.id

    # Chỉ cho phép người dùng được nhắc đến nhấn nút
    if callback_user_id != user_id:
        query.answer("Đây không phải là yêu cầu của bạn!", show_alert=True)
        return

    query.answer()

    try:
        # QUAN TRỌNG: Kiểm tra trạng thái thành viên trong kênh
        chat_member = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        
        # Kiểm tra nếu trạng thái là 'member', 'administrator', hoặc 'creator'
        if chat_member.status in ['member', 'administrator', 'creator']:
            # XÓA HẠN CHẾ - MỞ KHÓA CHAT
            context.bot.restrict_chat_member(
                chat_id=query.message.chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )

            # Sửa tin nhắn chào mừng thành thông báo thành công
            success_text = f"Chào mừng {query.from_user.first_name} đã chính thức tham gia nhóm! Cảm ơn bạn đã đăng ký kênh! 🎉"
            query.edit_message_text(success_text)

        else:
            # Nếu user chưa tham gia kênh
            query.answer("❌ Bạn chưa tham gia kênh. Vui lòng tham gia rồi thử lại!", show_alert=True)

    except Exception as e:
        # Xử lý lỗi, có thể bot không có quyền admin trong kênh
        logger.error(f"Lỗi khi kiểm tra thành viên kênh: {e}")
        query.answer("❌ Có lỗi xảy ra. Vui lòng thông báo cho Quản trị viên.", show_alert=True)

# Hàm xử lý lệnh /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Tôi là bot xác minh thành viên! Thêm tôi vào nhóm và cấp quyền Admin để hoạt động.")

def main():
    # Khởi tạo Updater
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Thêm Handlers
    dispatcher.add_handler(ChatMemberHandler(handle_new_member))
    dispatcher.add_handler(CallbackQueryHandler(handle_verification_button, pattern="^check_"))
    dispatcher.add_handler(CommandHandler("start", start))

    # Khởi chạy Bot
    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
