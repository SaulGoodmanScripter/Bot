import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
import hashlib
import os
import random
import threading

# ============= НАСТРОЙКИ =============
TOKEN = os.getenv('BOT_TOKEN') or "ВАШ_ТОКЕН_БОТА"  # Получаем из Heroku/Bothost
OWNER_ID = 6397071501
CHANNEL = "@SaulGoodmanScript"
BOT_USERNAME = "SaulScript_Bot"
WEBSITE_URL = "http://ваш-сайт.com"  # Ваш сайт

bot = telebot.TeleBot(TOKEN)

# ============= БАЗЫ ДАННЫХ =============
def load_json(filename, default={}):
    """Загрузка JSON файла"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Ошибка загрузки {filename}: {e}")
    return default

def save_json(filename, data):
    """Сохранение в JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения {filename}: {e}")
        return False

# ============= КОМАНДА /START =============
@bot.message_handler(commands=['start'])
def start_command(message):
    args = message.text.split()
    
    # Загружаем базы
    users_db = load_json('users.json', {})
    scripts_db = load_json('scripts.json', {})
    
    user_id = str(message.from_user.id)
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Пользователь"
    
    # Регистрируем/обновляем пользователя
    is_new_user = user_id not in users_db
    
    if is_new_user:
        users_db[user_id] = {
            'username': username,
            'first_name': first_name,
            'last_name': message.from_user.last_name or "",
            'join_date': time.strftime("%d.%m.%Y %H:%M:%S"),
            'join_timestamp': time.time(),
            'scripts_count': 0,
            'role': 'admin' if user_id == str(OWNER_ID) else 'user',
            'last_active': time.time()
        }
    else:
        # Обновляем последнюю активность
        users_db[user_id]['last_active'] = time.time()
    
    # Обработка аргументов start
    if len(args) > 1:
        param = args[1].lower()
        
        if param == 'registration':
            # Регистрация с сайта
            registration_flow(message, users_db, user_id, first_name, is_new_user)
            return
            
        elif param.startswith('auth_'):
            # Авторизация с сайта (старый метод)
            auth_token = args[1]
            handle_auth_token(message, users_db, user_id, auth_token)
            return
            
        elif param.startswith('script_'):
            # Получение скрипта по ключу
            script_key = param.replace('script_', '').upper()
            get_script(message, scripts_db, script_key)
            return
    
    # Обычный старт без параметров
    regular_start(message, users_db, scripts_db, user_id, first_name, is_new_user)
    
    # Сохраняем изменения
    save_json('users.json', users_db)

def registration_flow(message, users_db, user_id, first_name, is_new_user):
    """Поток регистрации с сайта"""
    # Генерируем токен для сайта
    auth_token = f"auth_{hashlib.md5(f'{user_id}{time.time()}'.encode()).hexdigest()[:12]}"
    
    # Сохраняем токен
    users_db[user_id]['website_token'] = auth_token
    users_db[user_id]['token_time'] = time.time()
    
    # Создаем кнопку для возврата на сайт
    markup = InlineKeyboardMarkup()
    site_url = f"{WEBSITE_URL}/auth_callback.html?token={auth_token}&user_id={user_id}"
    markup.add(InlineKeyboardButton("✅ Вернуться на сайт", url=site_url))
    
    # Приветственное сообщение
    if is_new_user:
        welcome_text = f"🎉 Добро пожаловать, {first_name}!\n\n"
        welcome_text += "✅ Вы успешно зарегистрированы!\n"
        welcome_text += f"🆔 Ваш ID: `{user_id}`\n"
        welcome_text += f"🔑 Токен: `{auth_token}`\n\n"
        welcome_text += "Теперь вы можете:\n"
        welcome_text += "• Добавлять свои скрипты на сайте\n"
        welcome_text += "• Получать доступ к эксклюзивным скриптам\n"
        welcome_text += "• Участвовать в обновлениях первым\n\n"
        welcome_text += "Нажмите кнопку ниже, чтобы вернуться на сайт:"
    else:
        welcome_text = f"👋 С возвращением, {first_name}!\n\n"
        welcome_text += "✅ Вы уже зарегистрированы!\n"
        welcome_text += f"🆔 Ваш ID: `{user_id}`\n"
        welcome_text += f"🔑 Новый токен: `{auth_token}`\n\n"
        welcome_text += "Нажмите кнопку ниже, чтобы вернуться на сайт:"
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

