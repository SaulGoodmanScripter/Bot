import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
import hashlib
import os
import re
import random
from math import ceil

# ============= НАСТРОЙКИ =============
TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = 6397071501
CHANNEL = "@SaulGoodmanScript"
CHANNEL_ID = -1002969447954  
BOT_USERNAME = "SaulScript_Bot"

bot = telebot.TeleBot(TOKEN)

# ============= ПРОВЕРКА ПОДПИСКИ =============

def check_subscription(user_id):
    """Проверяет, подписан ли пользователь на канал"""
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

def show_subscription_message(chat_id, first_name):
    """Показывает сообщение с требованием подписки"""
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
        InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")
    )
    
    bot.send_message(
        chat_id,
        f"👋 Привет, {first_name}!\n\n"
        f"📢 Чтобы пользоваться ботом, нужно подписаться на наш канал:\n"
        f"{CHANNEL}\n\n"
        f"👉 После подписки нажмите кнопку '✅ Я подписался'",
        reply_markup=markup
    )

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

# ============= КАТАЛОГ СКРИПТОВ =============

def get_unique_games():
    """Получает список уникальных игр из базы"""
    SCRIPTS_DATABASE = load_scripts_dynamic()
    games = {}
    
    for key, script in SCRIPTS_DATABASE.items():
        game_name = script['game_name']
        if game_name not in games:
            games[game_name] = {
                'count': 0,
                'keys': []
            }
        games[game_name]['count'] += 1
        games[game_name]['keys'].append(key)
    
    # Сортируем по алфавиту
    sorted_games = sorted(games.items(), key=lambda x: x[0].lower())
    return dict(sorted_games)

def get_catalog_page(page=0, games_per_page=6):
    """Получает страницу каталога"""
    games = get_unique_games()
    game_list = list(games.items())
    
    total_pages = ceil(len(game_list) / games_per_page)
    
    # Проверяем корректность страницы
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * games_per_page
    end_idx = start_idx + games_per_page
    page_games = game_list[start_idx:end_idx]
    
    return {
        'games': page_games,
        'current_page': page,
        'total_pages': total_pages,
        'total_games': len(game_list)
    }

