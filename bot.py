import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
import hashlib
import os
import re

# ============= НАСТРОЙКИ =============
TOKEN = "8327750780:AAHo6Rn0wiAmN_sZNC1B13785Kg-LuSi-Oc"
OWNER_ID = 6397071501
CHANNEL = "@SaulGoodmanScript"
BOT_USERNAME = "SaulScript_Bot"

bot = telebot.TeleBot(TOKEN)

# ============= ХРАНЕНИЕ В ПЕРЕМЕННЫХ ПИТОНА =============
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

# ============= ФУНКЦИИ ДЛЯ РАБОТЫ С БАЗОЙ =============
def save_backup():
    """Создает резервную копию базы (для восстановления)"""
    try:
        backup = json.dumps(SCRIPTS_DATABASE, ensure_ascii=False, indent=2)
        
        # Можно сохранить в файл, если нужно
        # with open("backup.txt", "w", encoding="utf-8") as f:
        #     f.write(backup)
        
        return backup
    except Exception as e:
        print(f"❌ Ошибка создания бэкапа: {e}")
        return None

def add_script_to_code(key, data):
    """Добавляет скрипт в базу (в памяти)"""
    SCRIPTS_DATABASE[key] = data
    print(f"✅ Скрипт {key} добавлен в базу")
    
    # Авто-сохранение в файл (опционально)
    try:
        with open("scripts_backup.py", "w", encoding="utf-8") as f:
            f.write("SCRIPTS_DATABASE = " + json.dumps(SCRIPTS_DATABASE, ensure_ascii=False, indent=2))
    except:
        pass

# ============= КОМАНДА ДЛЯ ЭКСПОРТА/ИМПОРТА =============
@bot.message_handler(commands=['database'])
def database_management(message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Только для создателя")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📦 Экспорт базы", callback_data="export_db"),
        InlineKeyboardButton("📥 Импорт базы", callback_data="import_db"),
        InlineKeyboardButton("📋 Показать все", callback_data="show_all_keys"),
        InlineKeyboardButton("🔄 Обновить код", callback_data="update_code")
    )
    
    bot.send_message(
        message.chat.id,
        f"🗄 **Управление базой данных**\n\n"
        f"📊 Всего скриптов: {len(SCRIPTS_DATABASE)}\n"
        f"🔄 Для обновления кода скопируйте данные ниже\n"
        f"📝 и отправьте разработчику/вставьте в код",
        reply_markup=markup
    )

# Экспорт базы
@bot.callback_query_handler(func=lambda call: call.data == "export_db")
def export_database(call):
    backup = save_backup()
    
    if backup:
        # Отправляем как файл
        bot.send_document(
            call.message.chat.id,
            ("scripts_database.py", f"SCRIPTS_DATABASE = {backup}".encode('utf-8')),
            caption="📦 Экспорт базы данных\nПросто скопируйте этот код и замените в файле"
        )
        
        # Также показываем первые 1000 символов для быстрого просмотра
        preview = backup[:500] + "..." if len(backup) > 500 else backup
        bot.send_message(
            call.message.chat.id,
            f"📋 **Превью базы:**\n```python\n{preview}\n```",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(call.message.chat.id, "❌ Ошибка экспорта")
    
    bot.answer_callback_query(call.id)

# Показать все ключи
@bot.callback_query_handler(func=lambda call: call.data == "show_all_keys")
def show_all_keys(call):
    if not SCRIPTS_DATABASE:
        bot.send_message(call.message.chat.id, "📭 База пуста")
        bot.answer_callback_query(call.id)
        return
    
    keys_list = "\n".join([f"• `{key}` - {data['game_name']}" for key, data in SCRIPTS_DATABASE.items()])
    
    bot.send_message(
        call.message.chat.id,
        f"🗝 **Все ключи в базе:**\n\n{keys_list}\n\n"
        f"Всего: {len(SCRIPTS_DATABASE)} скриптов",
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# Обновить код
@bot.callback_query_handler(func=lambda call: call.data == "update_code")
def update_code_info(call):
    bot.send_message(
        call.message.chat.id,
        "🔄 **Как обновить код базы:**\n\n"
        "1. Используйте команду `/database` → 📦 Экспорт базы\n"
        "2. Получите файл `scripts_database.py`\n"
        "3. Откройте основной файл бота\n"
        "4. Найдите блок `SCRIPTS_DATABASE = {`\n"
        "5. Замените ВСЕ данные на новые из экспорта\n"
        "6. Перезапустите бота\n\n"
        "📝 **Важно:** Не меняйте названия переменных!",
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# ============= СТАРТ (с обновленной базой) =============
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()

    if len(args) > 1:
        key = args[1].upper()
        if key in SCRIPTS_DATABASE:
            script = SCRIPTS_DATABASE[key]
            # Увеличиваем счетчик использований
            script['uses'] = script.get('uses', 0) + 1
            
            text = f"📌 {script['game_name']}\n\n"
            text += f"📝 Описание:\n{script['description']}\n\n"
            text += f"📥 Код для эксплоита:\n`{script['loadstring']}`\n\n"
            text += f"🔗 URL: {script['url']}\n"
            text += f"📅 Добавлен: {script['date']}\n"
            text += f"👥 Скачали: {script['uses']} раз\n\n"
            text += "📢 Больше скриптов: @SaulGoodmanScript\n"
            text += "🤝 Партнёр: @loriscript"

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
                InlineKeyboardButton("🤝 Партнёр", url="https://t.me/loriscript")
            )

            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Скрипт не найден в базе")
        return

    if message.from_user.id == OWNER_ID:
        # Показываем статистику для создателя
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

    # Генерируем ключ
    key = hashlib.md5(f"{game_name}{time.time()}".encode()).hexdigest()[:8].upper()
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
            f"📊 Всего скриптов: {len(SCRIPTS_DATABASE)}",
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
    
    bot.send_message(
        call.message.chat.id,
        f"💾 Сохранено в базу!\n"
        f"🔑 Ключ: `{key}`\n"
        f"🎮 Игра: {data['game_name']}\n"
        f"📊 Всего скриптов: {len(SCRIPTS_DATABASE)}\n\n"
        f"Теперь вы можете:\n"
        f"1. Добавить этот ключ в код бота\n"
        f"2. Использовать команду `/database` для экспорта\n"
        f"3. Отправить разработчику для обновления кода",
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
print("=" * 50)

try:
    bot.polling(none_stop=True, skip_pending=True)
except Exception as e:
    print(f"❌ Ошибка: {e}")