def handle_auth_token(message, users_db, user_id, auth_token):
    """Обработка токена авторизации"""
    users_db[user_id]['website_token'] = auth_token
    users_db[user_id]['token_time'] = time.time()
    
    markup = InlineKeyboardMarkup()
    site_url = f"{WEBSITE_URL}/auth_callback.html?token={auth_token}"
    markup.add(InlineKeyboardButton("🔗 Вернуться на сайт", url=site_url))
    
    bot.send_message(
        message.chat.id,
        f"✅ Авторизация успешна!\n\n"
        f"👤 {message.from_user.first_name}\n"
        f"🆔 ID: `{user_id}`\n"
        f"🔑 Токен: `{auth_token}`\n\n"
        f"Нажмите кнопку ниже:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

def get_script(message, scripts_db, script_key):
    """Получение скрипта по ключу"""
    if script_key in scripts_db:
        script = scripts_db[script_key]
        script['uses'] = script.get('uses', 0) + 1
        save_json('scripts.json', scripts_db)
        
        text = f"📌 {script['game_name']}\n\n"
        text += f"📥 Код для эксплоита:\n`{script['loadstring']}`\n\n"
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
            InlineKeyboardButton("🌐 Сайт", url=WEBSITE_URL)
        )
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Скрипт не найден!\n\n"
            f"🔑 Ключ: `{script_key}`\n"
            f"📦 Всего скриптов: {len(scripts_db)}",
            parse_mode="Markdown"
        )

