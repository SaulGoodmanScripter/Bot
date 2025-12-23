import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import time
import os
import random
import re
from datetime import datetime
import html

# ============= НАСТРОЙКИ =============

# Получаем токен 
TOKEN = "8318026349:AAEncQY0tBB_gnrpmGGtRv-Bk_RgHOHFcaU"

# Проверяем, что токен загрузился
if not TOKEN:
    print("=" * 50)
    print("❌ ОШИБКА: Не найден BOT_TOKEN в переменных окружения!")
    print("Создайте файл .env или установите переменную окружения:")
    print("BOT_TOKEN=ваш_токен_бота")
    exit(1)

print(f"✅ Токен загружен! Начинается на: {TOKEN[:15]}...")

bot = telebot.TeleBot(TOKEN)

# ID владельца бота
OWNER_ID = 6397071501  # Замените на ваш ID

# ============= РАБОТА С ДАННЫМИ =============

def load_data():
    """Загружает сохранённые каналы и посты"""
    try:
        with open('channels.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "channels": {},
            "user_channels": {},
            "posts": {}
        }

def save_data(data):
    """Сохраняет данные в JSON"""
    try:
        with open('channels.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

# Загружаем данные
DATA = load_data()

# Временное хранилище для создания постов
user_temp_data = {}

# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

def validate_markdown(text):
    """Проверяет и исправляет Markdown разметку"""
    if not text:
        return text
    
    # Экранируем специальные символы для HTML разметки
    text = html.escape(text)
    
    # Исправляем незакрытые теги
    tags_to_check = ['**', '__', '`']
    
    for tag in tags_to_check:
        count = text.count(tag)
        if count % 2 != 0:  # Если нечетное количество тегов
            # Удаляем все эти теги
            text = text.replace(tag, '')
    
    # Проверяем ссылки [текст](ссылка)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    def validate_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        # Проверяем, что URL начинается с http/https
        if not re.match(r'^https?://', link_url):
            return f'[{link_text}](https://{link_url})'
        return match.group(0)
    
    text = re.sub(link_pattern, validate_link, text)
    
    return text

def escape_markdown(text):
    """Экранирует спецсимволы Markdown"""
    if not text:
        return text
    
    # Список символов, которые нужно экранировать
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def clear_user_data(user_id):
    """Очищает временные данные пользователя"""
    if user_id in user_temp_data:
        del user_temp_data[user_id]

# ============= СТАРТ =============
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📝 Создать пост"),
        KeyboardButton("📢 Мои каналы")
    )
    
    if message.from_user.id == OWNER_ID:
        markup.add(
            KeyboardButton("⚙️ Настройки"),
            KeyboardButton("📊 Статистика")
        )
    
    welcome_text = """👋 Привет! Я бот для создания постов с кнопками и картинками.

📝 **Возможности:**
• Создание постов с текстом
• Добавление кнопок со ссылками
• Прикрепление фото/картинок
• Публикация в Telegram каналы

Выберите действие:"""
    
    try:
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка при отправке start: {e}")
        # Пробуем без разметки
        bot.send_message(
            message.chat.id,
            welcome_text.replace("**", ""),
            reply_markup=markup
        )

# ============= СОЗДАНИЕ ПОСТА =============
@bot.message_handler(func=lambda message: message.text == "📝 Создать пост")
def create_post_step1(message):
    user_id = str(message.from_user.id)
    user_temp_data[user_id] = {
        "step": "select_channel",
        "buttons": [],
        "media": None,
        "media_type": None
    }
    
    # Проверяем, есть ли у пользователя сохранённые каналы
    user_channels = DATA.get("user_channels", {}).get(user_id, [])
    
    if user_channels:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        
        for channel_info in user_channels:
            channel_name = channel_info.get("name", channel_info["id"])
            markup.add(KeyboardButton(f"📢 {channel_name}"))
        
        markup.add(
            KeyboardButton("➕ Новый канал"), 
            KeyboardButton("❌ Отмена")
        )
        
        bot.send_message(
            message.chat.id,
            "📢 Выберите канал для публикации:",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "📝 Введите ID или username канала:\n\n"
            "Примеры:\n"
            "• @mychannel (публичный)\n"
            "• -1001234567890 (приватный)\n\n"
            "ℹ️ Как получить ID канала:\n"
            "1. Добавьте бота в канал как администратора\n"
            "2. Отправьте сообщение в канал\n"
            "3. Перешлите его боту @username_to_id_bot",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))
        )
        user_temp_data[user_id]["step"] = "enter_channel"

