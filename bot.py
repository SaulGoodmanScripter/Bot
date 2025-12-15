import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
import hashlib
import os
import re
import random

# ============= НАСТРОЙКИ =============


# Получаем токен из окружения
TOKEN = os.getenv('BOT_TOKEN')

# Проверяем, что токен загрузился
if not TOKEN:
    print("=" * 50)
    print("❌ ОШИБКА: Не найден BOT_TOKEN в переменных окружения!")
    print("👉 Проверь на Bothost:")
    print("   1. Залогинься на bothost.ru")
    print("   2. Найди свой проект")
    print("   3. Перейди в 'Настройки' → 'Переменные окружения'")
    print("   4. Убедись, что есть переменная BOT_TOKEN")
    print("=" * 50)
    exit(1)  # Останавливаем бота

# Если токен есть, показываем часть для проверки
print(f"✅ Токен загружен! Начинается на: {TOKEN[:15]}...")
print(f"📏 Длина токена: {len(TOKEN)} символов")

OWNER_ID = 6397071501
CHANNEL = "@SaulGoodmanScript"
BOT_USERNAME = "SaulScript_Bot"

bot = telebot.TeleBot(TOKEN)

# ============= БАЗА СКРИПТОВ =============
SCRIPTS_DATABASE = {
    "757B96AA": {
        "game_name": "The forge",
        "url": "https://raw.githubusercontent.com/GiftStein1/pepehook-loader/refs/heads/main/loader.lua",
        "description": "+Без ключа\n+Без бана",
        "loadstring": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/GiftStein1/pepehook-loader/refs/heads/main/loader.lua"))()',
        "date": "08.12.2025 18:34",
        "uses": 1
    },
    "D758B054": {
        "game_name": "Grow a garden",
        "url": "https://raw.githubusercontent.com/furik-hub/X-HUB/976fce839fc5eb9aea586081b4e98b94b538c9bd/source.lua",
        "description": "+Без ключа\n+Без бана",
        "loadstring": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/furik-hub/X-HUB/976fce839fc5eb9aea586081b4e98b94b538c9bd/source.lua"))()',
        "date": "08.12.2025 18:34",
        "uses": 1
    },
    "757B96AA": {
        "game_name": "The forge",
        "url": "https://pastefy.app/67vPkIvz/raw",
        "description": "+Без ключа\n+Без бана",
        "loadstring": 'loadstring(game:HttpGet("https://pastefy.app/67vPkIvz/raw"))()',
        "date": "08.12.2025 18:34",
        "uses": 1
    },

    "1DBAD8ED": {
        "game_name": "99 nights in rhe forest ",
        "url": "https://raw.githubusercontent.com/GEC0/gec/refs/heads/main/Gec.Loader",
        "description": "+без ключа/n+без бана",
        "loadstring": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/GEC0/gec/refs/heads/main/Gec.Loader"))()',
        "date": "11.12.2025 15:36",
        "uses": 0
     },
    "E393D9B9": {
        "game_name": "Grow a garden",
        "url": "https://raw.githubusercontent.com/furik-hub/X-HUB/976fce839fc5eb9aea586081b4e98b94b538c9bd/source.lua",
        "description": "+Без ключа\n+Без бана",
        "loadstring": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/furik-hub/X-HUB/976fce839fc5eb9aea586081b4e98b94b538c9bd/source.lua"))()',
        "date": "13.12.2025 12:46",
        "uses": 1
    },
    "48791C56": {
        "game_name": "Universal",
        "url": "https://glot.io/snippets/h8id91ebrx/raw/supermanfly.lua",
        "description": "Fly с анимацией супер мена\n+без ключа\n+без бана",
        "loadstring": 'loadstring(game:HttpGet("https://glot.io/snippets/h8id91ebrx/raw/supermanfly.lua"))()',
        "date": "10.12.2025 00:00",
        "uses": 0
    }
}

# Расписание (если нужно)
SCHEDULE_DATABASE = []

# Временные данные в оперативке (теряются при перезагрузке)
temp_data = {}

# ============= ОТЛАДКА =============
def debug_log(message):
    """Логирование для отладки"""
    print(f"[DEBUG] {time.strftime('%H:%M:%S')} - {message}")

