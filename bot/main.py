import asyncio
import logging
import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT2_TOKEN      = '8929239888:AAH1rvoNcAb3RM88FM64rEiKQr7RmOqkew8'
LEADS_BOT_TOKEN = '8650746508:AAEUc9iDvWD0GdGGcSaHHZFMphuwaaQqT7g'
CHAT_ID         = '490873482'

WAITING_NAME  = 1
WAITING_PHONE = 2

# Пути к изображениям (относительно папки bot/)
BASE = os.path.dirname(os.path.abspath(__file__))
IMG  = os.path.join(BASE, '..', 'images')

PHOTOS = {
    'welcome':  os.path.join(IMG, 'Логотип',         'Логотип.png'),
    'brick':    os.path.join(IMG, 'Наша продукция',  'облицовочный кирпич.png'),
    'tile':     os.path.join(IMG, 'Наша продукция',  'облицовочная плитка.png'),
    'paving':   os.path.join(IMG, 'Наша продукция',  'Тротуарная плитка.png'),
    'tech':     os.path.join(IMG, 'Технология',      'технология.jpg'),
}

PORTFOLIO_PHOTOS = [
    os.path.join(IMG, 'Портфолио', 'кирпич1.jpg'),
    os.path.join(IMG, 'Портфолио', 'кирпич2.jpg'),
    os.path.join(IMG, 'Портфолио', 'кирпич3.jpg'),
    os.path.join(IMG, 'Портфолио', 'плитка1.jpg'),
    os.path.join(IMG, 'Портфолио', 'плитка2.jpg'),
    os.path.join(IMG, 'Портфолио', 'плитка3.jpg'),
    os.path.join(IMG, 'Портфолио', 'оплитка1.jpg'),
    os.path.join(IMG, 'Портфолио', 'оплитка2.jpg'),
    os.path.join(IMG, 'Портфолио', 'оплитка3.jpg'),
]

PRODUCT_NAMES = {
    'brick':  '🧱 Кирпич',
    'tile':   '🪨 Плитка',
    'paving': '🟫 Тротуарная плитка',
    'price':  '💰 Прайс-лист',
}


# ──────────────────────────────────────────────
# Клавиатуры
# ──────────────────────────────────────────────
MINI_APP_URL = 'https://djalaev222-arch.github.io/novobricks/app.html'

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Открыть квиз / заявку",
                              web_app=WebAppInfo(url=MINI_APP_URL))],
        [InlineKeyboardButton("🧱 Кирпич",           callback_data="brick"),
         InlineKeyboardButton("🪨 Плитка",            callback_data="tile")],
        [InlineKeyboardButton("🟫 Тротуарная плитка", callback_data="paving")],
        [InlineKeyboardButton("🎨 Палитра цветов",    callback_data="colors"),
         InlineKeyboardButton("📸 Наши объекты",      callback_data="portfolio")],
        [InlineKeyboardButton("💰 Получить прайс",    callback_data="order_price"),
         InlineKeyboardButton("📞 Контакты",          callback_data="contacts")],
    ])

def product_kb(product):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Оставить заявку", callback_data=f"order_{product}")],
        [InlineKeyboardButton("⬅️ Главное меню",    callback_data="main_menu")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]])

def cancel_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]])


# ──────────────────────────────────────────────
# Вспомогательные функции
# ──────────────────────────────────────────────
async def delete_message(update: Update):
    """Удаляет текущее сообщение (если возможно)."""
    try:
        if update.callback_query:
            await update.callback_query.message.delete()
    except Exception:
        pass


async def send_photo_msg(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         photo_key: str, caption: str, keyboard):
    """Удаляет старое сообщение и отправляет фото с подписью и кнопками."""
    await delete_message(update)
    chat_id = (update.callback_query or update).message.chat_id if update.callback_query \
              else update.message.chat_id

    photo_path = PHOTOS.get(photo_key, '')
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as f:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=f,
                caption=caption,
                reply_markup=keyboard,
                parse_mode='Markdown',
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=keyboard,
            parse_mode='Markdown',
        )


async def send_text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE,
                        text: str, keyboard):
    """Удаляет старое сообщение и отправляет текст с кнопками."""
    await delete_message(update)
    chat_id = update.callback_query.message.chat_id if update.callback_query \
              else update.message.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        parse_mode='Markdown',
    )