# ============= ОБРАБОТКА ВЫБОРА КАНАЛА =============
@bot.message_handler(func=lambda message: message.text.startswith("📢 ") or 
                     (str(message.from_user.id) in user_temp_data and 
                      user_temp_data[str(message.from_user.id)].get("step") == "enter_channel"))
def process_channel_selection(message):
    user_id = str(message.from_user.id)
    
    if message.text == "❌ Отмена":
        clear_user_data(user_id)
        start(message)
        return
    
    if message.text.startswith("📢 "):
        # Ищем канал в сохранённых
        selected_name = message.text[2:]
        user_channels = DATA.get("user_channels", {}).get(user_id, [])
        
        channel = None
        for channel_info in user_channels:
            if channel_info.get("name", channel_info["id"]) == selected_name:
                channel = channel_info["id"]
                break
        
        if not channel:
            channel = selected_name
    else:
        channel = message.text.strip()
    
    # Проверяем формат канала
    if not (channel.startswith('@') or (channel.startswith('-') and channel[1:].isdigit())):
        bot.send_message(
            message.chat.id,
            "⚠️ Неверный формат канала!\n\n"
            "Используйте:\n"
            "• @username для публичных каналов\n"
            "• -1001234567890 для приватных каналов",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))
        )
        return
    
    # Сохраняем канал
    user_temp_data[user_id]["channel"] = channel
    
    # Добавляем в список каналов пользователя
    if user_id not in DATA["user_channels"]:
        DATA["user_channels"][user_id] = []
    
    # Проверяем, есть ли уже такой канал
    channel_exists = False
    for ch in DATA["user_channels"][user_id]:
        if ch["id"] == channel:
            channel_exists = True
            break
    
    if not channel_exists:
        # Получаем информацию о канале
        try:
            chat = bot.get_chat(channel)
            channel_name = chat.title
        except Exception as e:
            print(f"Ошибка получения информации о канале: {e}")
            channel_name = channel
        
        DATA["user_channels"][user_id].append({
            "id": channel,
            "name": channel_name,
            "added": datetime.now().strftime("%d.%m.%Y %H:%M")
        })
        save_data(DATA)
    
    # Переходим к следующему шагу
    user_temp_data[user_id]["step"] = "add_content"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📝 Ввести текст"),
        KeyboardButton("📸 Добавить фото"),
        KeyboardButton("❌ Отмена")
    )
    
    bot.send_message(
        message.chat.id,
        f"✅ Канал выбран: {channel}\n\n"
        "Выберите, что добавить первым:",
        reply_markup=markup
    )

# ============= ВЫБОР ТИПА КОНТЕНТА =============
@bot.message_handler(func=lambda message: message.text in ["📝 Ввести текст", "📸 Добавить фото"])
def choose_content_type(message):
    user_id = str(message.from_user.id)
    
    if message.text == "📝 Ввести текст":
        user_temp_data[user_id]["step"] = "enter_text"
        bot.send_message(
            message.chat.id,
            "📝 Введите текст поста:\n\n"
            "ℹ️ Поддерживается HTML разметка:\n"
            "• <b>жирный текст</b>\n"
            "• <i>курсив</i>\n"
            "• <a href='http://example.com'>ссылка</a>\n"
            "• <code>код</code>",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена")),
            parse_mode="HTML"
        )
    
    elif message.text == "📸 Добавить фото":
        user_temp_data[user_id]["step"] = "add_photo"
        bot.send_message(
            message.chat.id,
            "📸 Отправьте фото для поста:\n\n"
            "ℹ️ Можно отправить фото или картинку",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))
        )