# ============= СТАРТ С ПОДРОБНОЙ ОТЛАДКОЙ =============
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()

    if len(args) > 1:
        key = args[1].upper()
        
        # ОТЛАДКА: выводим все данные
        debug_log("=" * 60)
        debug_log(f"🔑 ЗАПРОШЕН КЛЮЧ: {key}")
        debug_log(f"📊 ВСЕ КЛЮЧИ В БАЗЕ: {list(SCRIPTS_DATABASE.keys())}")
        debug_log(f"📱 User ID: {message.from_user.id}")
        debug_log(f"📝 Полный текст: {message.text}")
        
        if key in SCRIPTS_DATABASE:
            script = SCRIPTS_DATABASE[key]
            script['uses'] = script.get('uses', 0) + 1
            
            debug_log(f"✅ КЛЮЧ НАЙДЕН: {script['game_name']}")
            debug_log(f"📥 Использований: {script['uses']}")
            
            text = f"📌 {script['game_name']}\n\n"
            text += f"📥 Код для эксплоита:\n`{script['loadstring']}`\n\n"
            text += f"🔗 URL: {script['url']}\n"
            text += "📢 Больше скриптов: @SaulGoodmanScript\n"
            text += "🤝 Партнёр: @loriscript"

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
                InlineKeyboardButton("🤝 Партнёр", url="https://t.me/loriscript")
            )

            try:
                bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                debug_log(f"✅ Сообщение отправлено пользователю {message.from_user.id}")
            except Exception as e:
                debug_log(f"❌ Ошибка отправки: {e}")
                bot.send_message(message.chat.id, "❌ Ошибка отправки скрипта")
        else:
            debug_log(f"❌ КЛЮЧ НЕ НАЙДЕН В БАЗЕ!")
            
            # Подробное сообщение об ошибке для отладки
            error_msg = f"❌ Скрипт не найден!\n\n"
            error_msg += f"🔑 Запрошенный ключ: `{key}`\n"
            error_msg += f"📦 Доступные ключи:\n"
            for k in SCRIPTS_DATABASE.keys():
                error_msg += f"• `{k}` - {SCRIPTS_DATABASE[k]['game_name']}\n"
            
            # Только владельцу показываем полную отладку
            if message.from_user.id == OWNER_ID:
                error_msg += f"\n📊 Debug info:\n"
                error_msg += f"• Всего скриптов: {len(SCRIPTS_DATABASE)}\n"
                error_msg += f"• База: {SCRIPTS_DATABASE}"
            
            bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
        return

    # Обычный старт без ключа
    if message.from_user.id == OWNER_ID:
        bot.send_message(
            message.chat.id,
            f"👑 Создатель SaulGoodmanScript\n\n"
            f"📊 Статистика:\n"
            f"• Скриптов в базе: {len(SCRIPTS_DATABASE)}\n"
            f"• Всего скачиваний: {sum(s.get('uses', 0) for s in SCRIPTS_DATABASE.values())}\n\n"
            f"Отправь фото (если нужно) и текст в формате:\n\n"
            f"Название игры\n---\nURL\n---\nОписание через +"
        )
    else:
        bot.send_message(
            message.chat.id,
            "👋 Добро пожаловать!\n\n"
            f"📢 Канал: @SaulGoodmanScript\n"
            f"📦 Доступно скриптов: {len(SCRIPTS_DATABASE)}"
        )

# ============= КОМАНДА ДЛЯ ПРОВЕРКИ =============
@bot.message_handler(commands=['check'])
def check_key_command(message):
    if message.from_user.id != OWNER_ID:
        return
    
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
                f"Доступные ключи: {', '.join(SCRIPTS_DATABASE.keys())}",
                parse_mode="Markdown"
            )
    else:
        # Показать все ключи
        keys_list = "\n".join([f"• `{k}` - {SCRIPTS_DATABASE[k]['game_name']}" for k in SCRIPTS_DATABASE.keys()])
        bot.send_message(
            message.chat.id,
            f"🗝 Все ключи в базе ({len(SCRIPTS_DATABASE)}):\n\n{keys_list}",
            parse_mode="Markdown"
        )

