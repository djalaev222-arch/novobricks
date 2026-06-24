import os
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT2_TOKEN        = os.environ['BOT2_TOKEN']
LEADS_BOT_TOKEN   = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID           = os.environ['TELEGRAM_CHAT_ID']

WAITING_NAME  = 1
WAITING_PHONE = 2

# ──────────────────────────────────────────────
# Тексты разделов
# ──────────────────────────────────────────────
TEXTS = {
    'brick': (
        "🧱 *Облицовочный кирпич NovoBricks*\n\n"
        "• Прочность М300 — в 3 раза выше стандарта\n"
        "• Морозостойкость F150\n"
        "• Водопоглощение < 6%\n"
        "• Срок службы в 12 раз выше силикатного\n"
        "• 14 цветов, 22 типоразмера\n\n"
        "💰 Цена: *от 28 ₽/шт*\n"
        "🚚 Доставка по РФ от 3 дней"
    ),
    'tile': (
        "🪨 *Облицовочная плитка NovoBricks*\n\n"
        "• Гиперпрессованная технология\n"
        "• Толщина 20–40 мм\n"
        "• Устойчива к морозу и влаге\n"
        "• 14 цветов\n\n"
        "💰 Цена: *от 850 ₽/м²*\n"
        "🚚 Доставка по РФ от 3 дней"
    ),
    'paving': (
        "🟫 *Тротуарная плитка NovoBricks*\n\n"
        "• Нагрузка до 40 тонн\n"
        "• Морозостойкость F200\n"
        "• Антискользящая поверхность\n"
        "• 8 форм, 10 цветов\n\n"
        "💰 Цена: *от 650 ₽/м²*\n"
        "🚚 Доставка по РФ от 3 дней"
    ),
    'colors': (
        "🎨 *Палитра NovoBricks — 14 цветов*\n\n"
        "🔴 Красный классический\n"
        "🟤 Коричневый\n"
        "⚫ Антрацит\n"
        "⚪ Белый\n"
        "🟡 Песочный / бежевый\n"
        "🟠 Терракот\n"
        "…и ещё 8 оттенков\n\n"
        "Для получения образцов — оставьте заявку!"
    ),
    'portfolio': (
        "📸 *Наши объекты*\n\n"
        "Реализованные проекты по всей Башкирии и России.\n"
        "Жилые дома, коттеджи, торговые центры, административные здания.\n\n"
        "Подробное портфолио на сайте: novobricks.ru"
    ),
    'contacts': (
        "📞 *Контакты NovoBricks*\n\n"
        "📱 +7 (964) 95-95-095\n"
        "📧 info@novobricks.ru\n\n"
        "🏢 *Офис:*\n"
        "Уфа, ул. Строительная, 1, офис 201\n"
        "Пн–Пт: 9:00–18:00\n\n"
        "🏭 *Завод:*\n"
        "Белорецк, ул. Заводская, 14"
    ),
}

PRODUCT_NAMES = {
    'brick':   '🧱 Кирпич',
    'tile':    '🪨 Плитка',
    'paving':  '🟫 Тротуарная плитка',
    'price':   '💰 Прайс-лист',
}

# ──────────────────────────────────────────────
# Клавиатуры
# ──────────────────────────────────────────────
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧱 Кирпич",            callback_data="brick"),
         InlineKeyboardButton("🪨 Плитка",             callback_data="tile")],
        [InlineKeyboardButton("🟫 Тротуарная плитка",  callback_data="paving")],
        [InlineKeyboardButton("🎨 Палитра цветов",     callback_data="colors"),
         InlineKeyboardButton("📸 Наши объекты",       callback_data="portfolio")],
        [InlineKeyboardButton("💰 Получить прайс",     callback_data="order_price"),
         InlineKeyboardButton("📞 Контакты",           callback_data="contacts")],
    ])

def product_kb(product):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Оставить заявку", callback_data=f"order_{product}")],
        [InlineKeyboardButton("⬅️ Главное меню",    callback_data="main_menu")],
    ])

def back_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
    ])

def cancel_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]
    ])

# ──────────────────────────────────────────────
# Отправка заявки в бот №1
# ──────────────────────────────────────────────
async def send_lead(name: str, phone: str, product: str):
    text = (
        f"🔔 *Заявка из Telegram-бота*\n\n"
        f"👤 *Имя:* {name}\n"
        f"📞 *Телефон:* {phone}\n"
        f"📋 *Интерес:* {PRODUCT_NAMES.get(product, product)}"
    )
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{LEADS_BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )

# ──────────────────────────────────────────────
# Хэндлеры
# ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Добро пожаловать в *NovoBricks*!\n\n"
        "Производитель гиперпрессованного кирпича и плитки из Башкирии.\n"
        "Срок службы в 12 раз выше силикатного 🏗️\n\n"
        "Выберите раздел:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_kb(), parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_kb(), parse_mode='Markdown')


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'main_menu':
        await start(update, context)
        return

    # Информационные разделы
    if data in ('colors', 'portfolio', 'contacts'):
        await query.edit_message_text(TEXTS[data], reply_markup=back_kb(), parse_mode='Markdown')
        return

    # Продуктовые разделы
    if data in ('brick', 'tile', 'paving'):
        await query.edit_message_text(TEXTS[data], reply_markup=product_kb(data), parse_mode='Markdown')
        return

    # Начало заявки
    if data.startswith('order_'):
        product = data.replace('order_', '')
        context.user_data['product'] = product
        label = PRODUCT_NAMES.get(product, product)
        await query.edit_message_text(
            f"📋 *Заявка — {label}*\n\nВведите ваше имя:",
            reply_markup=cancel_kb(),
            parse_mode='Markdown',
        )
        return WAITING_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text(
        "📞 Введите ваш номер телефона:",
        reply_markup=cancel_kb(),
    )
    return WAITING_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name    = context.user_data.get('name', '—')
    phone   = update.message.text.strip()
    product = context.user_data.get('product', '—')

    try:
        await send_lead(name, phone, product)
    except Exception as e:
        logger.error("Failed to send lead: %s", e)

    await update.message.reply_text(
        "✅ *Заявка принята!*\n\nМенеджер свяжется с вами в течение 30 минут.",
        parse_mode='Markdown',
    )
    await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_kb())
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    query = update.callback_query
    if query:
        await query.answer()
    await start(update, context)
    return ConversationHandler.END


# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT2_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button, pattern=r'^order_')],
        states={
            WAITING_NAME:  [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
                CallbackQueryHandler(cancel, pattern='^main_menu$'),
            ],
            WAITING_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                CallbackQueryHandler(cancel, pattern='^main_menu$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == '__main__':
    main()
