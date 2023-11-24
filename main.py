import pyrogram
import os
import asyncio
import re
import requests

try:
    app_id = int(os.environ.get("app_id", None))
except Exception as app_id:
    print(f"⚠️ App ID Invalid {app_id}")

try:
    api_hash = os.environ.get("api_hash", None)
except Exception as api_id:
    print(f"⚠️ Api Hash Invalid {api_hash}")

try:
    bot_token = os.environ.get("bot_token", None)
except Exception as bot_token:
    print(f"⚠️ Bot Token Invalid {bot_token}")

try:
    custom_caption = os.environ.get("custom_caption", "`{file_name}`")
except Exception as custom_caption:
    print(f"⚠️ Custom Caption Invalid {custom_caption}")

AutoCaptionBot = pyrogram.Client(
    name="AutoCaptionBot", api_id=app_id, api_hash=api_hash, bot_token=bot_token)

def get_file_details(update: pyrogram.types.Message):
    if update.media:
        for message_type in (
                "photo",
                "animation",
                "audio",
                "document",
                "video",
                "video_note",
                "voice",
                "sticker"
        ):
            obj = getattr(update, message_type)
            if obj:
                original_file_name = obj.file_name
                modified_file_name = original_file_name[:47] + ".mx" if len(original_file_name) >= 50 else original_file_name + ".mx"
                modified_file_name = re.sub(r'[^a-zA-Z0-9.]', '.', modified_file_name)
                modified_file_name = re.sub(r'\.+', '.', modified_file_name)
                return obj, obj.file_id, modified_file_name
    elif update.entities:
        for entity in update.entities:
            if entity.type == "text_link":
                return entity, None, entity.url
    return None, None, None

@AutoCaptionBot.on_message(pyrogram.filters.channel)
def edit_caption(bot, update: pyrogram.types.Message):
    if os.environ.get("custom_caption"):
        motech, _, modified_file_name = get_file_details(update)
        try:
            try:
                if motech:
                    if motech.type == "text_link":
                        update.edit(f"Caption for text link: {motech.url}")
                    else:
                        update.edit(custom_caption.format(file_name=modified_file_name))
            except pyrogram.errors.FloodWait as FloodWait:
                asyncio.sleep(FloodWait.value)
                update.edit(custom_caption.format(file_name=modified_file_name))
        except pyrogram.errors.MessageNotModified:
            pass
    else:
        return

AutoCaptionBot.run()
