import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
import json
import time
import hashlib
import os
import re
import random

# ============= НАСТРОЙКИ =============

# Получаем токен из переменных окружения Bothost
TOKEN = os.getenv('BOT_TOKEN')

# Проверяем, что токен загрузился
if not TOKEN:
    print("=" * 50)
    print("❌ ОШИБКА: Не найден BOT_TOKEN в переменных окружении Bothost!")
    print("✅ Убедитесь, что в настройках бота есть переменная BOT_TOKEN")
    exit(1)

print(f"✅ Токен загружен с Bothost! Начинается на: {TOKEN[:15]}...")

OWNER_ID = 6397071501
CHANNEL = "@SaulGoodmanScript"
BOT_USERNAME = "SaulScript_Bot"

bot = telebot.TeleBot(TOKEN)

# ============= КОНФИГУРАЦИЯ ДОНАТОВ =============

# Цены в Telegram Stars (1 Star = $0.01)
STARS_PACKAGES = {
    "10": 10,     # 10 stars
    "25": 25,     # 25 stars
    "50": 50,     # 50 stars
    "100": 100,   # 100 stars
    "250": 250,   # 250 stars
    "500": 500,   # 500 stars
}

# Описания пакетов
STARS_DESCRIPTIONS = {
    "10": "10 ⭐ - Базовая поддержка",
    "25": "25 ⭐ - Небольшой донат",
    "50": "50 ⭐ - Средний донат",
    "100": "100 ⭐ - Значительная помощь",
    "250": "250 ⭐ - Большой донат",
    "500": "500 ⭐ - Максимальная поддержка",
}

# ============= КОМАНДА ДОНАТ =============

