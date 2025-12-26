import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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
    print("❌ ОШИБКА: Не найден BOT_TOKEN в переменных окружения Bothost!")
    print("✅ Убедитесь, что в настройках бота есть переменная BOT_TOKEN")
    exit(1)

print(f"✅ Токен загружен с Bothost! Начинается на: {TOKEN[:15]}...")

OWNER_ID = 6397071501
CHANNEL = "@SaulGoodmanScript"
BOT_USERNAME = "SaulScript_Bot"

bot = telebot.TeleBot(TOKEN)

# ============= ДИНАМИЧЕСКАЯ ЗАГРУЗКА JSON =============

def load_scripts_dynamic():
    """ВСЕГДА загружает свежую версию из файла"""
    try:
        if os.path.exists('scripts.json'):
            with open('scripts.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            return {}
    except Exception as e:
        print(f"❌ Ошибка загрузки JSON: {e}")
        return {}

def save_scripts_dynamic(data):
    """Сохраняет скрипты и возвращает обновленные данные"""
    try:
        with open('scripts.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

# ============= ИСПРАВЛЕННЫЙ СТАРТ =============

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
                InlineKeyboardButton("🤝 Партнёр", url="https://t.me/loriscript")
            )

            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(
                message.chat.id,
                f"❌ Скрипт не найден!\n\n"
                f"🔑 Ключ: `{key}`\n"
                f"📦 Всего скриптов: {len(SCRIPTS_DATABASE)}\n"
                f"📋 Ключи: {', '.join(SCRIPTS_DATABASE.keys()[:5])}...",
                parse_mode="Markdown"
            )
        return

    # Обычный старт без ключа
    SCRIPTS_DATABASE = load_scripts_dynamic()
    
    if message.from_user.id == OWNER_ID:
        total_uses = sum(s.get('uses', 0) for s in SCRIPTS_DATABASE.values())
        bot.send_message(
            message.chat.id,
            f"👑 Создатель SaulGoodmanScript\n\n"
            f"📊 Статистика:\n"
            f"• Скриптов в базе: {len(SCRIPTS_DATABASE)}\n"
            f"• Всего скачиваний: {total_uses}\n\n"
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

# ============= ИСПРАВЛЕННАЯ КОМАНДА CHECK =============

@bot.message_handler(commands=['check'])
def check_key_command(message):
    if message.from_user.id != OWNER_ID:
        return

    # ВСЕГДА загружаем свежие данные
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
                f"Доступные ключи: {', '.join(SCRIPTS_DATABASE.keys()[:10])}...",
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

# ============= ДОБАВЛЕНИЕ СКРИПТОВ (исправлено) =============

temp_data = {}

def generate_unique_key(game_name):
    """Генерирует уникальный ключ"""
    # Загружаем текущую базу
    SCRIPTS_DATABASE = load_scripts_dynamic()
    
    for attempt in range(10):
        unique_data = f"{game_name}{time.time()}{random.randint(1000, 999999)}"
        key = hashlib.md5(unique_data.encode()).hexdigest()[:8].upper()

        if key not in SCRIPTS_DATABASE:
            return key
    
    # Fallback
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

    # Загружаем актуальную базу
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

    # Генерируем ключ с проверкой в ТЕКУЩЕЙ базе
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

    # Загружаем текущую базу
    SCRIPTS_DATABASE = load_scripts_dynamic()
    
    # Добавляем в базу
    SCRIPTS_DATABASE[key] = {
        'game_name': data['game_name'],
        'url': data['url'],
        'description': data['description'],
        'loadstring': data['loadstring'],
        'date': time.strftime("%d.%m.%Y %H:%M"),
        'uses': 0
    }

    # Сохраняем в JSON
    save_scripts_dynamic(SCRIPTS_DATABASE)

    # Публикуем в канал
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

        # Очищаем временные данные
        if user_id in temp_data:
            del temp_data[user_id]

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {str(e)}")

    bot.answer_callback_query(call.id)

# ============= ЗАПУСК БОТА =============

print("=" * 50)
print("🤖 Бот запущен на Bothost!")
print("=" * 50)

try:
    bot.polling(none_stop=True, skip_pending=True, timeout=30)
except Exception as e:
    print(f"❌ Ошибка: {e}")