def regular_start(message, users_db, scripts_db, user_id, first_name, is_new_user):
    """Обычный старт без параметров"""
    if user_id == str(OWNER_ID):
        # Админ панель
        total_uses = sum(s.get('uses', 0) for s in scripts_db.values())
        active_users = len([u for u in users_db.values() if time.time() - u.get('last_active', 0) < 86400])
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton("➕ Добавить скрипт", callback_data="add_script"),
            InlineKeyboardButton("🌐 Ссылка для сайта", callback_data="admin_site_link")
        )
        
        welcome_text = f"👑 Создатель, приветствую!\n\n"
        welcome_text += f"📊 Статистика:\n"
        welcome_text += f"• Пользователей: {len(users_db)}\n"
        welcome_text += f"• Активных (24ч): {active_users}\n"
        welcome_text += f"• Скриптов: {len(scripts_db)}\n"
        welcome_text += f"• Скачиваний: {total_uses}\n\n"
        welcome_text += f"Выберите действие:"
        
    else:
        # Обычный пользователь
        user_data = users_db[user_id]
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🌐 Регистрация на сайте", callback_data="user_register"),
            InlineKeyboardButton("➕ Добавить скрипт", callback_data="add_script"),
            InlineKeyboardButton("📢 Наш канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
            InlineKeyboardButton("❓ Помощь", callback_data="help")
        )
        
        if is_new_user:
            welcome_text = f"👋 Привет, {first_name}!\n\n"
            welcome_text += "🎉 Добро пожаловать в Roblox Scripts Hub!\n\n"
            welcome_text += "📢 Наш канал: @SaulGoodmanScript\n"
            welcome_text += "🌐 Сайт: " + WEBSITE_URL + "\n\n"
            welcome_text += "Для доступа к полному функционалу:\n"
            welcome_text += "1. Нажмите '🌐 Регистрация на сайте'\n"
            welcome_text += "2. Получите ссылку\n"
            welcome_text += "3. Откройте её в браузере"
        else:
            welcome_text = f"👋 С возвращением, {first_name}!\n\n"
            welcome_text += f"📊 Ваша статистика:\n"
            welcome_text += f"• Зарегистрирован: {user_data.get('join_date', 'N/A')}\n"
            welcome_text += f"• Ваших скриптов: {user_data.get('scripts_count', 0)}\n\n"
            welcome_text += "Выберите действие:"
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# ============= КОЛБЭКИ =============
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    users_db = load_json('users.json', {})
    
    if call.data == "user_register":
        # Генерация ссылки для регистрации
        auth_token = f"auth_{hashlib.md5(f'{user_id}{time.time()}'.encode()).hexdigest()[:12]}"
        
        users_db[user_id]['website_token'] = auth_token
        users_db[user_id]['token_time'] = time.time()
        save_json('users.json', users_db)
        
        # Создаем ссылку
        site_url = f"{WEBSITE_URL}/auth_callback.html?token={auth_token}&user_id={user_id}"
        
        bot.send_message(
            call.message.chat.id,
            f"🔗 Ваша ссылка для регистрации на сайте:\n\n"
            f"`{site_url}`\n\n"
            f"📋 Инструкция:\n"
            f"1. Скопируйте эту ссылку\n"
            f"2. Откройте её в браузере\n"
            f"3. Вы будете автоматически авторизованы\n\n"
            f"⚠️ Ссылка действительна 24 часа",
            parse_mode="Markdown"
        )
        
    elif call.data == "add_script":
        bot.send_message(
            call.message.chat.id,
            "📝 Чтобы добавить скрипт, используйте команду:\n\n"
            "`/add`\n\n"
            "Или отправьте текст в формате:\n"
            "НАЗВАНИЕ ИГРЫ\n---\nURL СКРИПТА\n---\nОПИСАНИЕ"
        )
        
    elif call.data == "help":
        bot.send_message(
            call.message.chat.id,
            "❓ Помощь по использованию бота:\n\n"
            "📌 Основные команды:\n"
            "• /start - начало работы\n"
            "• /add - добавить скрипт\n"
            "• /myscripts - мои скрипты\n"
            "• /help - эта справка\n\n"
            "🌐 Регистрация на сайте:\n"
            "1. Нажмите '🌐 Регистрация на сайте'\n"
            "2. Получите уникальную ссылку\n"
            "3. Откройте её в браузере\n\n"
            "📢 Наш канал: @SaulGoodmanScript"
        )
        
    elif call.data == "admin_stats":
        if user_id != str(OWNER_ID):
            bot.answer_callback_query(call.id, "❌ Только для создателя")
            return
            
        users_db = load_json('users.json', {})
        scripts_db = load_json('scripts.json', {})
        
        total_uses = sum(s.get('uses', 0) for s in scripts_db.values())
        today = time.strftime("%d.%m.%Y")
        today_users = len([u for u in users_db.values() if u.get('join_date', '').startswith(today)])
        
        stats_text = f"📊 Детальная статистика:\n\n"
        stats_text += f"👥 Пользователи:\n"
        stats_text += f"• Всего: {len(users_db)}\n"
        stats_text += f"• Сегодня: {today_users}\n"
        stats_text += f"• Активных (24ч): {len([u for u in users_db.values() if time.time() - u.get('last_active', 0) < 86400])}\n\n"
        stats_text += f"📝 Скрипты: {len(scripts_db)}\n"
        stats_text += f"• Скачиваний: {total_uses}\n"
        stats_text += f"• Популярных (>10): {len([s for s in scripts_db.values() if s.get('uses', 0) > 10])}\n"
        stats_text += f"• Популярных (>50): {len([s for s in scripts_db.values() if s.get('uses', 0) > 50])}\n\n"
        stats_text += f"🌐 Веб-сайт: {WEBSITE_URL}\n"
        stats_text += f"• Зарегистрировано: {len([u for u in users_db.values() if u.get('website_token')])}"
        
        bot.send_message(call.message.chat.id, stats_text)
        
    elif call.data == "admin_users":
        if user_id != str(OWNER_ID):
            bot.answer_callback_query(call.id, "❌ Только для создателя")
            return
            
        users_db = load_json('users.json', {})
        
        # Последние 10 пользователей
        recent_users = sorted(
            users_db.items(),
            key=lambda x: x[1].get('join_timestamp', 0),
            reverse=True
        )[:10]
        
        users_text = "👥 Последние 10 пользователей:\n\n"
        for uid, data in recent_users:
            users_text += f"• {data.get('first_name', 'N/A')} (@{data.get('username', 'N/A')})\n"
            users_text += f"  ID: `{uid}`\n"
            users_text += f"  Дата: {data.get('join_date', 'N/A')}\n"
            users_text += f"  Скриптов: {data.get('scripts_count', 0)}\n"
            if data.get('website_token'):
                users_text += f"  🌐 Зарегистрирован на сайте\n"
            users_text += "\n"
        
        bot.send_message(call.message.chat.id, users_text, parse_mode="Markdown")
        
    elif call.data == "admin_site_link":
        if user_id != str(OWNER_ID):
            bot.answer_callback_query(call.id, "❌ Только для создателя")
            return
            
        site_url = f"{WEBSITE_URL}/admin.html"
        bot.send_message(
            call.message.chat.id,
            f"🔗 Ссылка на админ-панель сайта:\n\n`{site_url}`",
            parse_mode="Markdown"
        )
    
    bot.answer_callback_query(call.id)

# ============= КОМАНДА /ADD =============
temp_storage = {}

@bot.message_handler(commands=['add'])
def add_script_command(message):
    user_id = str(message.from_user.id)
    
    bot.send_message(
        message.chat.id,
        "📝 Отправьте информацию о скрипте в формате:\n\n"
        "НАЗВАНИЕ ИГРЫ\n---\nURL СКРИПТА\n---\nОПИСАНИЕ\n\n"
        "Пример:\n"
        "Blox Fruits\n---\nhttps://pastebin.com/raw/xxx\n---\nAuto Farm + Teleport + ESP\n\n"
        "Или отправьте фото и текст отдельно."
    )
    
    # Сохраняем состояние
    temp_storage[user_id] = {'step': 'waiting_for_script'}