@bot.message_handler(commands=['donate', 'donates', 'stars'])
def donate_command(message):
    """Показывает меню донатов"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Создаем кнопки для выбора количества звезд
    buttons = []
    for stars in STARS_PACKAGES.keys():
        buttons.append(
            InlineKeyboardButton(
                f"{stars} ⭐", 
                callback_data=f"donate_{stars}"
            )
        )
    
    # Добавляем кнопки в два столбца
    for i in range(0, len(buttons), 2):
        if i+1 < len(buttons):
            markup.row(buttons[i], buttons[i+1])
        else:
            markup.row(buttons[i])
    
    # Кнопка "Другой размер"
    markup.row(InlineKeyboardButton("🎁 Другой размер", callback_data="donate_custom"))
    
    bot.send_message(
        message.chat.id,
        "🌟 **Поддержать разработчика**\n\n"
        "Выберите количество звезд для доната:\n"
        "• 10 ⭐ - Базовая поддержка\n"
        "• 25 ⭐ - Небольшой донат\n"
        "• 50 ⭐ - Средний донат\n"
        "• 100 ⭐ - Значительная помощь\n"
        "• 250 ⭐ - Большой донат\n"
        "• 500 ⭐ - Максимальная поддержка\n\n"
        "💫 Каждая звезда помогает развитию бота!",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ============= ОБРАБОТКА ВЫБОРА ДОНАТА =============

@bot.callback_query_handler(func=lambda call: call.data.startswith('donate_'))
def handle_donate_selection(call):
    """Обрабатывает выбор количества звезд"""
    if call.data == "donate_custom":
        # Запрос произвольной суммы
        msg = bot.send_message(
            call.message.chat.id,
            "💫 Введите произвольное количество звезд (от 10 до 1000):"
        )
        bot.register_next_step_handler(msg, process_custom_donate)
        bot.answer_callback_query(call.id)
        return
    
    stars_amount = call.data.replace('donate_', '')
    
    if stars_amount not in STARS_PACKAGES:
        bot.answer_callback_query(call.id, "❌ Неверный выбор")
        return
    
    stars_count = STARS_PACKAGES[stars_amount]
    description = STARS_DESCRIPTIONS.get(stars_amount, f"{stars_amount} звезд")
    
    # Создаем инвойс для Telegram Stars
    try:
        prices = [LabeledPrice(label=f"{stars_amount} Telegram Stars", amount=stars_count)]
        
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f"Донат {stars_amount} ⭐",
            description=description,
            invoice_payload=f"donate_{stars_amount}_{call.from_user.id}",
            provider_token="",  # Для Telegram Stars оставляем пустым
            currency="XTR",  # Код валюты для Telegram Stars
            prices=prices,
            start_parameter="donate",
            photo_url="https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/Resources/art/icon256.png",
            photo_size=100,
            photo_width=256,
            photo_height=256,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            f"❌ Ошибка при создании платежа: {str(e)}"
        )
    
    bot.answer_callback_query(call.id)

def process_custom_donate(message):
    """Обрабатывает произвольную сумму доната"""
    try:
        stars = int(message.text.strip())
        
        if stars < 10:
            bot.send_message(message.chat.id, "❌ Минимальное количество звезд - 10")
            return
        if stars > 1000:
            bot.send_message(message.chat.id, "❌ Максимальное количество звезд - 1000")
            return
        
        # Создаем инвойс для произвольной суммы
        prices = [LabeledPrice(label=f"{stars} Telegram Stars", amount=stars)]
        
        bot.send_invoice(
            chat_id=message.chat.id,
            title=f"Донат {stars} ⭐",
            description=f"Произвольный донат {stars} звезд",
            invoice_payload=f"donate_custom_{stars}_{message.from_user.id}",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="donate_custom",
            photo_url="https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/Resources/art/icon256.png",
            photo_size=100,
            photo_width=256,
            photo_height=256,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите число")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

# ============= ОБРАБОТКА УСПЕШНОГО ПЛАТЕЖА =============

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    """Обрабатывает предварительный запрос на оплату"""
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    """Обрабатывает успешный платеж"""
    try:
        payload = message.successful_payment.invoice_payload
        user_id = message.from_user.id
        stars_amount = 0
        
        # Извлекаем количество звезд из payload
        if payload.startswith("donate_"):
            parts = payload.split("_")
            if len(parts) >= 2:
                if parts[1] == "custom" and len(parts) >= 3:
                    stars_amount = int(parts[2])
                elif parts[1] in STARS_PACKAGES:
                    stars_amount = STARS_PACKAGES[parts[1]]
        
        # Отправляем благодарность пользователю
        bot.send_message(
            message.chat.id,
            f"🎉 **Спасибо за донат!**\n\n"
            f"Вы успешно отправили {stars_amount} ⭐\n"
            f"Ваша поддержка очень важна для развития бота!\n\n"
            f"💫 Спасибо за помощь!",
            parse_mode="Markdown"
        )
        
        # Уведомляем владельца
        bot.send_message(
            OWNER_ID,
            f"💰 **Новый донат!**\n\n"
            f"👤 Пользователь: @{message.from_user.username or 'Нет username'}\n"
            f"🆔 ID: {user_id}\n"
            f"⭐ Звезд: {stars_amount}\n"
            f"💳 Сумма: {message.successful_payment.total_amount / 100:.2f} USD",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        print(f"Ошибка обработки платежа: {e}")

# ============= ОБНОВЛЕННЫЙ СТАРТ =============

@bot.message_handler(commands=['start'])
def start(message):
    # ВСЕГДА загружаем свежие данные
    SCRIPTS_DATABASE = load_scripts_dynamic()

    args = message.text.split()

    if len(args) > 1:
        key = args[1].upper()

        print(f"🔑 Запрос ключа: {key}")
        print(f"📊 Доступно ключей: {list(SCRIPTS_DATABASE.keys())}")

        if key in SCRIPTS_DATABASE:
            script = SCRIPTS_DATABASE[key]
            script['uses'] = script.get('uses', 0) + 1

            # Сохраняем обновленные данные
            save_scripts_dynamic(SCRIPTS_DATABASE)

            text = f"📌 {script['game_name']}\n\n"
            text += f"📥 Код для эксплоита:\n`{script['loadstring']}`\n\n"

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
                InlineKeyboardButton("🤝 Партнёр", url="https://t.me/loriscript"),
                InlineKeyboardButton("🌟 Поддержать", callback_data="donate_menu")
            )

            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(
                message.chat.id,
                f"❌ Скрипт не найден!\n\n"
                f"🔑 Ключ: `{key}`\n"
                f"📦 Всего скриптов: {len(SCRIPTS_DATABASE)}\n"
                f"📋 Ключи: {', '.join(list(SCRIPTS_DATABASE.keys())[:5])}...",
                parse_mode="Markdown"
            )
        return

    # Обычный старт без ключа
    SCRIPTS_DATABASE = load_scripts_dynamic()

    # Создаем меню
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
        InlineKeyboardButton("🌟 Поддержать", callback_data="donate_menu")
    )
    
    if message.from_user.id == OWNER_ID:
        total_uses = sum(s.get('uses', 0) for s in SCRIPTS_DATABASE.values())
        bot.send_message(
            message.chat.id,
            f"👑 Создатель SaulGoodmanScript\n\n"
            f"📊 Статистика:\n"
            f"• Скриптов в базе: {len(SCRIPTS_DATABASE)}\n"
            f"• Всего скачиваний: {total_uses}\n\n"
            f"Отправь фото (если нужно) и текст в формате:\n\n"
            f"Название игры\n---\nURL\n---\nОписание через +",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "👋 Добро пожаловать!\n\n"
            f"📢 Канал: @SaulGoodmanScript\n"
            f"📦 Доступно скриптов: {len(SCRIPTS_DATABASE)}\n\n"
            f"🌟 Поддержите развитие бота - ваш донат поможет добавить больше скриптов!",
            reply_markup=markup
        )

# ============= КНОПКА ДОНАТА В МЕНЮ =============

@bot.callback_query_handler(func=lambda call: call.data == "donate_menu")
def show_donate_menu(call):
    """Показывает меню донатов при нажатии на кнопку"""
    donate_command(call.message)
    bot.answer_callback_query(call.id)

# ============= ОСТАЛЬНЫЕ ФУНКЦИИ (без изменений) =============

@bot.message_handler(commands=['check'])
def check_key_command(message):
    if message.from_user.id != OWNER_ID:
        return

    SCRIPTS_DATABASE = load_scripts_dynamic()

    args = message.text.split()
    if len(args) > 1:
        key = args[1].upper()

        if key in SCRIPTS_DATABASE:
            script = SCRIPTS_DATABASE[key]
            test_link = f"https://t.me/{BOT_USERNAME}?start={key}"

            bot.send_message(
                message.chat.id,
                f"✅ Ключ найден!\n\n"
                f"🔑 `{key}`\n"
                f"🎮 {script['game_name']}\n"
                f"🔗 {script['url']}\n"
                f"📅 {script['date']}\n"
                f"👥 Использований: {script.get('uses', 0)}\n\n"
                f"Тестовая ссылка:\n{test_link}",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"❌ Ключ `{key}` не найден!\n\n"
                f"Доступные ключи: {', '.join(list(SCRIPTS_DATABASE.keys())[:10])}...",
                parse_mode="Markdown"
            )
    else:
        keys_list = "\n".join([f"• `{k}` - {SCRIPTS_DATABASE[k]['game_name']}" for k in SCRIPTS_DATABASE.keys()])
        bot.send_message(
            message.chat.id,
            f"🗝 Все ключи в базе ({len(SCRIPTS_DATABASE)}):\n\n{keys_list}",
            parse_mode="Markdown"
        )

# ============= ДОБАВЛЕНИЕ СКРИПТОВ =============

temp_data = {}

def generate_unique_key(game_name):
    """Генерирует уникальный ключ"""
    SCRIPTS_DATABASE = load_scripts_dynamic()

    for attempt in range(10):
        unique_data = f"{game_name}{time.time()}{random.randint(1000, 999999)}"
        key = hashlib.md5(unique_data.encode()).hexdigest()[:8].upper()

        if key not in SCRIPTS_DATABASE:
            return key

    return hashlib.md5(f"{game_name}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id != OWNER_ID:
        return

    user_id = str(message.from_user.id)
    if user_id not in temp_data:
        temp_data[user_id] = {}

    temp_data[user_id]['photo'] = message.photo[-1].file_id
    bot.reply_to(message, "✅ Фото сохранено! Теперь отправь текст.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id != OWNER_ID:
        return

    SCRIPTS_DATABASE = load_scripts_dynamic()
    user_id = str(message.from_user.id)

    if message.text.startswith('/'):
        return

    parts = message.text.split('\n---\n')
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Неправильный формат!")
        return

    game_name = parts[0].strip()
    url = parts[1].strip()
    description = parts[2].strip()

    if not url.startswith(('http://', 'https://')):
        bot.send_message(message.chat.id, "❌ Неверный URL")
        return

    key = generate_unique_key(game_name)
    loadstring = f'loadstring(game:HttpGet("{url}"))()'

    if user_id not in temp_data:
        temp_data[user_id] = {}

    temp_data[user_id].update({
        'game_name': game_name,
        'url': url,
        'description': description,
        'loadstring': loadstring,
        'key': key,
        'has_photo': 'photo' in temp_data[user_id]
    })

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👁️ Предпросмотр", callback_data=f"preview_{user_id}"),
        InlineKeyboardButton("🚀 Опубликовать", callback_data=f"publish_{user_id}"),
        InlineKeyboardButton("💾 Сохранить в базу", callback_data=f"save_{user_id}")
    )

    bot.send_message(
        message.chat.id,
        f"✅ Данные получены!\n"
        f"🎮 Игра: {game_name}\n"
        f"🔑 Ключ: `{key}`\n"
        f"📷 Фото: {'Да' if 'photo' in temp_data[user_id] else 'Нет'}\n"
        f"📊 Текущее кол-во скриптов: {len(SCRIPTS_DATABASE)}\n\n"
        f"Выберите действие:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ============= CALLBACK HANDLERS =============

@bot.callback_query_handler(func=lambda call: call.data.startswith('publish_'))
def publish_script(call):
    user_id = call.data.replace('publish_', '')

    if user_id not in temp_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены")
        return

    data = temp_data[user_id]
    key = data['key']

    SCRIPTS_DATABASE = load_scripts_dynamic()

    SCRIPTS_DATABASE[key] = {
        'game_name': data['game_name'],
        'url': data['url'],
        'description': data['description'],
        'loadstring': data['loadstring'],
        'date': time.strftime("%d.%m.%Y %H:%M"),
        'uses': 0
    }

    save_scripts_dynamic(SCRIPTS_DATABASE)

    post_text = f"📌 {data['game_name']} SCRIPT!\n{data['description']}\n\n"
    post_text += f"⚡️Гайд как скачать\n@saulGoodmanScript_Guides\n\n"
    post_text += f"🤖Получить ключ от Delta\nhttps://keybypass.net/ \n\n"
    post_text += f"❓️Как использовать\n1. Копируете код выше\n2. Вставляете в ваш эксплоит\n3. Нажимаете Execute\n\n"
    post_text += f" Больше скриптов: @SaulGoodmanScript\n🤝 Партнёр: @loriscript"

    bot_link = f"https://t.me/{BOT_USERNAME}?start={key}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📥 Получить скрипт", url=bot_link))

    try:
        if data.get('has_photo') and 'photo' in data:
            bot.send_photo(CHANNEL, photo=data['photo'], caption=post_text, reply_markup=markup)
        else:
            bot.send_message(CHANNEL, post_text, reply_markup=markup, disable_web_page_preview=True)

        bot.send_message(
            call.message.chat.id,
            f"✅ Опубликовано и сохранено в базу!\n"
            f"🔑 Ключ: `{key}`\n"
            f"📊 Всего скриптов: {len(SCRIPTS_DATABASE)}\n\n"
            f"Тестовая ссылка: {bot_link}",
            parse_mode="Markdown"
        )

        if user_id in temp_data:
            del temp_data[user_id]

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {str(e)}")

    bot.answer_callback_query(call.id)

# ============= ЗАПУСК БОТА =============

print("=" * 50)
print("🤖 Бот запущен на Bothost!")
print("⭐ Система донатов активирована")
print("=" * 50)

try:
    bot.polling(none_stop=True, skip_pending=True, timeout=30)
except Exception as e:
    print(f"❌ Ошибка: {e}")