# main.py – WEBHOOK VERSION (Render free chạy ngon 100%, không bao giờ Conflict)
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, run_app
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

TEXT = f"""
Chào {{name}}! 

Để được chat trong nhóm, bạn phải tham gia kênh:
https://t.me/{CHANNEL_USERNAME}

Sau khi tham gia xong, bấm nút bên dưới để mở khóa ngay!
"""

@dp.message(F.new_chat_members)
async def on_user_join(message: types.Message):
    for user in message.new_chat_members:
        if user.is_bot or user.id == (await bot.get_me()).id: continue
        await bot.restrict_chat_member(message.chat.id, user.id, permissions=ChatPermissions())
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("Tôi đã tham gia kênh ✅", callback_data=f"verify_{user.id}")]])
        await bot.send_message(message.chat.id, TEXT.format(name=user.first_name or "bạn"), reply_markup=keyboard, disable_web_page_preview=True)

@dp.callback_query(F.data.startswith("verify_"))
async def check_verify(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    if callback.from_user.id != user_id:
        return await callback.answer("Không phải nút của bạn!", show_alert=True)
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ("member", "administrator", "creator"):
            await bot.restrict_chat_member(callback.message.chat.id, user_id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_voice_notes=True, can_add_web_page_previews=True))
            await callback.message.edit_text(f"Xác minh thành công!\nChào mừng {callback.from_user.first_name} đến với nhóm ❤️")
        else:
            await callback.answer("Bạn chưa tham gia kênh thật!", show_alert=True)
    except:
        await callback.answer("Bạn chưa tham gia kênh! Hãy join rồi bấm lại.", show_alert=True)

async def on_startup(app):
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_URL')}/webhook"
    await bot.set_webhook(webhook_url)
    print(f"Webhook đã được set: {webhook_url}")

async def main():
    app = aiohttp.web.Application()
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path="/webhook")
    app.on_startup.append(on_startup)
    return app

if __name__ == "__main__":
    run_app(main(), host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