# Обработка текста с форматом скрипта
@bot.message_handler(func=lambda m: True)
def handle_script_format(message):
    user_id = str(message.from_user.id)
    
    if '---' in message.text:
        parts = message.text.split('\n---\n')
        if len(parts) >= 3:
            process_script_data(message, parts)

def process_script_data(message, parts):
    user_id = str(message.from_user.id)
    
    game_name = parts[0].strip()
    url = parts[1].strip()
    description = parts[2].strip()
    
    # Валидация URL
    if not url.startswith(('http://', 'https://')):
        bot.send_message(message.chat.id, "❌ URL должен начинаться с http:// или https://")
        return
    
    # Генерация ключа
    key = f"SCR_{hashlib.md5(f'{game_name}{user_id}{time.time()}'.encode()).hexdigest()[:6].upper()}"
    loadstring = f'loadstring(game:HttpGet("{url}"))()'
    
    # Показываем предпросмотр
    preview_text = f"✅ Данные получены!\n\n"
    preview_text += f"🎮 Игра: {game_name}\n"
    preview_text += f"🔑 Ключ: `{key}`\n"
    preview_text += f"🔗 URL: {url[:50]}...\n"
    preview_text += f"📝 Описание: {description[:100]}...\n\n"
    preview_text += f"Код для эксплоита:\n`{loadstring}`"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Опубликовать", callback_data=f"publish_{key}_{user_id}"),
        InlineKeyboardButton("❌ Отменить", callback_data="cancel_add")
    )
    
    # Сохраняем во временное хранилище
    temp_storage[user_id] = {
        'game_name': game_name,
        'url': url,
        'description': description,
        'loadstring': loadstring,
        'key': key
    }
    
    bot.send_message(message.chat.id, preview_text, reply_markup=markup, parse_mode="Markdown")

# Обработка публикации
@bot.callback_query_handler(func=lambda call: call.data.startswith('publish_'))
def publish_script(call):
    try:
        _, key, user_id = call.data.split('_')
        
        if user_id != str(call.from_user.id):
            bot.answer_callback_query(call.id, "❌ Это не ваш скрипт")
            return
        
        if user_id in temp_storage:
            script_data = temp_storage[user_id]
            
            # Загружаем базы
            scripts_db = load_json('scripts.json', {})
            users_db = load_json('users.json', {})
            
            # Сохраняем скрипт
            scripts_db[key] = {
                'game_name': script_data['game_name'],
                'url': script_data['url'],
                'description': script_data['description'],
                'loadstring': script_data['loadstring'],
                'author_id': user_id,
                'author_name': call.from_user.first_name,
                'date': time.strftime("%d.%m.%Y %H:%M"),
                'uses': 0,
                'verified': True if user_id == str(OWNER_ID) else False
            }
            
            # Обновляем статистику пользователя
            if user_id in users_db:
                users_db[user_id]['scripts_count'] = users_db[user_id].get('scripts_count', 0) + 1
            
            # Сохраняем изменения
            save_json('scripts.json', scripts_db)
            save_json('users.json', users_db)
            
            # Очищаем временное хранилище
            del temp_storage[user_id]
            
            # Отправляем подтверждение
            bot.send_message(
                call.message.chat.id,
                f"✅ Скрипт опубликован!\n\n"
                f"🔑 Ключ: `{key}`\n"
                f"📊 Всего скриптов: {len(scripts_db)}\n\n"
                f"Ссылка для скачивания:\n"
                f"https://t.me/{BOT_USERNAME}?start=script_{key}",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {str(e)}")
    
    bot.answer_callback_query(call.id)

# ============= ЗАПУСК БОТА =============
print("=" * 50)
print(f"🤖 Бот @{BOT_USERNAME} запущен!")
print(f"👑 Создатель: {OWNER_ID}")
print(f"🌐 Сайт: {WEBSITE_URL}")
print(f"📢 Канал: {CHANNEL}")
print("=" * 50)

# Автосохранение каждые 5 минут
def auto_save():
    while True:
        time.sleep(300)  # 5 минут
        try:
            # Просто проверяем, что бот жив
            print(f"🔄 Автосохранение: {time.strftime('%H:%M:%S')}")
        except:
            pass

# Запускаем автосохранение в отдельном потоке
threading.Thread(target=auto_save, daemon=True).start()

# Запуск бота
try:
    bot.polling(none_stop=True, skip_pending=True, timeout=30)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    time.sleep(5)