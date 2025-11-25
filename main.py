# main.py (aiogram – không cần api_id/api_hash)
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))        # vẫn cần ID kênh (dùng @getidsbot lấy 1 lần)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME") # ví dụ: myvipchannel

WELCOME = f"""
Chào {{name}}!

Để chat được trong nhóm, bạn cần tham gia kênh:
https://t.me/{CHANNEL_USERNAME}

Sau khi tham gia xong, bấm nút bên dưới để mở khóa!
"""

# Khi có người mới join
@dp.chat_member()
async def new_member(update: types.ChatMemberUpdated):
    if update.new_chat_member.status in ["member", "administrator", "creator"]:
        if update.old_chat_member.status in ["left", "kicked", None]:
            user = update.new_chat_member.user
            chat_id = update.chat.id

            # Mute vĩnh viễn
            await bot.restrict_chat_member(
                chat_id, user.id, permissions=ChatPermissions()
            )

            # Gửi nút verify
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton("Tôi đã tham gia kênh ✅", callback_data=f"verify_{user.id}")
            ]])
            await bot.send_message(
                chat_id, WELCOME.format(name=user.first_name or "bạn"),
                reply_markup=kb, disable_web_page_preview=True
            )

# Khi bấm nút
@dp.callback_query(F.data.startswith("verify_"))
async def verify(cb: types.CallbackQuery):
    user_id = int(cb.data.split("_")[1])
    if cb.from_user.id != user_id:
        return await cb.answer("Không phải nút của bạn!", show_alert=True)

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            # ĐÃ JOIN THẬT → mở khóa
            await bot.restrict_chat_member(
                cb.message.chat.id, user_id,
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
            await cb.message.edit_text(
                f"Xác minh thành công!\nChào mừng {cb.from_user.first_name} đến với nhóm ❤️"
            )
        else:
            await cb.answer("Bạn chưa tham gia kênh thật!", show_alert=True)
    except:
        await cb.answer("Bạn chưa tham gia kênh! Hãy join rồi bấm lại.", show_alert=True)

async def main():
    print("Bot đang chạy...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
