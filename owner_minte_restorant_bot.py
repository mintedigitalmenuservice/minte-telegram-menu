

#  Owner Minte Restorant Button Bot Version 1
import json
import os
import time
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import api_restorant_bot


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot_errors.log',
    filemode='a'
)

OWNER_TELEGRAM_ID = 6776661461

# File paths
OWNER_JSON_PATH = "telegram_owner_minte_restorant_bot.json"

# Global variable to track what the owner is updating
pending_update = {}

async def clear_pending(request_msg, context, chat_id, product_type, product_key):
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    lang = owner_data["language_menu"][lang_key]
    
    print(f"⏰ Timer STARTED for {product_type} {product_key} at: {time.strftime('%H:%M:%S')}")
    
    try:
        await asyncio.sleep(300)  # 5 minutes
    except asyncio.CancelledError:
        print(f"⏰ Timer CANCELLED for {product_type} {product_key} at: {time.strftime('%H:%M:%S')}")
        return
    
    print(f"⏰ Timer FINISHED for {product_type} {product_key} at: {time.strftime('%H:%M:%S')}")
    
    # Only clear if the pending is still for this product
    current_pending = list(pending_update.keys())
    if current_pending and current_pending[0][0] == product_type and current_pending[0][1] == product_key:
        pending_update.clear()
        
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{lang['timeout_message']}",
                parse_mode="Markdown"
            )
        except:
            pass
        
        # try:
        #     await request_msg.delete()
        # except:
        #     pass
        
        print(f"⏰ Cleared pending for {product_type} {product_key}")
        

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Accept command from Button and command(/)
def get_target(update):
    if update.callback_query:
        return update.callback_query.message
    return update.message

def make_2_button(buttons):
    return [buttons[i:i+2] for i in range(0, len(buttons), 2)]

