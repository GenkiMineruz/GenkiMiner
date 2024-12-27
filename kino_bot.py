import telebot
from telebot import types

API_TOKEN = '8060008717:AAG5lTTOYw2zluDEhXPR1U6eEAXgqcsBEAA'  # Tokeningiz
ADMIN_USERNAME = 'DilshodNomozov'  # Hozirgi adminning username

bot = telebot.TeleBot(API_TOKEN)

linked_channels = []  # Ulangan kanallar ro'yxati
movies = {}  # Kinolarni saqlash: {'kinonomi': file_id}

# Admin panel
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.username == ADMIN_USERNAME:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📌 Kanalni ulash", "❌ Kanalni o'chirish")
        markup.row("🎥 Kino yuklash", "📚 Kinolar ro'yxati")
        markup.row("👤 Adminni o'zgartirish", "🔙 Chiqish")
        bot.send_message(message.chat.id, "Admin paneliga xush kelibsiz!", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Sizda admin paneliga kirish huquqi yo'q!")

# Tugmalarni boshqarish
@bot.message_handler(func=lambda message: message.text in ["📌 Kanalni ulash", "❌ Kanalni o'chirish", "🎥 Kino yuklash", "📚 Kinolar ro'yxati", "👤 Adminni o'zgartirish", "🔙 Chiqish"])
def handle_admin_buttons(message):
    if message.text == "📌 Kanalni ulash":
        bot.send_message(message.chat.id, "Kanal username-ni yuboring (masalan, @kanal_nomi):")
        bot.register_next_step_handler(message, add_channel)
    elif message.text == "❌ Kanalni o'chirish":
        bot.send_message(message.chat.id, "O'chiriladigan kanal username-ni yuboring:")
        bot.register_next_step_handler(message, remove_channel)
    elif message.text == "🎥 Kino yuklash":
        bot.send_message(message.chat.id, "Yuklanadigan kinoni yuboring (fayl yoki video):")
        bot.register_next_step_handler(message, upload_movie)
    elif message.text == "📚 Kinolar ro'yxati":
        if movies:
            movie_list = "\n".join(movies.keys())
            bot.send_message(message.chat.id, f"Yuklangan kinolar:\n{movie_list}")
        else:
            bot.send_message(message.chat.id, "Hozircha hech qanday kino yuklanmagan.")
    elif message.text == "👤 Adminni o'zgartirish":
        bot.send_message(message.chat.id, "Yangi admin username-ni yuboring (masalan, @yangiadmin):")
        bot.register_next_step_handler(message, change_admin)
    elif message.text == "🔙 Chiqish":
        bot.send_message(message.chat.id, "Admin paneldan chiqildi.", reply_markup=types.ReplyKeyboardRemove())

# Kanal ulash
def add_channel(message):
    channel_username = message.text
    if channel_username not in linked_channels:
        linked_channels.append(channel_username)
        bot.send_message(message.chat.id, f"{channel_username} kanal ulashdi!")
    else:
        bot.send_message(message.chat.id, "Bu kanal allaqachon ulashgan!")

# Kanalni o'chirish
def remove_channel(message):
    channel_username = message.text
    if channel_username in linked_channels:
        linked_channels.remove(channel_username)
        bot.send_message(message.chat.id, f"{channel_username} kanal olib tashlandi!")
    else:
        bot.send_message(message.chat.id, "Bu kanal ulanganlar ro'yxatida yo'q!")

# Kino yuklash
def upload_movie(message):
    if message.content_type in ['video', 'document']:
        file_id = message.video.file_id if message.content_type == 'video' else message.document.file_id
        bot.send_message(message.chat.id, "Kino nomini kiriting:")
        bot.register_next_step_handler(message, save_movie, file_id)
    else:
        bot.send_message(message.chat.id, "Faqat video yoki fayl yuboring!")

# Kino saqlash
def save_movie(message, file_id):
    movie_name = message.text
    if movie_name not in movies:
        movies[movie_name] = file_id
        bot.send_message(message.chat.id, f"'{movie_name}' nomli kino muvaffaqiyatli yuklandi!")
    else:
        bot.send_message(message.chat.id, "Bu nomdagi kino allaqachon yuklangan.")

# Adminni o'zgartirish
def change_admin(message):
    global ADMIN_USERNAME
    new_admin_username = message.text.lstrip('@')
    if new_admin_username:
        old_admin = ADMIN_USERNAME
        ADMIN_USERNAME = new_admin_username
        bot.send_message(message.chat.id, f"Admin muvaffaqiyatli o'zgartirildi!\nEski admin: @{old_admin}\nYangi admin: @{ADMIN_USERNAME}")
    else:
        bot.send_message(message.chat.id, "Noto'g'ri username kiritildi!")

# Obunani tekshirish
def check_subscription(user_id):
    for channel in linked_channels:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except Exception:
            return False
    return True

# Foydalanuvchilar uchun start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    if linked_channels:
        bot.send_message(message.chat.id, f"Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling: {', '.join(linked_channels)}")
    else:
        bot.send_message(message.chat.id, "Hozircha hech qanday kanal ulangan.")

# Botni ishga tushirish
bot.polling(none_stop=True)