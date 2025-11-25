# main.py - Telegram Subscribe-to-Unlock Bot (Mute mãi mãi cho đến khi join kênh thật)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import os
from dotenv import load_dotenv

load_dotenv()

app = Client(
    "verifybot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Cấu hình từ .env
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))          # Ví dụ: -1001234567890
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")   # Ví dụ: myvipchannel (không @)

WELCOME_MSG = (
    "Chào {name}!\n\n"
    "Để được chat trong nhóm, bạn bắt buộc phải tham gia kênh sau:\n"
    f"• https://t.me/{CHANNEL_USERNAME}\n\n"
    "Sau khi tham gia xong, bấm nút bên dưới để được mở khóa ngay!\n\n"
    "Bạn sẽ bị cấm chat cho đến khi hoàn thành bước này."
)

@app.on_chat_member_updated()
async def new_member(client, update):
    new = update.new_chat_member
    old = update.old_chat_member
    if not new or not new.user:
        return

    user = new.user
    chat_id = update.chat.id

    # Bỏ qua bot và chính nó
    if user.is_bot or user.id == (await client.get_me()).id:
        return

    # Chỉ xử lý khi người dùng thực sự join lần đầu
    if new.status in ["member", "administrator", "creator"]:
        if not old or old.status in ["left", "kicked"]:
            # Mute vĩnh viễn
            await client.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions=ChatPermissions()
            )

            # Nút verify
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("Tôi đã tham gia kênh ✅", callback_data=f"verify_{user.id}")
            ]])

            # Gửi tin nhắn chào
            await client.send_message(
                chat_id=chat_id,
                text=WELCOME_MSG.format(name=user.first_name or "bạn"),
                reply_markup=keyboard,
                disable_web_page_preview=True
            )

# Khi bấm nút verify
@app.on_callback_query(filters.regex("^verify_"))
async def verify_button(client, cq):
    user_id = int(cq.data.split("_")[1])

    if cq.from_user.id != user_id:
        await cq.answer("Đây không phải nút của bạn!", show_alert=True)
        return

    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            # ĐÃ JOIN THẬT → MỞ KHÓA
            await client.restrict_chat_member(
                chat_id=cq.message.chat.id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_audios=True,
                    can_send_documents=True,
                    can_send_photos=True,
                    can_send_videos=True,
                    can_send_video_notes=True,
                    can_send_voice_notes=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
            )
            await cq.edit_message_text(
                f"Xác minh thành công!\n"
                f"Chào mừng {cq.from_user.first_name} đã đến với nhóm ❤️\n"
                f"Bạn đã được mở khóa chat!"
            )
        else:
            await cq.answer("Bạn vẫn chưa tham gia kênh thật! Hãy join rồi bấm lại.", show_alert=True)
    except:
        await cq.answer("Bạn chưa tham gia kênh! Vui lòng tham gia rồi bấm lại nhé.", show_alert=True)

print("Bot đang chạy... Đang chờ thành viên mới!")
app.run()