# ========== LANGUAGE MENU ==========
async def language_menu(update, context):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    owner_data = load_json(OWNER_JSON_PATH)
    language_menu = owner_data.get("language_menu", {})
    
    keyboard = []
    for key in ["first_language", "second_language"]:
        if key in language_menu:
            name = language_menu[key]["starts"]["name"]
            keyboard.append([InlineKeyboardButton(name, callback_data=f"lang_{key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Choose Your Language / ቋንቋ ምረጡ", reply_markup=reply_markup)

async def language_selected(update, context):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    query = update.callback_query
    await query.answer()
    
    lang_key = query.data.replace("lang_", "")
    context.user_data["owner_lang"] = lang_key
    
    await show_update_menu(update, context)

async def show_update_menu(update, context):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    lang = owner_data["language_menu"][lang_key]["starts"]
    
    keyboard = [
    [InlineKeyboardButton(f"{lang['start_menu']}", callback_data="helper_video")],
    [InlineKeyboardButton(f"{owner_data['language_menu'][lang_key]['food']['types']}", callback_data="food_menu")],
    [InlineKeyboardButton(f"{owner_data['language_menu'][lang_key]['drink']['types']}", callback_data="drink_menu")]
]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    target = get_target(update)
    await target.reply_text(lang["start_describ"], reply_markup=reply_markup)

# ========== COMMAND HANDLERS ==========
async def service_command(update, context):
    """Handle /service command"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    
    lang_key = context.user_data.get("owner_lang", "first_language")
    if not lang_key:
        await language_menu(update, context)
    else:
        await show_update_menu(update, context)

async def menu_command(update, context):
    """Handle /menu command - same as service"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    await service_command(update, context)

async def help_command(update, context):
    """Handle /help command - show update menu"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    await helper_video(update, context)

async def food_command(update, context):
    """Handle /food command"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    await food_menu(update, context)

async def drink_command(update, context):
    """Handle /drink command"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    await drink_menu(update, context)

async def contact_command(update, context):
    """Handle /contact command"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    lang = owner_data["language_menu"][lang_key]
    
    await update.message.reply_text(lang["contact"])

async def helper_video(update, context):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    video_path = owner_data["language_menu"].get("helper_video", "")
    
    target = get_target(update)
    lang = owner_data["language_menu"][lang_key]["starts"]
    
    # Send waiting message
    waiting_msg = await target.reply_text(f"{lang['please_wait_video']}")
    
    if video_path and os.path.exists(video_path):
        # Get file size
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # Size in MB
        
        if file_size > 50:
            # Video too large - send as document instead
            with open(video_path, 'rb') as video:
                await target.reply_document(
                    document=video,
                    caption=f"{lang['start_menu']}\n\n⚠️ Video too large for preview. Download to watch."
                )
        else:
            # Video is small enough - send normally
            with open(video_path, 'rb') as video:
                await target.reply_video(
                    video=video, 
                    caption=f"{lang['start_menu']}",
                    supports_streaming=True
                )
                
            # Delete waiting message
            await waiting_msg.delete()
    else:
        # Delete waiting message
        await waiting_msg.delete()
        await target.reply_text(f"❌ {lang.get('video_not_found', 'Helper video not found')}")
    
    await show_update_menu(update, context)

# ========== FOOD MENU ==========
async def food_menu(update, context):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    CUSTOMER_JSON_PATH = "minte_restorant_bot.json"
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    customer_data = load_json(CUSTOMER_JSON_PATH)
    
    owner_lang = owner_data["language_menu"][lang_key]
    customer_lang = customer_data["language_menu"].get(lang_key, customer_data["language_menu"]["first_language"])
    
    food_items = customer_lang["food"]["product"]
    buttons = []
    
    for key, item in food_items.items():
        if key != "types":
            buttons.append(InlineKeyboardButton(item["name"], callback_data=f"food_{key}"))
    
    keyboard = make_2_button(buttons)
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    target = get_target(update)
    await target.reply_text(owner_lang["host_food"], reply_markup=reply_markup)

# ========== DRINK MENU ==========
async def drink_menu(update, context):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    CUSTOMER_JSON_PATH = "minte_restorant_bot.json"
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    customer_data = load_json(CUSTOMER_JSON_PATH)
    
    owner_lang = owner_data["language_menu"][lang_key]
    customer_lang = customer_data["language_menu"].get(lang_key, customer_data["language_menu"]["first_language"])
    
    drink_items = customer_lang["drink"]["product"]
    buttons = []
    
    for key, item in drink_items.items():
        if key != "types":
            buttons.append(InlineKeyboardButton(item["name"], callback_data=f"drink_{key}"))
    
    keyboard = make_2_button(buttons)
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    target = get_target(update)
    await target.reply_text(owner_lang["host_drink"], reply_markup=reply_markup)

# ========== SHOW PRODUCT WITH UPDATE BUTTONS ==========
async def show_product(update, context, product_type, product_key):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    CUSTOMER_JSON_PATH = "minte_restorant_bot.json"
    query = update.callback_query
    await query.answer()
    
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    customer_data = load_json(CUSTOMER_JSON_PATH)
    
    owner_lang = owner_data["language_menu"][lang_key]
    customer_lang = customer_data["language_menu"].get(lang_key, customer_data["language_menu"]["first_language"])
    
    if product_type == "food":
        product_data = customer_lang["food"]["product"][product_key]
    else:
        product_data = customer_lang["drink"]["product"][product_key]
    
    # Store context for later updates
    context.user_data["updating_product_type"] = product_type
    context.user_data["updating_product_key"] = product_key
    
    # Get language text from owner JSON
    if product_type == "food":
        update_image_text = owner_lang["food"]["food_update_image_f"] + " " + owner_lang["food"]["food_update_image_s"]
        update_desc_text = owner_lang["food"]["food_update_descr_f"] + " " + owner_lang["food"]["food_update_descr_s"]
        update_price_text = owner_lang["food"]["food_update_price_f"] + " " + owner_lang["food"]["food_update_price_s"]
    else:
        update_image_text = owner_lang["drink"]["drink_update_image_f"] + " " + owner_lang["drink"]["drink_update_image_s"]
        update_desc_text = owner_lang["drink"]["drink_update_descr_f"] + " " + owner_lang["drink"]["drink_update_descr_s"]
        update_price_text = owner_lang["drink"]["drink_update_price_f"] + " " + owner_lang["drink"]["drink_update_price_s"]
    
    keyboard = [
        [InlineKeyboardButton(f"📷 {update_image_text}", callback_data=f"update_image_{product_type}_{product_key}")],
        [InlineKeyboardButton(f"📝 {update_desc_text}", callback_data=f"update_description_{product_type}_{product_key}")],
        [InlineKeyboardButton(f"💰 {update_price_text}", callback_data=f"update_price_{product_type}_{product_key}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get price text from customer JSON
    price_label = product_data.get('lang_price', '💰 Price')
    currency = product_data.get('currenc', '$')
    price = product_data.get('price', 0)
    
    caption = (
        f"*{product_data['name']}*\n\n"
        f"📝 {product_data['description']}\n\n"
        f"{price_label}: {price} {currency}"
    )
    
    # Check if image file exists
    image_path = product_data.get('image', '')
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img:
            await query.message.reply_photo(
                photo=img,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    else:
        await query.message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ========== HANDLE UPDATE BUTTONS ==========
async def update_image_request(update, context, product_type, product_key):
    query = update.callback_query
    await query.answer()
    
    # Cancel existing timer if exists
    if "timeout_task" in context.user_data:
        context.user_data["timeout_task"].cancel()
    
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    owner_lang = owner_data["language_menu"][lang_key]
    
    if product_type == "food":
        text = owner_lang["food"]["food_update_image_f"] + " " + owner_lang["food"]["food_update_image_s"]
    else:
        text = owner_lang["drink"]["drink_update_image_f"] + " " + owner_lang["drink"]["drink_update_image_s"]
    
    # Clear old pending
    pending_update.clear()
    
    request_msg = await query.message.reply_text(f"⏳ {text}\n\n{owner_lang['request_image']}")
    pending_update[(product_type, product_key, "image")] = True
    
    # Start new timer and store it
    task = asyncio.create_task(clear_pending(request_msg, context, query.message.chat_id, product_type, product_key))
    context.user_data["timeout_task"] = task


async def update_description_request(update, context, product_type, product_key):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    query = update.callback_query
    await query.answer()
    
    # Cancel existing timer if exists
    if "timeout_task" in context.user_data:
        context.user_data["timeout_task"].cancel()
    
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    owner_lang = owner_data["language_menu"][lang_key]
    
    if product_type == "food":
        text = owner_lang["food"]["food_update_descr_f"] + " " + owner_lang["food"]["food_update_descr_s"]
    else:
        text = owner_lang["drink"]["drink_update_descr_f"] + " " + owner_lang["drink"]["drink_update_descr_s"]
    
    # Clear old pending
    pending_update.clear()
    
    request_msg = await query.message.reply_text(f"📝 {text}\n\n{owner_lang['request_description']}")
    pending_update[(product_type, product_key, "description")] = True
    
    # Start new timer and store it
    task = asyncio.create_task(clear_pending(request_msg, context, query.message.chat_id, product_type, product_key))
    context.user_data["timeout_task"] = task


async def update_price_request(update, context, product_type, product_key):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    query = update.callback_query
    await query.answer()
    
    # Cancel existing timer if exists
    if "timeout_task" in context.user_data:
        context.user_data["timeout_task"].cancel()
    
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    owner_lang = owner_data["language_menu"][lang_key]
    
    if product_type == "food":
        text = owner_lang["food"]["food_update_price_f"] + " " + owner_lang["food"]["food_update_price_s"]
    else:
        text = owner_lang["drink"]["drink_update_price_f"] + " " + owner_lang["drink"]["drink_update_price_s"]
    
    # Clear old pending
    pending_update.clear()
    
    request_msg = await query.message.reply_text(f"💰 {text}\n\n{owner_lang['request_price']}")
    pending_update[(product_type, product_key, "price")] = True
    
    # Start new timer and store it
    task = asyncio.create_task(clear_pending(request_msg, context, query.message.chat_id, product_type, product_key))
    context.user_data["timeout_task"] = task
    
    # ========== SAVE UPDATES FROM MESSAGES ==========
async def handle_owner_update(update, context):
    if not pending_update:
        return
    
    user_id = update.effective_user.id
    if user_id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    
    # Get pending update info
    for key in list(pending_update.keys()):
        CUSTOMER_JSON_PATH = "minte_restorant_bot.json"
        product_type, product_key, field = key
        
        customer_data = load_json(CUSTOMER_JSON_PATH)
        lang_key = context.user_data.get("owner_lang", "first_language")
        customer_lang = customer_data["language_menu"].get(lang_key, customer_data["language_menu"]["first_language"])
        
        if product_type == "food":
            target = customer_lang["food"]["product"][product_key]
        else:
            target = customer_lang["drink"]["product"][product_key]
        
        # Show "Updating..." message
        lang_key = context.user_data.get("owner_lang", "first_language")
        owner_data = load_json(OWNER_JSON_PATH)
        lang = owner_data["language_menu"][lang_key]
        status_msg = await update.message.reply_text(f"⏳ {lang['updating_message']}")
        
        if field == "image":
            # Only accept photo
            if update.message.photo:
                # Get the largest photo
                photo_file = await update.message.photo[-1].get_file()
                
                # Save to images folder
                image_filename = f"{product_type}_{product_key}.jpg"
                image_path = os.path.join("images", image_filename)
                
                # Create images folder if not exists
                os.makedirs("images", exist_ok=True)
                
                # Download image
                await photo_file.download_to_drive(image_path)
                
                # Update JSON with new image path
                target["image"] = image_path
                save_json(CUSTOMER_JSON_PATH, customer_data)
                
                #await status_msg.edit_text("✅ Image updated successfully!")
                await status_msg.edit_text(f"✅ {lang['image_updated']}")
                
            else:
                await status_msg.edit_text(f"❌ {lang['error_photo_only']}")
                return
                
        elif field == "description":
            if update.message.text:
                target["description"] = update.message.text
                save_json(CUSTOMER_JSON_PATH, customer_data)
                #await status_msg.edit_text("✅ Description updated successfully!")
                await status_msg.edit_text(f"✅ {lang['description_updated']}")
            else:
                #await status_msg.edit_text("❌ Please send TEXT for description.")
                await status_msg.edit_text(f"❌ {lang['error_text_only']}")
                return
                
        elif field == "price":
            if update.message.text:
                try:
                    new_price = float(update.message.text)
                    target["price"] = new_price
                    save_json(CUSTOMER_JSON_PATH, customer_data)
                    await status_msg.edit_text(f"✅ {lang['price_updated']} {new_price}")
                except ValueError:
                    await status_msg.edit_text(f"❌ {lang['error_number_only']}")
                    return
            else:
                await status_msg.edit_text(f"❌ {lang['error_number_only']}")
                return
        
        # Remove from pending
        del pending_update[key]
        
        # Show full updated product info
        await show_full_updated_info(update, context, product_type, product_key)
        return

async def show_full_updated_info(update, context, product_type, product_key):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    CUSTOMER_JSON_PATH = "minte_restorant_bot.json"
    """Show full product info after update (image, description, price)"""
    lang_key = context.user_data.get("owner_lang", "first_language")
    owner_data = load_json(OWNER_JSON_PATH)
    customer_data = load_json(CUSTOMER_JSON_PATH)
    
    owner_lang = owner_data["language_menu"][lang_key]
    customer_lang = customer_data["language_menu"].get(lang_key, customer_data["language_menu"]["first_language"])
    if product_type == "food":
        product_data = customer_lang["food"]["product"][product_key]
        success_text = owner_lang["food"]["food_succes"]
    else:
        product_data = customer_lang["drink"]["product"][product_key]
        success_text = owner_lang["drink"]["drink_succes"]
    
    bot_link = owner_data["language_menu"].get("bot_link", "")
    
    # Get price label
    price_label = product_data.get('lang_price', '💰 Price')
    currency = product_data.get('currenc', '$')
    price = product_data.get('price', 0)
    
    keyboard = [
        [InlineKeyboardButton("📋 Menu", callback_data="menu_back")],
        [InlineKeyboardButton("🔍 Check Bot", url=bot_link)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"✅ *{product_data['name']}* {success_text}\n\n"
        f"📝 {product_data['description']}\n\n"
        f"{price_label}: {price} {currency}"
    )
    
    # Show image if exists
    image_path = product_data.get('image', '')
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img:
            await update.message.reply_photo(
                photo=img,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ========== BUTTON ROUTER ==========
async def button_router(update, context):
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ You don't have permission.")
        return
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "helper_video":
        await helper_video(update, context)
    elif data == "food_menu":
        await food_menu(update, context)
    elif data == "drink_menu":
        await drink_menu(update, context)
    elif data == "menu_back":
        await show_update_menu(update, context)
    elif data.startswith("food_"):
        product_key = data.replace("food_", "")
        await show_product(update, context, "food", product_key)
    elif data.startswith("drink_"):
        product_key = data.replace("drink_", "")
        await show_product(update, context, "drink", product_key)
    elif data.startswith("update_image_"):
        parts = data.split("_")
        product_type = parts[2]
        product_key = parts[3]
        await update_image_request(update, context, product_type, product_key)
    elif data.startswith("update_description_"):
        parts = data.split("_")
        product_type = parts[2]
        product_key = parts[3]
        await update_description_request(update, context, product_type, product_key)
    elif data.startswith("update_price_"):
        parts = data.split("_")
        product_type = parts[2]
        product_key = parts[3]
        await update_price_request(update, context, product_type, product_key)

# ========== ERROR HANDLER ==========
async def error(update, context):
    """Clean error handler - logs to file, prints only cause"""
    error_msg = str(context.error)
    
    # Log full error to file
    logging.error(f"Update: {update}, Error: {error_msg}")
    
    # Print only cause to terminal
    cause = error_msg.split("\n")[0][:150]
    print(f"❌ {cause}")
    
# ========== MAIN ==========
if __name__ == '__main__':
    app = ApplicationBuilder().token(api_restorant_bot.telegram_owner_minte_restorant_bot_api).build()
    
    # Commands (all 6 commands)
    app.add_handler(CommandHandler('start', language_menu))
    app.add_handler(CommandHandler('service', service_command))
    app.add_handler(CommandHandler('menu', menu_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('food', food_command))
    app.add_handler(CommandHandler('drink', drink_command))
    app.add_handler(CommandHandler('contact', contact_command))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(button_router, pattern="^(helper_video|food_menu|drink_menu|menu_back|food_|drink_|update_image_|update_description_|update_price_)"))
    # Message handler for updates (images, text)
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_owner_update))
    
    # Error handler
    app.add_error_handler(error)
    
    print("🚀 Owner Minte Restorant Bot running...")
    app.run_polling()
    
    