# ============= ОБРАБОТКА ФОТО =============
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_temp_data or user_temp_data[user_id].get("step") != "add_photo":
        return
    
    # Берём фото максимального качества
    file_id = message.photo[-1].file_id
    
    # Сохраняем медиа
    user_temp_data[user_id]["media"] = file_id
    user_temp_data[user_id]["media_type"] = "photo"
    user_temp_data[user_id]["step"] = "enter_text"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📝 Ввести текст"),
        KeyboardButton("👁️ Предпросмотр"),
        KeyboardButton("❌ Отмена")
    )
    
    bot.send_message(
        message.chat.id,
        "✅ Фото добавлено!\n\n"
        "Теперь введите текст поста или посмотрите предпросмотр:",
        reply_markup=markup
    )

# ============= ВВОД ТЕКСТА ПОСТА =============
@bot.message_handler(func=lambda message: 
                     str(message.from_user.id) in user_temp_data and 
                     user_temp_data[str(message.from_user.id)].get("step") == "enter_text")
def process_post_text(message):
    user_id = str(message.from_user.id)
    
    if message.text == "❌ Отмена":
        clear_user_data(user_id)
        start(message)
        return
    
    # Сохраняем текст как есть, без валидации
    user_temp_data[user_id]["text"] = message.text
    user_temp_data[user_id]["step"] = "add_buttons"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("➕ Добавить кнопку"),
        KeyboardButton("👁️ Предпросмотр"),
        KeyboardButton("🚀 Опубликовать"),
        KeyboardButton("❌ Отмена")
    )
    
    bot.send_message(
        message.chat.id,
        "✅ Текст сохранен!\n\n"
        "Теперь вы можете добавить кнопки или опубликовать пост:",
        reply_markup=markup
    )

# ============= ДОБАВЛЕНИЕ КНОПОК =============
@bot.message_handler(func=lambda message: message.text == "➕ Добавить кнопку")
def add_button_step1(message):
    user_id = str(message.from_user.id)
    user_temp_data[user_id]["step"] = "enter_button_text"
    
    bot.send_message(
        message.chat.id,
        "✏️ Введите текст для кнопки (например: 'Нажми меня', 'Купить', 'Подписаться'):",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))
    )

@bot.message_handler(func=lambda message: 
                     str(message.from_user.id) in user_temp_data and 
                     user_temp_data[str(message.from_user.id)].get("step") == "enter_button_text")
def process_button_text(message):
    user_id = str(message.from_user.id)
    
    if message.text == "❌ Отмена":
        user_temp_data[user_id]["step"] = "add_buttons"
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Добавить кнопку"),
            KeyboardButton("👁️ Предпросмотр"),
            KeyboardButton("🚀 Опубликовать"),
            KeyboardButton("❌ Отмена")
        )
        bot.send_message(message.chat.id, "Действие отменено", reply_markup=markup)
        return
    
    user_temp_data[user_id]["button_temp_text"] = message.text
    user_temp_data[user_id]["step"] = "enter_button_url"
    
    bot.send_message(
        message.chat.id,
        "🔗 Теперь введите URL для кнопки (например: https://example.com):",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))
    )

@bot.message_handler(func=lambda message: 
                     str(message.from_user.id) in user_temp_data and 
                     user_temp_data[str(message.from_user.id)].get("step") == "enter_button_url")
