


# Minte Telegram Restorant Bot Version 1
import json
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import api_restorant_bot


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot_errors.log',
    filemode='a'
)

def load_json(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as rule_json:
            load = json.load(rule_json)
            return load
    except FileNotFoundError:
        print(f"Error: {json_path} Not Found")
        return {}
    except json.JSONDecodeError:
        print(f"Error: {json_path} is not valid JSON!")
        return {}

def get_target(update):
    if update.callback_query:
        return update.callback_query.message
    return update.message

def make_2_button(buttons):
    return [buttons[i:i+2] for i in range(0, len(buttons), 2)]

async def language_menu(update, context):
    bot_date = load_json("minte_restorant_bot.json")
    language = bot_date["language_menu"]
    keyboard = []

    for key, value in language.items():
        name = value["starts"]["name"]
        keyboard.append([InlineKeyboardButton(name, callback_data=key)])

    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.message.reply_text(f"🌍 Choose Your Language / ቋንቋ ምረጡ", reply_markup=reply_markup)

async def service(update, context):
    bot_data = load_json("minte_restorant_bot.json")

    # -------------------------
    # Get language safely
    # -------------------------
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        key = query.data

        context.user_data["lang"] = key
        message_target = query.message
    else:
        key = context.user_data.get("lang", "first_language")
        message_target = update.message

    language = bot_data["language_menu"][key]["starts"]

    # -------------------------
    # BUTTONS
    # -------------------------
    keyboard = [
        [InlineKeyboardButton(language["start_menu"], callback_data="menu")],
        [InlineKeyboardButton(language["start_contact"], callback_data="contact")],
        [InlineKeyboardButton(language["start_about"], callback_data="about")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # -------------------------
    # MESSAGE OUTPUT
    # -------------------------
    await message_target.reply_text(
        f"{language['start_describ']}\n\n",
        reply_markup=reply_markup
    )

async def types(update, context):
    bot_data = load_json("minte_restorant_bot.json")
    lang_key = context.user_data.get("lang", "first_language")
    lang = bot_data["language_menu"][lang_key]

    keyboard = [
        [
            InlineKeyboardButton(lang["food"]["product"]["types"], callback_data="food")],[
            InlineKeyboardButton(lang["drink"]["product"]["types"], callback_data="drink")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    target = get_target(update)

    await target.reply_text(lang["host_dic"], reply_markup=reply_markup)
    
async def button_router(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "food":
        await food_menu(update, context)

    elif data == "drink":
        await drink_menu(update, context)

    elif data == "menu":
        await types(update, context)

    elif data == "contact":
        await contact_command(update, context)

    elif data == "about":
        await about_command(update, context)
        
# Two Button
async def food_menu(update, context):
    bot_data = load_json("minte_restorant_bot.json")
    lang_key = context.user_data.get("lang", "first_language")
    lang = bot_data["language_menu"][lang_key]
    food = lang["food"]["product"]

    buttons = []

    for key, item in food.items():
        if key != "types":
            buttons.append(
                InlineKeyboardButton(item["name"], callback_data=f"food_{key}")
            )

    keyboard = make_2_button(buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    target = update.callback_query.message if update.callback_query else update.message

    await target.reply_text(lang["host_food"], reply_markup=reply_markup)
    
# Two Button
async def drink_menu(update, context):
    bot_data = load_json("minte_restorant_bot.json")
    lang_key = context.user_data.get("lang", "first_language")
    lang = bot_data["language_menu"][lang_key]
    drink = lang["drink"]["product"]
    
    buttons = []

    for key, item in drink.items():
        if key != "types":
            name = item["name"]
    
            buttons.append(InlineKeyboardButton(name, callback_data=f"drink_{key}"))

    keyboard = make_2_button(buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    target = update.callback_query.message if update.callback_query else update.message

    await target.reply_text(lang["host_drink"], reply_markup=reply_markup)
    
async def product_food(update, context):
    bot_data = load_json("minte_restorant_bot.json")
    query = update.callback_query 
    await query.answer()
    
    lang_key = context.user_data.get("lang", "first_language")
    lang = bot_data["language_menu"][lang_key]
    food = lang["food"]["product"]
    
    key = query.data.replace("food_", "")
    
    item = food[key]
     
    await query.message.reply_photo(
        photo=item['image'],
        caption=
        f"{item['name']}\n\n"
        f"{item['description']}\n\n"
        f"{item['lang_price']}: {item['price']}{item['currenc']}"
    )
    
    
async def product_drink(update, context):
    bot_data = load_json("minte_restorant_bot.json")
    query = update.callback_query 
    await query.answer() 
     
    lang_key = context.user_data.get("lang", "first_language")
    lang = bot_data["language_menu"][lang_key]
    drink = lang["drink"]["product"]
    
    key = query.data.replace("drink_", "")
    
    item = drink[key]
    
    await query.message.reply_photo(
        photo=item['image'],
        caption=
        f"{item['name']}\n\n"
        f"{item['description']}\n\n"
        f"{item['lang_price']}: {item['price']}{item['currenc']}"
    )
    
    
async def contact_command(update, context):
    bot_data = load_json("minte_restorant_bot.json")
    lang_key = context.user_data.get("lang", "first_language")
    lang = bot_data["language_menu"][lang_key]
    
    target = get_target(update)
    
    await target.reply_text(lang["contact"])

async def about_command(update, context):
    bot_data = load_json("minte_restorant_bot.json")
    lang_key = context.user_data.get("lang", "first_language")
    lang = bot_data["language_menu"][lang_key]
    
    target = get_target(update)
    
    await target.reply_text(lang["about"])
    
async def handle_message(update, context):
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    response = ""
    
    print(f"User: ({update.message.chat.username}) says: '{text}' in: '{message_type}'")
    
# ========== ERROR HANDLER ==========
async def error(update, context):
    """Clean error handler - logs to file, prints only cause"""
    error_msg = str(context.error)
    
    # Log full error to file
    logging.error(f"Update: {update}, Error: {error_msg}")
    
    # Print only cause to terminal
    cause = error_msg.split("\n")[0][:150]
    print(f"❌ {cause}")
    
    
if __name__ == "__main__":
    #chat()
    app = ApplicationBuilder().token(api_restorant_bot.telegram_minte_restorant_bot_api_cloud).build()
    
    #command  
    app.add_handler(CommandHandler('start', language_menu))
    app.add_handler(CommandHandler('service', service))
    app.add_handler(CommandHandler('menu', types))
    
    app.add_handler(CommandHandler('food', food_menu))
    app.add_handler(CommandHandler('drink', drink_menu))
    
    app.add_handler(CommandHandler('help', service)) 
    app.add_handler(CommandHandler('contact', contact_command))
    app.add_handler(CommandHandler('about', about_command))
    
    # buttons
    app.add_handler(CallbackQueryHandler(service, pattern='^(first_language|second_language)$'))
    app.add_handler(CallbackQueryHandler(product_food, pattern="^food_"))
    app.add_handler(CallbackQueryHandler(product_drink, pattern="^drink_"))
    app.add_handler(CallbackQueryHandler(button_router, pattern="^(food|drink|menu|contact|about)$"))
    
    # message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Error
    app.add_error_handler(error)
    
    # Run bot
    print("🚀 Minte Telegram Restorant bot is LIVE and thinking...")
    app.run_polling()
       
        