import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import json
import time
import hashlib
import os
import random
from datetime import datetime

# ============= НАСТРОЙКИ =============
TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = 6397071501
CHANNEL = "@SaulGoodmanScript"
BOT_USERNAME = "SaulScript_Bot"
WEBSITE_URL = "https://ваш-сайт.com"  # Замените на ваш домен

bot = telebot.TeleBot(TOKEN)

# ============= УЛУЧШЕННАЯ БАЗА ДАННЫХ =============
USERS_FILE = 'users.json'
SCRIPTS_FILE = 'scripts.json'

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_scripts():
    try:
        if os.path.exists(SCRIPTS_FILE):
            with open(SCRIPTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_scripts(scripts):
    try:
        with open(SCRIPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(scripts, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ============= РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ =============

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    
    # Регистрация/авторизация пользователя
    users = load_users()
    user_id = str(message.from_user.id)
    
    if user_id not in users:
        users[user_id] = {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'registration_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'scripts_count': 0,
            'is_verified': False,
            'role': 'user' if user_id != str(OWNER_ID) else 'admin'
        }
        save_users(users)
    
    if len(args) > 1:
        # Обработка ссылок на скрипты (старая функциональность)
        key = args[1].upper()
        
        if key.startswith('AUTH_'):
            # Авторизация с сайта
            auth_token = key.replace('AUTH_', '')
            users[user_id]['web_auth_token'] = auth_token
            users[user_id]['last_auth'] = time.strftime("%Y-%m-%d %H:%M:%S")
            save_users(users)
            
            # Отправляем данные для сайта
            user_data = {
                'id': message.from_user.id,
                'username': message.from_user.username,
                'firstName': message.from_user.first_name,
                'lastName': message.from_user.last_name,
                'authMethod': 'telegram',
                'authToken': auth_token
            }
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                "✅ Перейти на сайт",
                web_app=WebAppInfo(url=f"{WEBSITE_URL}/auth_callback?data={json.dumps(user_data)}")
            ))
            
            bot.send_message(
                message.chat.id,
                f"✅ Авторизация успешна!\n\n"
                f"👤 {message.from_user.first_name}\n"
                f"📅 Зарегистрирован: {users[user_id]['registration_date']}\n"
                f"📊 Скриптов добавлено: {users[user_id]['scripts_count']}\n\n"
                f"Нажмите кнопку ниже чтобы продолжить на сайте:",
                reply_markup=markup
            )
            return
            
        elif key.startswith('SCRIPT_'):
            # Прямой доступ к скрипту
            script_key = key.replace('SCRIPT_', '')
            scripts = load_scripts()
            
            if script_key in scripts:
                script = scripts[script_key]
                script['uses'] = script.get('uses', 0) + 1
                save_scripts(scripts)
                
                text = f"📌 {script['game_name']}\n\n"
                text += f"📥 Код для эксплоита:\n`{script['loadstring']}`\n\n"
                
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
                    InlineKeyboardButton("🌐 Открыть на сайте", web_app=WebAppInfo(url=WEBSITE_URL))
                )
                
                bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ Скрипт не найден!")
            return
    
    # Стандартное приветствие
    users = load_users()
    user_data = users.get(str(message.from_user.id), {})
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    if message.from_user.id == OWNER_ID:
        total_uses = sum(s.get('uses', 0) for s in load_scripts().values())
        scripts_count = len(load_scripts())
        
        markup.add(
            InlineKeyboardButton("🌐 Открыть сайт", web_app=WebAppInfo(url=WEBSITE_URL)),
            InlineKeyboardButton("📊 Статистика", callback_data="stats"),
            InlineKeyboardButton("➕ Добавить скрипт", callback_data="add_script")
        )
        
        bot.send_message(
            message.chat.id,
            f"👑 Создатель SaulGoodmanScript\n\n"
            f"📊 Статистика:\n"
            f"• Пользователей: {len(users)}\n"
            f"• Скриптов в базе: {scripts_count}\n"
            f"• Всего скачиваний: {total_uses}\n\n"
            f"Выберите действие:",
            reply_markup=markup
        )
    else:
        markup.add(
            InlineKeyboardButton("🌐 Открыть сайт", web_app=WebAppInfo(url=WEBSITE_URL)),
            InlineKeyboardButton("➕ Добавить скрипт", callback_data="add_script"),
            InlineKeyboardButton("📢 Наш канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
            InlineKeyboardButton("📋 Мои скрипты", callback_data="my_scripts")
        )
        
        bot.send_message(
            message.chat.id,
            f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            f"📢 Канал: @SaulGoodmanScript\n"
            f"📊 Ваша статистика:\n"
            f"• Зарегистрирован: {user_data.get('registration_date', 'сегодня')}\n"
            f"• Ваших скриптов: {user_data.get('scripts_count', 0)}\n\n"
            f"Выберите действие:",
            reply_markup=markup
        )

# ============= ДОБАВЛЕНИЕ СКРИПТОВ =============

temp_data = {}

def generate_script_key(game_name, user_id):
    unique_data = f"{game_name}{user_id}{time.time()}{random.randint(1000, 999999)}"
    return hashlib.md5(unique_data.encode()).hexdigest()[:8].upper()

@bot.callback_query_handler(func=lambda call: call.data == "add_script")
def add_script_callback(call):
    users = load_users()
    user_id = str(call.from_user.id)
    
    if user_id not in users:
        bot.answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь через /start")
        return
    
    bot.send_message(
        call.message.chat.id,
        "📝 Для добавления скрипта отправьте текст в формате:\n\n"
        "Название игры\n---\nURL скрипта\n---\nОписание через +\n\n"
        "Или отправьте фото и текст отдельно."
    )
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = str(message.from_user.id)
    
    if user_id not in temp_data:
        temp_data[user_id] = {}
    
    temp_data[user_id]['photo'] = message.photo[-1].file_id
    bot.reply_to(message, "✅ Фото сохранено! Теперь отправьте текст с информацией о скрипте.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = str(message.from_user.id)
    
    if message.text.startswith('/'):
        return
    
    parts = message.text.split('\n---\n')
    
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Неправильный формат! Используйте:\n\nНазвание игры\n---\nURL\n---\nОписание")
        return
    
    game_name = parts[0].strip()
    url = parts[1].strip()
    description = parts[2].strip()
    
    if not url.startswith(('http://', 'https://')):
        bot.send_message(message.chat.id, "❌ Неверный URL")
        return
    
    # Загружаем текущие данные
    users = load_users()
    scripts = load_scripts()
    
    # Генерируем ключ
    key = generate_script_key(game_name, user_id)
    loadstring = f'loadstring(game:HttpGet("{url}"))()'
    
    # Сохраняем во временные данные
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
    
    # Увеличиваем счетчик скриптов пользователя
    if user_id in users:
        users[user_id]['scripts_count'] = users[user_id].get('scripts_count', 0) + 1
        save_users(users)
    
    # Создаем клавиатуру с действиями
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👁️ Предпросмотр", callback_data=f"preview_{user_id}"),
        InlineKeyboardButton("🚀 Опубликовать в канал", callback_data=f"publish_{user_id}"),
        InlineKeyboardButton("💾 Сохранить в базу", callback_data=f"save_{user_id}"),
        InlineKeyboardButton("🌐 Добавить на сайт", callback_data=f"web_{user_id}")
    )
    
    bot.send_message(
        message.chat.id,
        f"✅ Данные получены!\n\n"
        f"🎮 Игра: {game_name}\n"
        f"🔑 Ключ: `{key}`\n"
        f"📷 Фото: {'Да' if 'photo' in temp_data[user_id] else 'Нет'}\n"
        f"👤 Ваш ID: {user_id}\n\n"
        f"Выберите действие:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('publish_'))
def publish_script(call):
    user_id = call.data.replace('publish_', '')
    
    if user_id not in temp_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены")
        return
    
    data = temp_data[user_id]
    key = data['key']
    
    # Сохраняем в базу
    scripts = load_scripts()
    scripts[key] = {
        'game_name': data['game_name'],
        'url': data['url'],
        'description': data['description'],
        'loadstring': data['loadstring'],
        'date': time.strftime("%d.%m.%Y %H:%M"),
        'author_id': user_id,
        'author_name': call.from_user.first_name,
        'uses': 0,
        'verified': True
    }
    save_scripts(scripts)
    
    # Публикуем в канал
    post_text = f"📌 {data['game_name']} SCRIPT!\n{data['description']}\n\n"
    post_text += f"⚡️Гайд как скачать\n@saulGoodmanScript_Guides\n\n"
    post_text += f"🤖Получить ключ от Delta\nhttps://keybypass.net/ \n\n"
    post_text += f"❓️Как использовать\n1. Копируете код выше\n2. Вставляете в ваш эксплоит\n3. Нажимаете Execute\n\n"
    post_text += f" Больше скриптов: @SaulGoodmanScript\n🤝 Партнёр: @loriscript"

    bot_link = f"https://t.me/{BOT_USERNAME}?start=SCRIPT_{key}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📥 Получить скрипт", url=bot_link))
    
    try:
        if data.get('has_photo') and 'photo' in data:
            bot.send_photo(CHANNEL, photo=data['photo'], caption=post_text, reply_markup=markup)
        else:
            bot.send_message(CHANNEL, post_text, reply_markup=markup, disable_web_page_preview=True)
        
        # Отправляем пользователю
        bot.send_message(
            call.message.chat.id,
            f"✅ Скрипт опубликован!\n\n"
            f"🔑 Ключ: `{key}`\n"
            f"📊 Всего скриптов в базе: {len(scripts)}\n\n"
            f"Ссылка для скачивания:\n{bot_link}",
            parse_mode="Markdown"
        )
        
        # Очищаем временные данные
        if user_id in temp_data:
            del temp_data[user_id]
            
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {str(e)}")
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('web_'))
def add_to_website(call):
    user_id = call.data.replace('web_', '')
    
    if user_id not in temp_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены")
        return
    
    data = temp_data[user_id]
    
    # Создаем данные для сайта
    script_data = {
        'id': f"TG_{data['key']}_{int(time.time())}",
        'game': data['game_name'],
        'name': data['game_name'] + " Script",
        'code': f"-- Скрипт из Telegram бота\n-- Игра: {data['game_name']}\n-- Автор: {call.from_user.first_name}\n\n{data['loadstring']}",
        'author': call.from_user.first_name,
        'author_id': user_id,
        'date': datetime.now().isoformat(),
        'verified': True,
        'source': 'telegram_bot',
        'telegram_key': data['key']
    }
    
    # Отправляем данные на сайт (в реальности через API)
    # Пока просто показываем информацию
    bot.send_message(
        call.message.chat.id,
        f"🌐 Данные для сайта:\n\n"
        f"Игра: {script_data['game']}\n"
        f"ID: {script_data['id']}\n"
        f"Автор: {script_data['author']}\n"
        f"Дата: {script_data['date'][:10]}\n\n"
        f"Скрипт будет добавлен на сайт автоматически.",
        parse_mode="Markdown"
    )
    
    bot.answer_callback_query(call.id, "✅ Данные подготовлены для сайта")

