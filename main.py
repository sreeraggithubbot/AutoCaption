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

start_message = """
<b>👋Hello {}</b>
<b>I am an AutoCaption bot</b>
<b>All you have to do is add me to your channel and I will show you my power</b>
<b>@Mo_Tech_YT</b>"""

about_message = """
<b>• Name : [AutoCaption V1](t.me/{username})</b>
<b>• Developer : [Muhammed](https://github.com/PR0FESS0R-99)
<b>• Language : Python3</b>
<b>• Library : Pyrogram v{version}</b>
<b>• Updates : <a href=https://t.me/Mo_Tech_YT>Click Here</a></b>
<b>• Source Code : <a href=https://github.com/PR0FESS0R-99/AutoCaption-Bot>Click Here</a></b>"""

def is_url_safe(url):
    # Add conditions to check if the URL starts with specific prefixes
    safe_prefixes = ["https://is.gd/", "https://stream.airtelxstreamsmarttube.workers.dev/0:/"]
    return not any(url.startswith(prefix) for prefix in safe_prefixes)

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

def start_buttons(bot, update):
    bot = bot.get_me()
    buttons = [[
        pyrogram.types.InlineKeyboardButton("Updates", url="t.me/Mo_Tech_YT"),
        pyrogram.types.InlineKeyboardButton("About 🤠", callback_data="about")
    ], [
        pyrogram.types.InlineKeyboardButton("➕️ Add To Your Channel ➕️", url=f"http://t.me/{bot.username}?startchannel=true")
    ]]
    return pyrogram.types.InlineKeyboardMarkup(buttons)

def about_buttons(bot, update):
    buttons = [[
        pyrogram.types.InlineKeyboardButton("🏠 Back To Home 🏠", callback_data="start")
    ]]
    return pyrogram.types.InlineKeyboardMarkup(buttons)

def shorten_url(url):
    try:
        response = requests.get(f"https://is.gd/create.php?format=simple&url={url}")
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error shortening URL: {e}")
    return url

@AutoCaptionBot.on_message(pyrogram.filters.private & pyrogram.filters.command(["start"]))
def start_command(bot, update):
    update.reply(start_message.format(update.from_user.mention), reply_markup=start_buttons(bot, update),
                 parse_mode=pyrogram.enums.ParseMode.HTML, disable_web_page_preview=True)

@AutoCaptionBot.on_callback_query(pyrogram.filters.regex("start"))
def strat_callback(bot, update):
    update.message.edit(start_message.format(update.from_user.mention), reply_markup=start_buttons(bot, update.message),
                         parse_mode=pyrogram.enums.ParseMode.HTML, disable_web_page_preview=True)

@AutoCaptionBot.on_callback_query(pyrogram.filters.regex("about"))
def about_callback(bot, update):
    bot = bot.get_me()
    update.message.edit(about_message.format(version=pyrogram.__version__, username=bot.mention),
                         reply_markup=about_buttons(bot, update.message), parse_mode=pyrogram.enums.ParseMode.HTML, disable_web_page_preview=True)

@AutoCaptionBot.on_message(pyrogram.filters.channel)
def edit_caption(bot, update: pyrogram.types.Message):
    if os.environ.get("custom_caption"):
        motech, _, modified_file_name = get_file_details(update)
        try:
            try:
                update.edit(custom_caption.format(file_name=modified_file_name))
            except pyrogram.errors.FloodWait as FloodWait:
                asyncio.sleep(FloodWait.value)
                update.edit(custom_caption.format(file_name=modified_file_name))
        except pyrogram.errors.MessageNotModified:
            pass

        # Check for links and shorten them
        if update.entities:
            for entity in update.entities:
                if entity.type == "text_link" and entity.url.startswith(("http", "https")) and is_url_safe(entity.url):
                    # Shorten the link using is.gd
                    shortened_url = shorten_url(entity.url)
                    # Edit the message to include the shortened link
                    update.edit(update.text.replace(entity.url, shortened_url))

    else:
        return

print("Telegram AutoCaption V1 Bot Start")
print("Bot Created By https://github.com/PR0FESS0R-99")

AutoCaptionBot.run()
                                  