def create_catalog_markup(page_data):
    """Создает клавиатуру для каталога"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Добавляем кнопки игр
    for game_name, game_data in page_data['games']:
        count = game_data['count']
        markup.add(InlineKeyboardButton(
            f"🎮 {game_name} ({count})", 
            callback_data=f"game_{game_name}_{page_data['current_page']}"
        ))
    
    # Добавляем навигацию
    nav_buttons = []
    if page_data['current_page'] > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"catalog_{page_data['current_page'] - 1}"))
    
    if page_data['current_page'] < page_data['total_pages'] - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"catalog_{page_data['current_page'] + 1}"))
    
    if nav_buttons:
        markup.add(*nav_buttons)
    
    # Добавляем кнопку возврата в главное меню
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    
    return markup

def get_game_scripts(game_name):
    """Получает все скрипты для конкретной игры"""
    SCRIPTS_DATABASE = load_scripts_dynamic()
    scripts = []
    
    for key, script in SCRIPTS_DATABASE.items():
        if script['game_name'] == game_name:
            script_data = script.copy()
            script_data['key'] = key
            scripts.append(script_data)
    
    return scripts

def create_game_scripts_markup(game_name, page=0, scripts_per_page=5):
    """Создает клавиатуру со скриптами игры"""
    scripts = get_game_scripts(game_name)
    
    total_pages = ceil(len(scripts) / scripts_per_page)
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * scripts_per_page
    end_idx = start_idx + scripts_per_page
    page_scripts = scripts[start_idx:end_idx]
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Добавляем кнопки скриптов
    for i, script in enumerate(page_scripts, start_idx + 1):
        uses = script.get('uses', 0)
        btn_text = f"📜 Скрипт {i} ({uses}👍)"
        markup.add(InlineKeyboardButton(
            btn_text, 
            callback_data=f"script_{script['key']}_{game_name}_{page}"
        ))
    
    # Навигация между скриптами
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"gamescripts_{game_name}_{page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"gamescripts_{game_name}_{page + 1}"))
    
    if nav_buttons:
        markup.add(*nav_buttons)
    
    # Кнопка возврата в каталог
    markup.add(InlineKeyboardButton("📂 Назад в каталог", callback_data="catalog_0"))
    
    return markup, len(scripts)

# ============= ОБНОВЛЕННЫЙ СТАРТ =============

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Проверяем ключ в аргументах
    args = message.text.split()
    if len(args) > 1:
        key = args[1].upper()
        SCRIPTS_DATABASE = load_scripts_dynamic()
        
        if key in SCRIPTS_DATABASE:
            # Админ всегда проходит без проверки
            if user_id != OWNER_ID:
                if not check_subscription(user_id):
                    show_subscription_message(message.chat.id, first_name)
                    return
            
            script = SCRIPTS_DATABASE[key]
            
            # Увеличиваем счетчик использований
            if 'uses' not in script:
                script['uses'] = 0
            script['uses'] += 1
            save_scripts_dynamic(SCRIPTS_DATABASE)
            
            # Формируем текст ответа
            text = f"🎮 *{script['game_name']}*\n\n"
            text += f"📝 *Описание:*\n{script['description']}\n\n"
            text += f"📥 *Код для эксплоита:*\n\n"
            text += f"```lua\n{script['loadstring']}\n```\n\n"
            text += f"🔑 Ключ: `{key}`\n"
            text += f"📊 Использований: {script['uses']}"
            
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
                f"🔑 Ключ: `{key}`",
                parse_mode="Markdown"
            )
        return
    
    # Обычный старт без ключа
    # Админ всегда проходит без проверки
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            show_subscription_message(message.chat.id, first_name)
            return
    
    # Главное меню
    text = f"Здравствуй, {first_name}! 👋\n\n"
    text += "Скрипты — это не просто код и окно с кнопками, а картина художника-кодера, которая отображает его опыт владения языком Luau.\n\n"
    text += "✨ *Чем этот бот лучше многих?*\n"
    text += "• Легко получать — нажал на кнопку и получил 🤩\n"
    text += "• Только актуальные скрипты — проверяются админами ✅\n"
    text += "• Всегда работает — бот оптимизирован и не имеет багов ⚙️\n\n"
    text += f"📢 *Для получения скриптов, загляни в наш канал* {CHANNEL} — там публикуются скрипты на большое количество игр 🔥"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 Наш канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
        InlineKeyboardButton("📂 Каталог скриптов", callback_data="catalog_0")
    )
    
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# ============= ОБРАБОТЧИКИ КОЛБЭКОВ =============

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu_callback(call):
    """Возврат в главное меню"""
    user_id = call.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            bot.answer_callback_query(call.id, "❌ Сначала подпишитесь на канал!", show_alert=True)
            return
    
    first_name = call.from_user.first_name
    
    text = f"Здравствуй, {first_name}! 👋\n\n"
    text += "Скрипты — это не просто код и окно с кнопками, а картина художника-кодера, которая отображает его опыт владения языком Luau.\n\n"
    text += "✨ *Чем этот бот лучше многих?*\n"
    text += "• Легко получать — нажал на кнопку и получил 🤩\n"
    text += "• Только актуальные скрипты — проверяются админами ✅\n"
    text += "• Всегда работает — бот оптимизирован и не имеет багов ⚙️\n\n"
    text += f"📢 *Для получения скриптов, загляни в наш канал* {CHANNEL} — там публикуются скрипты на большое количество игр 🔥"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 Наш канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
        InlineKeyboardButton("📂 Каталог скриптов", callback_data="catalog_0")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('catalog_'))
def catalog_callback(call):
    """Обработчик каталога"""
    user_id = call.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            bot.answer_callback_query(call.id, "❌ Сначала подпишитесь на канал!", show_alert=True)
            return
    
    try:
        page = int(call.data.split('_')[1])
    except:
        page = 0
    
    page_data = get_catalog_page(page)
    
    if not page_data['games']:
        bot.answer_callback_query(call.id, "📭 Каталог пуст!", show_alert=True)
        return
    
    text = f"📂 *Каталог скриптов*\n\n"
    text += f"🎮 *Всего игр:* {page_data['total_games']}\n"
    text += f"📄 *Страница:* {page_data['current_page'] + 1}/{page_data['total_pages']}\n\n"
    text += "👇 *Выберите игру:*"
    
    markup = create_catalog_markup(page_data)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('game_'))
def game_callback(call):
    """Обработчик выбора игры"""
    user_id = call.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            bot.answer_callback_query(call.id, "❌ Сначала подпишитесь на канал!", show_alert=True)
            return
    
    try:
        parts = call.data.split('_')
        game_name = '_'.join(parts[1:-1])  # Обрабатываем названия с пробелами
        from_page = parts[-1]
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!", show_alert=True)
        return
    
    scripts = get_game_scripts(game_name)
    
    if not scripts:
        bot.answer_callback_query(call.id, "❌ Скрипты не найдены!", show_alert=True)
        return
    
    markup, total_scripts = create_game_scripts_markup(game_name, 0)
    
    text = f"🎮 *{game_name}*\n\n"
    text += f"📜 *Доступно скриптов:* {total_scripts}\n"
    text += f"📊 *Всего скачиваний:* {sum(s.get('uses', 0) for s in scripts)}\n\n"
    text += "👇 *Выберите скрипт:*"
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('gamescripts_'))
def game_scripts_page_callback(call):
    """Перелистывание страниц скриптов игры"""
    user_id = call.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            bot.answer_callback_query(call.id, "❌ Сначала подпишитесь на канал!", show_alert=True)
            return
    
    try:
        parts = call.data.split('_')
        game_name = '_'.join(parts[1:-1])
        page = int(parts[-1])
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!", show_alert=True)
        return
    
    scripts = get_game_scripts(game_name)
    
    if not scripts:
        bot.answer_callback_query(call.id, "❌ Скрипты не найдены!", show_alert=True)
        return
    
    markup, total_scripts = create_game_scripts_markup(game_name, page)
    
    text = f"🎮 *{game_name}*\n\n"
    text += f"📜 *Доступно скриптов:* {total_scripts}\n"
    text += f"📊 *Всего скачиваний:* {sum(s.get('uses', 0) for s in scripts)}\n\n"
    text += "👇 *Выберите скрипт:*"
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('script_'))
def script_callback(call):
    """Обработчик выбора скрипта"""
    user_id = call.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            bot.answer_callback_query(call.id, "❌ Сначала подпишитесь на канал!", show_alert=True)
            return
    
    try:
        parts = call.data.split('_')
        key = parts[1]
        game_name = '_'.join(parts[2:-1])
        page = parts[-1]
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!", show_alert=True)
        return
    
    SCRIPTS_DATABASE = load_scripts_dynamic()
    
    if key not in SCRIPTS_DATABASE:
        bot.answer_callback_query(call.id, "❌ Скрипт не найден!", show_alert=True)
        return
    
    script = SCRIPTS_DATABASE[key]
    
    # Увеличиваем счетчик использований
    if 'uses' not in script:
        script['uses'] = 0
    script['uses'] += 1
    save_scripts_dynamic(SCRIPTS_DATABASE)
    
    # Формируем текст ответа
    text = f"🎮 *{script['game_name']}*\n\n"
    text += f"📝 *Описание:*\n{script['description']}\n\n"
    text += f"📥 *Код для эксплоита:*\n\n"
    text += f"```lua\n{script['loadstring']}\n```\n\n"
    text += f"🔑 Ключ: `{key}`\n"
    text += f"📊 Использований: {script['uses']}"
    
    # Создаем кнопки для навигации
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📂 Назад к скриптам", callback_data=f"game_{game_name}_{page}"),
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription_callback(call):
    """Проверка подписки"""
    user_id = call.from_user.id
    
    if check_subscription(user_id):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ Отлично! Вы подписаны!\n\n"
                 f"Теперь вы можете пользоваться всеми функциями бота.",
            parse_mode="Markdown"
        )
        # Показываем главное меню
        time.sleep(1)
        main_menu_callback(call)
    else:
        bot.answer_callback_query(
            call.id,
            "❌ Вы еще не подписались на канал!",
            show_alert=True
        )

@bot.callback_query_handler(func=lambda call: call.data == "noop")
def noop_callback(call):
    """Пустой колбэк для кнопок-заглушек"""
    bot.answer_callback_query(call.id)

# ============= ОСТАЛЬНЫЕ КОМАНДЫ =============

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            show_subscription_message(message.chat.id, message.from_user.first_name)
            return
    
    text = f"🤖 *Помощь по боту*\n\n"
    text += "📌 *Основные команды:*\n"
    text += "/start - главное меню\n"
    text += "/search <игра> - поиск скриптов\n"
    text += "/stats - статистика бота\n"
    text += "/check <ключ> - проверка ключа\n\n"
    text += "📂 *Каталог скриптов:*\n"
    text += "1. Нажмите '📂 Каталог скриптов'\n"
    text += "2. Выберите игру\n"
    text += "3. Выберите скрипт\n"
    text += "4. Скопируйте код\n\n"
    text += f"📢 *Канал:* {CHANNEL}\n"
    text += "🤝 *Партнёр:* @loriscript"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['search'])
def search_command(message):
    user_id = message.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            show_subscription_message(message.chat.id, message.from_user.first_name)
            return
    
    SCRIPTS_DATABASE = load_scripts_dynamic()
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(
            message.chat.id,
            "🔍 *Использование:*\n`/search <название игры>`\n\n"
            "Пример: `/search 99 Nights`",
            parse_mode="Markdown"
        )
        return
    
    search_term = args[1].lower()
    found_games = {}
    
    for key, script in SCRIPTS_DATABASE.items():
        if search_term in script['game_name'].lower():
            game_name = script['game_name']
            if game_name not in found_games:
                found_games[game_name] = {
                    'count': 0,
                    'uses': 0,
                    'keys': []
                }
            found_games[game_name]['count'] += 1
            found_games[game_name]['uses'] += script.get('uses', 0)
            found_games[game_name]['keys'].append(key)
    
    if not found_games:
        bot.send_message(
            message.chat.id,
            f"❌ Не найдено игр по запросу: *{search_term}*",
            parse_mode="Markdown"
        )
        return
    
    text = f"🔍 *Результаты поиска '{search_term}':*\n\n"
    
    for game_name, data in list(found_games.items())[:10]:
        text += f"🎮 *{game_name}*\n"
        text += f"📜 Скриптов: {data['count']}\n"
        text += f"📊 Скачиваний: {data['uses']}\n"
        
        # Создаем кнопку для перехода к игре
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"📂 Открыть {game_name}", callback_data=f"game_{game_name}_0"))
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        text = ""
    
    if len(found_games) > 10:
        bot.send_message(
            message.chat.id,
            f"📌 Найдено {len(found_games)} игр. Показаны первые 10.",
            parse_mode="Markdown"
        )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    
    if user_id != OWNER_ID:
        if not check_subscription(user_id):
            show_subscription_message(message.chat.id, message.from_user.first_name)
            return
    
    games = get_unique_games()
    SCRIPTS_DATABASE = load_scripts_dynamic()
    
    total_scripts = len(SCRIPTS_DATABASE)
    total_uses = sum(script.get('uses', 0) for script in SCRIPTS_DATABASE.values())
    
    text = f"📊 *Статистика бота*\n\n"
    text += f"📦 Всего скриптов: {total_scripts}\n"
    text += f"🎮 Уникальных игр: {len(games)}\n"
    text += f"📥 Всего скачиваний: {total_uses}\n\n"
    
    # Топ-5 игр по скачиваниям
    top_games = []
    for game_name, data in games.items():
        total_game_uses = 0
        for key in data['keys']:
            total_game_uses += SCRIPTS_DATABASE.get(key, {}).get('uses', 0)
        top_games.append((game_name, total_game_uses, data['count']))
    
    top_games.sort(key=lambda x: x[1], reverse=True)
    
    if top_games[:5]:
        text += "🏆 *Топ-5 игр по скачиваниям:*\n"
        for i, (game_name, uses, count) in enumerate(top_games[:5], 1):
            text += f"{i}. *{game_name}*: {count} скриптов, {uses} скач.\n"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ... (остальной код обработки добавления скриптов админом остается без изменений)

# ============= ЗАПУСК БОТА =============

print("=" * 50)
print("🤖 Бот запущен!")
print(f"👑 Админ ID: {OWNER_ID}")
print(f"📢 Канал: {CHANNEL}")
print(f"📂 Каталог скриптов: Включен")
print("=" * 50)

try:
    bot.polling(none_stop=True, skip_pending=True, timeout=30)
except Exception as e:
    print(f"❌ Ошибка: {e}")