# ============= АДМИН КОМАНДЫ =============

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != OWNER_ID:
        return
    
    users = load_users()
    scripts = load_scripts()
    
    total_uses = sum(s.get('uses', 0) for s in scripts.values())
    active_users = len([u for u in users.values() if u.get('scripts_count', 0) > 0])
    
    stats_text = f"📊 Статистика бота:\n\n"
    stats_text += f"👥 Пользователи:\n"
    stats_text += f"• Всего: {len(users)}\n"
    stats_text += f"• Активных: {active_users}\n"
    stats_text += f"• Новых за 24ч: {len([u for u in users.values() if 'registration_date' in u and '2024' in u['registration_date']])}\n\n"
    stats_text += f"📝 Скрипты:\n"
    stats_text += f"• Всего: {len(scripts)}\n"
    stats_text += f"• Скачиваний: {total_uses}\n"
    stats_text += f"• Популярных (>10 скач.): {len([s for s in scripts.values() if s.get('uses', 0) > 10])}\n\n"
    stats_text += f"🌐 Веб-интеграция:\n"
    stats_text += f"• Сайт: {WEBSITE_URL}\n"
    stats_text += f"• Авторизовано: {len([u for u in users.values() if u.get('web_auth_token')])}"
    
    bot.send_message(message.chat.id, stats_text)

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.from_user.id != OWNER_ID:
        return
    
    users = load_users()
    
    text = "👥 Список пользователей:\n\n"
    for user_id, user_data in list(users.items())[:20]:  # Первые 20
        text += f"ID: {user_id}\n"
        text += f"Имя: {user_data.get('first_name', 'N/A')}\n"
        text += f"Скриптов: {user_data.get('scripts_count', 0)}\n"
        text += f"Дата регистрации: {user_data.get('registration_date', 'N/A')}\n"
        if user_data.get('web_auth_token'):
            text += f"🌐 Веб-токен: {user_data['web_auth_token'][:8]}...\n"
        text += "─" * 20 + "\n"
    
    bot.send_message(message.chat.id, text)

# ============= API ДЛЯ САЙТА =============

@bot.message_handler(commands=['api'])
def api_info(message):
    user_id = str(message.from_user.id)
    users = load_users()
    
    if user_id not in users:
        bot.send_message(message.chat.id, "❌ Сначала зарегистрируйтесь через /start")
        return
    
    # Генерируем API токен
    api_token = hashlib.md5(f"{user_id}{time.time()}{random.randint(1000, 999999)}".encode()).hexdigest()
    users[user_id]['api_token'] = api_token
    save_users(users)
    
    bot.send_message(
        message.chat.id,
        f"🔐 Ваш API токен:\n`{api_token}`\n\n"
        f"Используйте его для интеграции с сайтом.\n"
        f"Действителен 30 дней.",
        parse_mode="Markdown"
    )

# ============= ЗАПУСК БОТА =============

print("=" * 50)
print(f"🤖 Бот запущен: @{BOT_USERNAME}")
print(f"🌐 Сайт: {WEBSITE_URL}")
print("=" * 50)

if __name__ == "__main__":
    bot.polling(none_stop=True, skip_pending=True, timeout=30)