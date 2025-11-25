# main.py – Bot verify join kênh (chỉ cần BOT_TOKEN)
from aiogram import Bot, Dispatcher, types
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Cấu hình kênh (bắt buộc join)
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))          # Ví dụ: -1001234567890
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")   # Ví dụ: myvipchannel (không có @)

TEXT = f"""
Chào {{name}}!

Để được chat trong nhóm, bạn phải tham gia kênh:
https://t.me/{CHANNEL_USERNAME}

Sau khi tham gia xong, bấm nút bên dưới để mở khóa ngay!
"""

# Khi có người mới vào nhóm
@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(update: types.ChatMemberUpdated):
    user = update.new_chat_member.user
    chat_id = update.chat.id

    # Mute vĩnh viễn
    await bot.restrict_chat_member(chat_id, user.id, permissions=ChatPermissions())

    # Nút verify
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton("Tôi đã tham gia kênh ✅", callback_data=f"verify_{user.id}")
    ]])

    await bot.send_message(
        chat_id,
        TEXT.format(name=user.first_name or "bạn"),
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# Khi bấm nút verify
@dp.callback_query(F.data.startswith("verify_"))
async def check_verify(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    if callback.from_user.id != user_id:
        return await callback.answer("Đây không phải nút của bạn!", show_alert=True)

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ("member", "administrator", "creator"):
            # ĐÃ THAM GIA THẬT → mở khóa
            await bot.restrict_chat_member(
                callback.message.chat.id, user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_audios=True,
                    can_send_documents=True,
                    can_send_photos=True,
                    can_send_videos=True,
                    can_send_voice_notes=True,
                    can_add_web_page_previews=True
                )
            )
            await callback.message.edit_text(
                f"Xác minh thành công!\nChào mừng {callback.from_user.first_name} đến với nhóm ❤️"
            )
        else:
            await callback.answer("Bạn chưa tham gia kênh thật! Hãy join rồi bấm lại.", show_alert=True)
    except:
        await callback.answer("Bạn chưa tham gia kênh! Vui lòng tham gia rồi bấm lại.", show_alert=True)

async def main():
    print("Bot đang chạy... Đang chờ thành viên mới!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