# ============= КОМАНДА ДЛЯ ЭКСПОРТА =============
@bot.message_handler(commands=['export'])
def export_database_command(message):
    if message.from_user.id != OWNER_ID:
        return
    
    try:
        backup = json.dumps(SCRIPTS_DATABASE, ensure_ascii=False, indent=2)
        
        # Отправляем как файл
        bot.send_document(
            message.chat.id,
            ("scripts_database.py", f"SCRIPTS_DATABASE = {backup}".encode('utf-8')),
            caption="📦 Экспорт базы данных"
        )
        
        # Также показываем в сообщении
        preview = backup[:500] + "..." if len(backup) > 500 else backup
        bot.send_message(
            message.chat.id,
            f"📋 **Превью базы:**\n```python\n{preview}\n```",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка экспорта: {e}")

# ============= ДОБАВЛЕНИЕ НОВЫХ СКРИПТОВ =============
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

    user_id = str(message.from_user.id)

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

    # Генерируем ключ с проверкой уникальности
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

    # Показываем меню публикации
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
        f"📷 Фото: {'Да' if 'photo' in temp_data[user_id] else 'Нет'}\n\n"
        f"Выберите действие:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Генерация уникального ключа
def generate_unique_key(game_name):
    """Генерирует гарантированно уникальный ключ"""
    for attempt in range(10):
        # Добавляем случайные данные для уникальности
        unique_data = f"{game_name}{time.time()}{random.randint(1000, 999999)}"
        key = hashlib.md5(unique_data.encode()).hexdigest()[:8].upper()
        
        # Проверяем, нет ли такого ключа уже в базе
        if key not in SCRIPTS_DATABASE:
            debug_log(f"🔑 Сгенерирован уникальный ключ: {key}")
            return key
    
    # Если не удалось за 10 попыток, добавляем дополнительную случайность
    fallback_key = hashlib.md5(f"{game_name}{time.time()}{random.random()}".encode()).hexdigest()[:8].upper()
    debug_log(f"⚠️ Использован fallback ключ: {fallback_key}")
    return fallback_key

# Опубликовать пост
@bot.callback_query_handler(func=lambda call: call.data.startswith('publish_'))
def publish_script(call):
    user_id = call.data.replace('publish_', '')

    if user_id not in temp_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены")
        return

    data = temp_data[user_id]
    key = data['key']

    # Добавляем в базу
    SCRIPTS_DATABASE[key] = {
        'game_name': data['game_name'],
        'url': data['url'],
        'description': data['description'],
        'loadstring': data['loadstring'],
        'date': time.strftime("%d.%m.%Y %H:%M"),
        'uses': 0
    }

    # Публикуем в канал
    post_text = f"📌 {data['game_name']} SCRIPT!\n{data['description']}\n\n"
    post_text += f"⚡️Гайд как скачать\n@saulGoodmanScript_Guides\n\n"
    post_text += f"🤖Получить ключ от Delta\nhttps://t.me/Saul_KeyBypass\n\n"
    post_text += f"❓️Как использовать\n1. Копируете код выше\n2. Вставляете в ваш эксплоит\n3. Нажимаете Execute\n\n"
    post_text += f"-- Больше скриптов: @SaulGoodmanScript\n🤝 Партнёр: @loriscript"

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

        # Очищаем временные данные
        if user_id in temp_data:
            del temp_data[user_id]

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {str(e)}")

    bot.answer_callback_query(call.id)

# Просто сохранить в базу без публикации
@bot.callback_query_handler(func=lambda call: call.data.startswith('save_'))
def save_to_database(call):
    user_id = call.data.replace('save_', '')

    if user_id not in temp_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены")
        return

    data = temp_data[user_id]
    key = data['key']

    # Добавляем в базу
    SCRIPTS_DATABASE[key] = {
        'game_name': data['game_name'],
        'url': data['url'],
        'description': data['description'],
        'loadstring': data['loadstring'],
        'date': time.strftime("%d.%m.%Y %H:%M"),
        'uses': 0
    }

    bot_link = f"https://t.me/{BOT_USERNAME}?start={key}"
    
    bot.send_message(
        call.message.chat.id,
        f"💾 Сохранено в базу!\n"
        f"🔑 Ключ: `{key}`\n"
        f"🎮 Игра: {data['game_name']}\n"
        f"📊 Всего скриптов: {len(SCRIPTS_DATABASE)}\n\n"
        f"Тестовая ссылка: {bot_link}",
        parse_mode="Markdown"
    )

    # Очищаем временные данные
    if user_id in temp_data:
        del temp_data[user_id]

    bot.answer_callback_query(call.id)

# ============= ЗАПУСК =============
print("=" * 50)
print("🤖 Бот запущен!")
print(f"📦 Скриптов в базе: {len(SCRIPTS_DATABASE)}")
print(f"🔑 Ключи: {', '.join(SCRIPTS_DATABASE.keys())}")
print("=" * 50)

try:
    bot.polling(none_stop=True, skip_pending=True, timeout=30)
except Exception as e:
    print(f"❌ Ошибка: {e}") 