def process_button_url(message):
    user_id = str(message.from_user.id)
    
    if message.text == "❌ Отмена":
        user_temp_data[user_id]["step"] = "add_buttons"
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Добавить кнопку"),
            KeyboardButton("👁️ Предпросмотр"),
            KeyboardButton("🚀 Опубликовать"),
            KeyboardButton("❌ Отмена")
        )
        bot.send_message(message.chat.id, "Действие отменено", reply_markup=markup)
        return
    
    # Проверяем URL
    url = message.text.strip()
    if not re.match(r'^(https?://|tg://)', url):
        bot.send_message(
            message.chat.id,
            "❌ Неверный формат URL! Начинайте с:\n"
            "• http:// или https://\n"
            "• tg://\n\n"
            "Попробуйте еще раз:"
        )
        return
    
    # Добавляем кнопку в список
    button_data = {
        "text": user_temp_data[user_id]["button_temp_text"],
        "url": url
    }
    
    if "buttons" not in user_temp_data[user_id]:
        user_temp_data[user_id]["buttons"] = []
    
    user_temp_data[user_id]["buttons"].append(button_data)
    
    # Удаляем временные данные
    del user_temp_data[user_id]["button_temp_text"]
    user_temp_data[user_id]["step"] = "add_buttons"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("➕ Ещё кнопку"),
        KeyboardButton("👁️ Предпросмотр"),
        KeyboardButton("🚀 Опубликовать"),
        KeyboardButton("❌ Отмена")
    )
    
    buttons_count = len(user_temp_data[user_id]["buttons"])
    bot.send_message(
        message.chat.id,
        f"✅ Кнопка добавлена! Всего кнопок: {buttons_count}\n\n"
        "Выберите действие:",
        reply_markup=markup
    )

# ============= ПРЕДПРОСМОТР =============
@bot.message_handler(func=lambda message: message.text == "👁️ Предпросмотр")
def show_preview_handler(message):
    user_id = str(message.from_user.id)
    
    try:
        show_preview(message.chat.id, user_id)
    except Exception as e:
        print(f"Ошибка при предпросмотре: {e}")
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка при создании предпросмотра: {str(e)}"
        )

def show_preview(chat_id, user_id):
    data = user_temp_data[user_id]
    
    # Создаем клавиатуру с кнопками
    markup = None
    if "buttons" in data and data["buttons"]:
        markup = InlineKeyboardMarkup(row_width=1)
        for button in data["buttons"]:
            markup.add(InlineKeyboardButton(
                text=button["text"],
                url=button["url"]
            ))
    
    # Формируем текст предпросмотра
    preview_text = "👁️ <b>ПРЕДПРОСМОТР ПОСТА</b>\n\n"
    
    if data.get("channel"):
        preview_text += f"📢 <b>Канал:</b> <code>{data['channel']}</code>\n\n"
    else:
        preview_text += "📢 <b>Режим:</b> Предпросмотр\n\n"
    
    preview_text += "📝 <b>Текст поста:</b>\n"
    preview_text += data.get("text", "Не указан") + "\n\n"
    
    if "buttons" in data and data["buttons"]:
        preview_text += "🔘 <b>Кнопки:</b>\n"
        for i, button in enumerate(data["buttons"], 1):
            preview_text += f"{i}. {button['text']} → {button['url']}\n"
    
    # Пытаемся отправить предпросмотр
    try:
        if data.get("media") and data.get("media_type") == "photo":
            if markup:
                bot.send_photo(
                    chat_id,
                    data["media"],
                    caption=preview_text,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            else:
                bot.send_photo(
                    chat_id,
                    data["media"],
                    caption=preview_text,
                    parse_mode="HTML"
                )
        else:
            if markup:
                bot.send_message(
                    chat_id,
                    preview_text,
                    reply_markup=markup,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            else:
                bot.send_message(
                    chat_id,
                    preview_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
    except Exception as e:
        print(f"Ошибка отправки предпросмотра: {e}")
        # Пробуем без разметки
        preview_text_simple = preview_text.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "")
        
        if data.get("media") and data.get("media_type") == "photo":
            if markup:
                bot.send_photo(
                    chat_id,
                    data["media"],
                    caption=preview_text_simple,
                    reply_markup=markup
                )
            else:
                bot.send_photo(
                    chat_id,
                    data["media"],
                    caption=preview_text_simple
                )
        else:
            if markup:
                bot.send_message(
                    chat_id,
                    preview_text_simple,
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                bot.send_message(
                    chat_id,
                    preview_text_simple,
                    disable_web_page_preview=True
                )
    
    # Кнопки действий
    action_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    action_markup.add(
        KeyboardButton("✏️ Изменить текст"),
        KeyboardButton("🖼 Изменить фото"),
        KeyboardButton("🔘 Изменить кнопки")
    )
    action_markup.add(
        KeyboardButton("🚀 Опубликовать"),
        KeyboardButton("❌ Отмена")
    )
    
    bot.send_message(
        chat_id,
        "Выберите действие:",
        reply_markup=action_markup
    )

# ============= РЕДАКТИРОВАНИЕ =============
@bot.message_handler(func=lambda message: message.text in ["✏️ Изменить текст", "🖼 Изменить фото", "🔘 Изменить кнопки"])
def edit_post(message):
    user_id = str(message.from_user.id)
    
    if message.text == "✏️ Изменить текст":
        user_temp_data[user_id]["step"] = "enter_text"
        bot.send_message(
            message.chat.id,
            "📝 Введите новый текст поста:",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))
        )
    
    elif message.text == "🖼 Изменить фото":
        user_temp_data[user_id]["step"] = "add_photo"
        bot.send_message(
            message.chat.id,
            "📸 Отправьте новое фото или напишите 'удалить' чтобы убрать фото:",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))
        )
    
    elif message.text == "🔘 Изменить кнопки":
        user_temp_data[user_id]["step"] = "add_buttons"
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Добавить кнопку"),
            KeyboardButton("🗑 Удалить все кнопки"),
            KeyboardButton("👁️ Предпросмотр"),
            KeyboardButton("❌ Отмена")
        )
        
        buttons_count = len(user_temp_data[user_id].get("buttons", []))
        bot.send_message(
            message.chat.id,
            f"🔘 Текущее количество кнопок: {buttons_count}\n\n"
            "Выберите действие:",
            reply_markup=markup
        )

