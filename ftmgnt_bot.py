#!/usr/bin/env python3
"""
FtMgnt B2B Telegram Bot
Прогрев B2B клиентов для магнитов ftmgnt.kz · Астана
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes,
)

# ─── КОНФИГУРАЦИЯ ───────────────────────────────────────────────────────────
BOT_TOKEN  = "8742153640:AAF8QBcxa3yby7sv8jSphzoQHnPkSW5sbCk"
MANAGER_ID = 5027017425          # Telegram ID менеджера (Baglan)
WHATSAPP   = "https://wa.me/77477061513"  # ← замените на свой номер WhatsApp
SITE_URL   = "https://ftmgnt.kz/ftmgnt-b2b.html"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── ТЕКСТЫ ─────────────────────────────────────────────────────────────────
WELCOME = (
    "👋 Привет! Я помогу подобрать магниты для вашего бизнеса.\n\n"
    "FtMgnt — производство магнитов оптом в Астане:\n"
    "✅ 1 098 дизайнов на выбор\n"
    "✅ Тираж от 50 штук\n"
    "✅ Kaspi Pay · Kaspi Express · Счёт для юрлиц\n"
    "⭐ 171 отзыв, рейтинг 5/5\n\n"
    "Выберите тип вашего бизнеса — покажу лучший вариант 👇"
)

CATEGORIES = {
    "coffee": {
        "label": "☕ Кофейня / ресторан",
        "pitch": (
            "☕ *Магниты для кофеен — это работающий инструмент!*\n\n"
            "→ Средний чек +10–15%: гости покупают «на память»\n"
            "→ Магнит на холодильнике = реклама у 10+ знакомых каждый день\n"
            "→ Уникальный брендинг, которого нет у конкурентов\n\n"
            "*Популярные форматы:*\n"
            "• Ваш логотип + адрес на стилизованном магните\n"
            "• Серия «Астана» с вашим брендингом\n"
            "• Сезонные лимитки (Новый год, 8 марта, Наурыз)\n\n"
            "🎯 Минимум 50 шт — окупается с первой недели продаж у стойки."
        ),
    },
    "travel": {
        "label": "✈️ Турагентство",
        "pitch": (
            "✈️ *Магниты для турагентств — умный инструмент удержания!*\n\n"
            "→ Подарок клиенту после тура = лояльность и повторные обращения\n"
            "→ Магнит с вашим лого висит у клиента годами — это бесплатная реклама\n"
            "→ Идеально для welcome-kit, корпоративных туров, VIP-клиентов\n\n"
            "*Что заказывают турагентства:*\n"
            "• Магниты стран и городов с вашим лого\n"
            "• Брендированные сувениры для клиентского пакета\n"
            "• Подарки партнёрам и корпоративным группам\n\n"
            "🎯 От 50 шт, документы для юрлиц, оплата Kaspi или счёт-фактура."
        ),
    },
    "wedding": {
        "label": "💍 Свадебное агентство",
        "pitch": (
            "💍 *Свадебные магниты — самый тёплый подарок гостям!*\n\n"
            "→ Персональный магнит с именами и датой = память на годы\n"
            "→ Каждый гость уносит частичку праздника домой\n"
            "→ Ваше агентство получает WOW-эффект и рекомендации\n\n"
            "*Форматы для свадеб:*\n"
            "• Имена + дата + фото пары\n"
            "• Дизайн в стиле свадьбы (цвета, цветы, шрифты)\n"
            "• Упаковка в конверт или крафтовую коробочку\n\n"
            "🎯 От 50 шт, срок 3–5 дней, печать с вашего фото."
        ),
    },
    "souvenir": {
        "label": "🏪 Сувенирный магазин",
        "pitch": (
            "🏪 *Сувенирные магазины — наши ключевые партнёры!*\n\n"
            "→ Готовый ассортимент 1 098 дизайнов — Астана, Казахстан, флаги, мультиперсонажи\n"
            "→ Оптовая цена от 100 шт + все документы для закупки\n"
            "→ Вся продукция в наличии, отгрузка день-в-день\n\n"
            "*Популярные серии:*\n"
            "• «Астана» — достопримечательности, Байтерек, ЭКСПО\n"
            "• «Казахстан» — природа, степи, национальная символика\n"
            "• Флаги мира · Мультиперсонажи\n\n"
            "🎯 Работаем с ИП и ТОО: счёт-фактура, накладная, приходной ордер."
        ),
    },
    "event": {
        "label": "🎪 Event / корпоратив",
        "pitch": (
            "🎪 *Корпоративный брендинг с магнитами — инструмент, который помнят!*\n\n"
            "→ Магнит с лого компании = мерч, который не выбрасывают\n"
            "→ Дешевле ручки, памятнее блокнота — идеально для форумов и конференций\n"
            "→ Участник видит ваш бренд каждый день на холодильнике\n\n"
            "*Форматы для event:*\n"
            "• Логотип + дата + слоган события\n"
            "• Серийный выпуск для участников (100–5 000 шт)\n"
            "• Брендинг под фирменные цвета компании\n\n"
            "🎯 От 50 шт, срок 3–5 дней, счёт для юрлиц."
        ),
    },
    "other": {
        "label": "🏢 Другой бизнес",
        "pitch": (
            "🏢 *Расскажите о вашем бизнесе — найдём решение!*\n\n"
            "FtMgnt делает магниты для любого бизнеса в Астане и по всему Казахстану.\n\n"
            "✅ Дизайн под ваш бренд — бесплатно\n"
            "✅ Тираж от 50 штук\n"
            "✅ Срок: 3–5 рабочих дней\n"
            "✅ Kaspi Express — доставка за 3 часа по Астане\n\n"
            "Напишите ниже: сколько штук нужно и для какого повода? 👇"
        ),
    },
}

FAQ = {
    "price": (
        "💰 *Цены FtMgnt:*\n\n"
        "• 50–99 шт → ~800–1 200 тг/шт\n"
        "• 100–299 шт → ~600–900 тг/шт\n"
        "• 300–999 шт → ~400–700 тг/шт\n"
        "• 1 000+ шт → индивидуальная цена\n\n"
        "*Дизайн входит в стоимость.*\n"
        "Точная цена зависит от размера и типа магнита.\n"
        "Напишем КП за 10 минут 🚀"
    ),
    "timing": (
        "⏱ *Сроки изготовления:*\n\n"
        "• Стандарт: 3–5 рабочих дней\n"
        "• Срочный заказ: 1–2 дня (+30% к цене)\n"
        "• Экспресс день-в-день: уточняйте наличие\n\n"
        "📦 *Доставка:*\n"
        "• Kaspi Express — 3 часа по Астане\n"
        "• Казпочта / СДЭК — по всему Казахстану\n"
        "• Самовывоз — Астана, центр"
    ),
    "kaspi": (
        "📱 *Оплата:*\n\n"
        "✅ Kaspi Pay (QR-код и Kaspi Gold)\n"
        "✅ Kaspi рассрочка 0-0-12 (для физлиц)\n"
        "✅ Счёт для юрлиц (ТОО, ИП)\n"
        "✅ Наличные при самовывозе\n\n"
        "Наш магазин на Kaspi:\n"
        "⭐ 171 отзыв · рейтинг 5 из 5"
    ),
    "minimum": (
        "📦 *Минимальный заказ:*\n\n"
        "→ От *50 штук* — дизайн из каталога (1 098 вариантов)\n"
        "→ От *100 штук* — индивидуальный дизайн с вашим логотипом\n"
        "→ От *300 штук* — оптовая цена + приоритет в очереди\n\n"
        "Есть дизайн? Пришлите — оценим стоимость за 10 минут."
    ),
}


# ─── КЛАВИАТУРЫ ──────────────────────────────────────────────────────────────
def kb_categories():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("☕ Кофейня / ресторан",     callback_data="cat_coffee")],
        [InlineKeyboardButton("✈️ Турагентство",           callback_data="cat_travel")],
        [InlineKeyboardButton("💍 Свадебное агентство",    callback_data="cat_wedding")],
        [InlineKeyboardButton("🏪 Сувенирный магазин",     callback_data="cat_souvenir")],
        [InlineKeyboardButton("🎪 Event / корпоратив",     callback_data="cat_event")],
        [InlineKeyboardButton("🏢 Другой бизнес",          callback_data="cat_other")],
    ])

def kb_after_pitch():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Сколько стоит?",           callback_data="faq_price")],
        [InlineKeyboardButton("⏱ Сроки изготовления?",      callback_data="faq_timing")],
        [InlineKeyboardButton("📦 Минимальный заказ?",       callback_data="faq_minimum")],
        [InlineKeyboardButton("📱 Kaspi / оплата?",          callback_data="faq_kaspi")],
        [InlineKeyboardButton("🎯 Хочу заказать!",           callback_data="want_order")],
        [InlineKeyboardButton("👨‍💼 Написать менеджеру",      callback_data="to_manager")],
    ])

def kb_after_faq():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Другой вопрос",            callback_data="back_faq")],
        [InlineKeyboardButton("🎯 Хочу заказать!",           callback_data="want_order")],
        [InlineKeyboardButton("👨‍💼 Написать менеджеру",      callback_data="to_manager")],
    ])

def kb_faq():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Цены",        callback_data="faq_price"),
            InlineKeyboardButton("⏱ Сроки",        callback_data="faq_timing"),
        ],
        [
            InlineKeyboardButton("📱 Kaspi/оплата", callback_data="faq_kaspi"),
            InlineKeyboardButton("📦 Минимум",      callback_data="faq_minimum"),
        ],
        [InlineKeyboardButton("🎯 Хочу заказать!",           callback_data="want_order")],
        [InlineKeyboardButton("👨‍💼 Написать менеджеру",      callback_data="to_manager")],
    ])


# ─── ХЕЛПЕР: уведомление менеджеру ──────────────────────────────────────────
async def notify_manager(bot, user, category_key: str, extra: str = ""):
    cat_label = CATEGORIES.get(category_key, {}).get("label", "—")
    name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "Без имени"
    uname = f"@{user.username}" if user.username else "нет username"
    msg = (
        f"🔔 *Новый лид в боте!*\n\n"
        f"👤 {name}\n"
        f"📱 {uname}\n"
        f"🆔 `{user.id}`\n"
        f"🏢 Категория: {cat_label}\n"
        + (f"\n💬 {extra}" if extra else "")
    )
    try:
        await bot.send_message(chat_id=MANAGER_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка уведомления менеджеру: {e}")


# ─── ХЕНДЛЕРЫ ────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(WELCOME, reply_markup=kb_categories())


async def on_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cat_key = q.data.replace("cat_", "")
    context.user_data["category"] = cat_key
    cat = CATEGORIES.get(cat_key, CATEGORIES["other"])
    await q.edit_message_text(cat["pitch"], parse_mode="Markdown",
                              reply_markup=kb_after_pitch())


async def on_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    faq_key = q.data.replace("faq_", "")
    text = FAQ.get(faq_key, "Уточните вопрос у менеджера.")
    await q.edit_message_text(text, parse_mode="Markdown",
                              reply_markup=kb_after_faq())


async def on_back_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("Выберите вопрос 👇", reply_markup=kb_faq())


async def on_want_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["collecting_order"] = True
    await q.edit_message_text(
        "✍️ *Отлично! Расскажите о заказе:*\n\n"
        "Напишите одним сообщением:\n"
        "1️⃣ Сколько штук нужно?\n"
        "2️⃣ Для чего / какого события?\n"
        "3️⃣ Ваш номер телефона или @username\n\n"
        "_Менеджер ответит в течение 15 минут_ ⚡",
        parse_mode="Markdown"
    )


async def on_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cat_key = context.user_data.get("category", "other")
    await notify_manager(context.bot, q.from_user, cat_key,
                         extra="Клиент нажал «Написать менеджеру»")
    await q.edit_message_text(
        "👨‍💼 *Передаю вас менеджеру!*\n\n"
        "Менеджер свяжется с вами в течение 15 минут ⚡\n\n"
        f"Пока ждёте — посмотрите каталог:\n{SITE_URL}",
        parse_mode="Markdown"
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Любое текстовое сообщение от клиента — переслать менеджеру."""
    user = update.message.from_user
    text = update.message.text
    cat_key = context.user_data.get("category", "other")

    await notify_manager(context.bot, user, cat_key,
                         extra=f"Сообщение клиента:\n«{text}»")

    await update.message.reply_text(
        "✅ *Получили!*\n\n"
        "Менеджер свяжется с вами в течение 15 минут ⚡\n\n"
        f"Пока ждёте — посмотрите каталог:\n{SITE_URL}",
        parse_mode="Markdown"
    )


# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_category,   pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(on_faq,        pattern=r"^faq_"))
    app.add_handler(CallbackQueryHandler(on_back_faq,   pattern=r"^back_faq$"))
    app.add_handler(CallbackQueryHandler(on_want_order, pattern=r"^want_order$"))
    app.add_handler(CallbackQueryHandler(on_to_manager, pattern=r"^to_manager$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    print("🤖 FtMgnt бот запущен. Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