# ──────────────────────────────────────────────
# Отправка заявки в бот №1
# ──────────────────────────────────────────────
async def send_lead(name: str, phone: str, product: str):
    text = (
        f"*Заявка из Telegram-бота*\n\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Интерес: {PRODUCT_NAMES.get(product, product)}"
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
    caption = (
        "*NovoBricks* — гиперпрессованный кирпич и плитка из Башкирии\n\n"
        "Срок службы в 12 раз выше силикатного\n"
        "14 цветов — 22 типоразмера — доставка по РФ\n\n"
        "Выберите раздел:"
    )
    if update.callback_query:
        await send_photo_msg(update, context, 'welcome', caption, main_menu_kb())
    else:
        chat_id = update.message.chat_id
        photo_path = PHOTOS['welcome']
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as f:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=f,
                    caption=caption,
                    reply_markup=main_menu_kb(),
                    parse_mode='Markdown',
                )
        else:
            await update.message.reply_text(caption, reply_markup=main_menu_kb(), parse_mode='Markdown')


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'main_menu':
        await start(update, context)
        return

    # ── Кирпич ───────────────────────────────
    if data == 'brick':
        await send_photo_msg(update, context, 'brick',
            "🧱 *Облицовочный кирпич NovoBricks*\n\n"
            "• Прочность М300 — в 3 раза выше стандарта\n"
            "• Морозостойкость F150\n"
            "• Водопоглощение < 6%\n"
            "• Срок службы в 12 раз выше силикатного\n"
            "• 14 цветов, 22 типоразмера\n\n"
            "Цена: *от 28 ₽/шт*\n"
            "Доставка по РФ от 3 дней",
            product_kb('brick'))
        return

    # ── Плитка ───────────────────────────────
    if data == 'tile':
        await send_photo_msg(update, context, 'tile',
            "🪨 *Облицовочная плитка NovoBricks*\n\n"
            "• Гиперпрессованная технология\n"
            "• Толщина 20–40 мм\n"
            "• Устойчива к морозу и влаге\n"
            "• 14 цветов\n\n"
            "Цена: *от 850 ₽/м²*\n"
            "Доставка по РФ от 3 дней",
            product_kb('tile'))
        return

    # ── Тротуарная плитка ────────────────────
    if data == 'paving':
        await send_photo_msg(update, context, 'paving',
            "🟫 *Тротуарная плитка NovoBricks*\n\n"
            "• Нагрузка до 40 тонн\n"
            "• Морозостойкость F200\n"
            "• Антискользящая поверхность\n"
            "• 8 форм, 10 цветов\n\n"
            "Цена: *от 650 ₽/м²*\n"
            "Доставка по РФ от 3 дней",
            product_kb('paving'))
        return

    # ── Палитра ──────────────────────────────
    if data == 'colors':
        await send_text_msg(update, context,
            "🎨 *Палитра NovoBricks — 14 цветов*\n\n"
            "🔴 Красный классический\n"
            "🟤 Коричневый\n"
            "⚫ Антрацит\n"
            "⚪ Белый\n"
            "🟡 Песочный / бежевый\n"
            "🟠 Терракот\n"
            "…и ещё 8 оттенков\n\n"
            "Для получения образцов — оставьте заявку!",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Заказать образцы", callback_data="order_colors")],
                [InlineKeyboardButton("⬅️ Главное меню",    callback_data="main_menu")],
            ]))
        return

    # ── Портфолио ────────────────────────────
    if data == 'portfolio':
        chat_id = query.message.chat_id
        await delete_message(update)

        existing = [p for p in PORTFOLIO_PHOTOS if os.path.exists(p)]
        if existing:
            files = [open(p, 'rb') for p in existing]
            try:
                media = [InputMediaPhoto(media=f) for f in files]
                media[0] = InputMediaPhoto(
                    media=files[0],
                    caption="📸 *Наши объекты*\nРеализованные проекты по Башкирии и России",
                    parse_mode='Markdown',
                )
                await context.bot.send_media_group(chat_id=chat_id, media=media)
            finally:
                for f in files:
                    f.close()

        await context.bot.send_message(
            chat_id=chat_id,
            text="Хотите реализовать похожий проект?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Оставить заявку", callback_data="order_paving")],
                [InlineKeyboardButton("⬅️ Главное меню",    callback_data="main_menu")],
            ]),
        )
        return

    # ── Контакты ─────────────────────────────
    if data == 'contacts':
        await send_text_msg(update, context,
            "📞 *Контакты NovoBricks*\n\n"
            "📱 +7 (964) 95-95-095\n"
            "📧 info@novobricks.ru\n\n"
            "🏢 *Офис:*\n"
            "Уфа, ул. Строительная, 1, офис 201\n"
            "Пн–Пт: 9:00–18:00\n\n"
            "🏭 *Завод:*\n"
            "Белорецк, ул. Заводская, 14",
            back_kb())
        return

    # ── Начало заявки ────────────────────────
    if data.startswith('order_'):
        product = data.replace('order_', '')
        context.user_data['product'] = product
        label = PRODUCT_NAMES.get(product, product)
        await send_text_msg(update, context,
            f"📋 *Заявка — {label}*\n\nВведите ваше имя:",
            cancel_kb())
        return WAITING_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("📞 Введите ваш номер телефона:", reply_markup=cancel_kb())
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
        "Заявка принята!\n\nМенеджер свяжется с вами в течение 30 минут.",
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
    app = (
        Application.builder()
        .token(BOT2_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

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

    print("Бот NovoBricks запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()


if __name__ == '__main__':
    main()