@bot.message_handler(func=lambda message: message.text == "🗑 Удалить все кнопки")
def remove_all_buttons(message):
    user_id = str(message.from_user.id)
    
    if "buttons" in user_temp_data[user_id]:
        user_temp_data[user_id]["buttons"] = []
        bot.send_message(
            message.chat.id,
            "✅ Все кнопки удалены!",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
                KeyboardButton("➕ Добавить кнопку"),
                KeyboardButton("👁️ Предпросмотр"),
                KeyboardButton("🚀 Опубликовать"),
                KeyboardButton("❌ Отмена")
            )
        )

# ============= ПУБЛИКАЦИЯ ПОСТА =============
@bot.message_handler(func=lambda message: message.text == "🚀 Опубликовать")
def publish_post_handler(message):
    user_id = str(message.from_user.id)
    
    try:
        publish_post(message.chat.id, user_id)
    except Exception as e:
        print(f"Ошибка при публикации: {e}")
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка при публикации: {str(e)}",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📝 Создать пост"))
        )

def publish_post(chat_id, user_id):
    data = user_temp_data[user_id]
    
    # Проверяем, есть ли канал для публикации
    if not data.get("channel"):
        bot.send_message(
            chat_id,
            "❌ Не выбран канал для публикации!\n\n"
            "Пожалуйста, сначала выберите канал.",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📝 Создать пост"))
        )
        return
    
    # Проверяем, есть ли текст
    if not data.get("text"):
        bot.send_message(
            chat_id,
            "❌ Текст поста не может быть пустым!",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("✏️ Изменить текст"))
        )
        return
    
    # Создаем клавиатуру с кнопками
    markup = None
    if "buttons" in data and data["buttons"]:
        markup = InlineKeyboardMarkup(row_width=1)
        for button in data["buttons"]:
            markup.add(InlineKeyboardButton(
                text=button["text"],
                url=button["url"]
            ))
    
    # Пытаемся отправить в канал с HTML разметкой
    try:
        post_text = data["text"]
        
        if data.get("media") and data.get("media_type") == "photo":
            if markup:
                sent_message = bot.send_photo(
                    data["channel"],
                    data["media"],
                    caption=post_text,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            else:
                sent_message = bot.send_photo(
                    data["channel"],
                    data["media"],
                    caption=post_text,
                    parse_mode="HTML"
                )
        else:
            if markup:
                sent_message = bot.send_message(
                    data["channel"],
                    post_text,
                    reply_markup=markup,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            else:
                sent_message = bot.send_message(
                    data["channel"],
                    post_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
        
    except Exception as e:
        error_msg = str(e)
        print(f"Ошибка HTML разметки: {error_msg}")
        
        # Пробуем без разметки
        try:
            post_text_simple = post_text
            # Убираем HTML теги
            post_text_simple = re.sub(r'<[^>]+>', '', post_text_simple)
            
            if data.get("media") and data.get("media_type") == "photo":
                if markup:
                    sent_message = bot.send_photo(
                        data["channel"],
                        data["media"],
                        caption=post_text_simple,
                        reply_markup=markup
                    )
                else:
                    sent_message = bot.send_photo(
                        data["channel"],
                        data["media"],
                        caption=post_text_simple
                    )
            else:
                if markup:
                    sent_message = bot.send_message(
                        data["channel"],
                        post_text_simple,
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
                else:
                    sent_message = bot.send_message(
                        data["channel"],
                        post_text_simple,
                        disable_web_page_preview=True
                    )
                    
        except Exception as e2:
            print(f"Ошибка при публикации без разметки: {e2}")
            
            if "CHAT_ADMIN_REQUIRED" in error_msg:
                bot.send_message(
                    chat_id,
                    "❌ Бот не является администратором в этом канале!\n\n"
                    "Добавьте бота как администратора с правом отправки сообщений.",
                    reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📝 Создать пост"))
                )
            elif "chat not found" in error_msg.lower():
                bot.send_message(
                    chat_id,
                    "❌ Канал не найден!\n\n"
                    "Убедитесь, что:\n"
                    "1. Канал существует\n"
                    "2. Бот добавлен в канал\n"
                    "3. Вы правильно ввели ID/username",
                    reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📝 Создать пост"))
                )
            else:
                bot.send_message(
                    chat_id,
                    f"❌ Ошибка при публикации: {str(e2)}",
                    reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📝 Создать пост"))
                )
            return
    
    # Сохраняем как опубликованный пост
    post_id = f"{user_id}_{int(time.time())}"
    if "posts" not in DATA:
        DATA["posts"] = {}
    
    DATA["posts"][post_id] = {
        "user_id": user_id,
        "data": data.copy(),
        "created": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "published": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "status": "published",
        "message_id": sent_message.message_id if sent_message else None
    }
    
    save_data(DATA)
    
    # Очищаем временные данные
    clear_user_data(user_id)
    
    # Отправляем подтверждение
    success_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    success_markup.add(
        KeyboardButton("📝 Создать ещё"),
        KeyboardButton("🔙 На главную")
    )
    
    bot.send_message(
        chat_id,
        f"✅ <b>Пост успешно опубликован!</b>\n\n"
        f"📢 Канал: <code>{data['channel']}</code>\n"
        f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        f"📝 ID поста: <code>{post_id}</code>",
        parse_mode="HTML",
        reply_markup=success_markup
    )

# ============= МОИ КАНАЛЫ =============
@bot.message_handler(func=lambda message: message.text == "📢 Мои каналы")
def my_channels(message):
    user_id = str(message.from_user.id)
    
    user_channels = DATA.get("user_channels", {}).get(user_id, [])
    
    if not user_channels:
        bot.send_message(
            message.chat.id,
            "📭 У вас нет сохранённых каналов.\n\n"
            "Чтобы добавить канал, создайте новый пост.",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📝 Создать пост"))
        )
        return
    
    text = "📢 <b>Ваши каналы:</b>\n\n"
    for i, channel in enumerate(user_channels, 1):
        text += f"{i}. {channel['name']}\n"
        text += f"   ID: <code>{channel['id']}</code>\n"
        text += f"   Добавлен: {channel.get('added', 'Неизвестно')}\n\n"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🗑 Удалить канал"),
        KeyboardButton("📝 Создать пост"),
        KeyboardButton("🔙 На главную")
    )
    
    try:
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, text.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", ""), reply_markup=markup)

# ============= СТАТИСТИКА (для владельца) =============
@bot.message_handler(func=lambda message: message.text == "📊 Статистика" and message.from_user.id == OWNER_ID)
def statistics(message):
    total_users = len(DATA.get("user_channels", {}))
    total_posts = len(DATA.get("posts", {}))
    total_channels = sum(len(channels) for channels in DATA.get("user_channels", {}).values())
    
    stats_text = f"""
📊 <b>Статистика бота</b>

👥 Пользователей: {total_users}
📢 Каналов: {total_channels}
📂 Постов: {total_posts}

📅 Последнее обновление: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    try:
        bot.send_message(message.chat.id, stats_text, parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, stats_text.replace("<b>", "").replace("</b>", ""))

# ============= НАСТРОЙКИ =============
@bot.message_handler(func=lambda message: message.text == "⚙️ Настройки" and message.from_user.id == OWNER_ID)
def settings(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🗑 Очистить базу"),
        KeyboardButton("📤 Экспорт данных"),
        KeyboardButton("🔙 На главную")
    )
    
    bot.send_message(
        message.chat.id,
        "⚙️ <b>Настройки администратора:</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=markup
    )

# ============= ОБРАБОТКА НЕИЗВЕСТНЫХ КОМАНД =============
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    if message.text == "🔙 На главную":
        start(message)
    elif message.text == "📝 Создать ещё":
        create_post_step1(message)
    elif message.text == "🗑 Удалить канал":
        delete_channel_step1(message)
    elif message.text == "📤 Экспорт данных" and message.from_user.id == OWNER_ID:
        export_data(message)
    elif message.text == "🗑 Очистить базу" and message.from_user.id == OWNER_ID:
        clear_database(message)
    else:
        # Если команда неизвестна, предлагаем вернуться на главную
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 На главную"))
        bot.send_message(
            message.chat.id,
            "Неизвестная команда. Используйте кнопки меню.",
            reply_markup=markup
        )

def delete_channel_step1(message):
    user_id = str(message.from_user.id)
    user_channels = DATA.get("user_channels", {}).get(user_id, [])
    
    if not user_channels:
        bot.send_message(
            message.chat.id,
            "У вас нет сохранённых каналов для удаления.",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 На главную"))
        )
        return
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for channel in user_channels:
        markup.add(KeyboardButton(f"🗑 {channel['name']}"))
    markup.add(KeyboardButton("🔙 Назад"))
    
    bot.send_message(
        message.chat.id,
        "Выберите канал для удаления:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text.startswith("🗑 "))
def delete_channel(message):
    user_id = str(message.from_user.id)
    channel_name = message.text[2:]  # Убираем "🗑 "
    
    if user_id in DATA["user_channels"]:
        DATA["user_channels"][user_id] = [
            ch for ch in DATA["user_channels"][user_id] 
            if ch["name"] != channel_name
        ]
        save_data(DATA)
    
    bot.send_message(
        message.chat.id,
        f"✅ Канал '{channel_name}' удален.",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 На главную"))
    )

def export_data(message):
    try:
        export_json = json.dumps(DATA, ensure_ascii=False, indent=2)
        bot.send_document(
            message.chat.id,
            ("bot_data.json", export_json.encode('utf-8')),
            caption="📤 Экспорт данных бота"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка экспорта: {e}")

def clear_database(message):
    global DATA
    DATA = {
        "channels": {},
        "user_channels": {},
        "posts": {}
    }
    save_data(DATA)
    bot.send_message(message.chat.id, "✅ База данных очищена.")

# ============= ЗАПУСК БОТА =============
print("=" * 50)
print("🤖 Бот для создания постов запущен!")
print(f"👤 Владелец ID: {OWNER_ID}")
print("=" * 50)
print("✅ Бот готов к работе!")
print("📝 Используйте команду /start в Telegram")

try:
    bot.polling(none_stop=True, interval=0, timeout=60)
except Exception as e:
    print(f"❌ Ошибка при запуске бота: {e}")