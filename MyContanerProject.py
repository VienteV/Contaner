from Knowledge_basket import Knowledge_Basket
import telebot
from telebot import types
from telebot.types import InlineKeyboardButton
from datetime import date
import configparser
from Schedule import Schedule


config = configparser.ConfigParser()
config.read('settings.ini')

bot = telebot.TeleBot(config['telebot']['Token'])
def show_post_by_subject(for_what):
    database = Knowledge_Basket()
    callback_data = "show_post_by_subject" if for_what == "for_show" else "dell_post_by_subject"
    subjects_titles = database.show_subjects_titles()
    markup = types.InlineKeyboardMarkup()
    subjects_titles = [InlineKeyboardButton(text=i, callback_data = f'{callback_data}: {i}') for i in subjects_titles]
    for titles in subjects_titles:
        markup.add(titles)
    return markup

def show_or_dell_post_by_subject(subject_title, for_what):
    callback_data = "show_post" if for_what == "for_show" else "dell_post"
    database = Knowledge_Basket()
    posts_name = database.show_post_by_subject(subject_title.strip())
    posts_name_markup = [InlineKeyboardButton(text=i, callback_data = f'{callback_data}: {i}') for i in posts_name]
    markup = types.InlineKeyboardMarkup()
    for name in posts_name_markup:
        markup.add(name)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Показать все заголовки постов', callback_data='show_all_posts_title'))
    markup.add(InlineKeyboardButton(text='Добавить тему', callback_data='add_subject_title'))
    markup.add(InlineKeyboardButton(text='Посмотреть посты по темам', callback_data='show_post_by_subject'))
    markup.add(InlineKeyboardButton(text='Добавить пост', callback_data='add_post'))
    markup.add(InlineKeyboardButton(text='Посмотреть расписание фитнесс хауса на сегодня', callback_data='chek_schedule'))
    markup.add(InlineKeyboardButton(text='Удалить пост пост', callback_data='dell_post'))
    markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup2.add(types.KeyboardButton("/start"))
    bot.send_message(message.chat.id, "Привет, что будем делать?", reply_markup= markup2)
    bot.send_message(message.chat.id, "Вот возможные действия", reply_markup= markup)

@bot.message_handler(content_types=['photo'])
def photo(message):
    photo_id = message.photo[-1].file_id
    photo = bot.get_file(photo_id)
    photo = bot.download_file(photo.file_path)
    with open('photo.jpg', 'wb') as file:
        file.write(photo)
    bot.send_photo(message.chat.id, photo_id)

@bot.callback_query_handler(func=lambda call: True)
def call_back_func(callback):
    if callback.data == 'show_all_posts_title':
        database = Knowledge_Basket()
        posts_name = database.show_all_posts_title()
        posts_name_markup = [InlineKeyboardButton(text=i, callback_data = f'show_post: {i}') for i in posts_name]
        markup = types.InlineKeyboardMarkup()
        for name in posts_name_markup:
            markup.add(name)
        bot.send_message(callback.from_user.id, "Вот все посты", reply_markup = markup)
        
    elif callback.data == 'add_subject_title':
        bot.send_message(callback.from_user.id, "Введите название темы")
        bot.register_next_step_handler(callback.message, add_subject_title)

    elif callback.data == 'add_post':
        database = Knowledge_Basket()
        subjects_titles = database.show_subjects_titles()
        subjects_titles = [InlineKeyboardButton(text=i, callback_data = f'add_post_in_subject:{i}') for i in subjects_titles]
        markup = types.InlineKeyboardMarkup()
        for titles in subjects_titles:
            markup.add(titles)
        bot.send_message(callback.from_user.id, "Выберете область по которой хотите добавить пост",
                         reply_markup = markup)
        
    elif callback.data.split(':')[0] == 'add_post_in_subject':
        subject = callback.data.split(':')[1]
        bot.send_message(callback.from_user.id, "Введите название темы")
        bot.register_next_step_handler(callback.message, add_post_title, subject)
        
        
    elif callback.data.split(':')[0] == 'show_post':
        post_title = callback.data.split(':')[1]
        database = Knowledge_Basket()
        post = database.show_post(post_title)
        bot.send_message(callback.from_user.id, post[0][3])
        if post[0][-1]:
            picture = open(post[0][-1], 'rb')
            bot.send_photo(callback.from_user.id, picture)
                

    elif callback.data == 'show_post_by_subject':
        #выбираем предмет по которому будем смотреть посты пост
        markup = show_post_by_subject('for_show')
        bot.send_message(callback.from_user.id, "Выберете область по которой хотите увидеть посты",
                         reply_markup = markup)
        
    elif callback.data.split(':')[0] == 'show_post_by_subject':
        #показывает посты по определенному предмету
        subject_title = callback.data.split(':')[1]
        markup = show_or_dell_post_by_subject(subject_title, 'for_show')
        bot.send_message(callback.from_user.id, "Вот посты", reply_markup = markup)

    elif callback.data == 'chek_schedule':
        scedule = Schedule()
        s = Schedule()
        soup = s.get_padge()
        text = s.get_schedule(soup)
        bot.send_message(callback.from_user.id, f"Вот расписание фитнесхауса: {text}")

    elif callback.data == 'dell_post':
        #выбираем предмет по которому будем удалять посты
        markup = show_post_by_subject('for_dell')
        bot.send_message(callback.from_user.id, "Выберете область по которой хотите удалить посты",
                         reply_markup = markup)

    elif callback.data.split(':')[0] == 'dell_post_by_subject':
        subject_title = callback.data.split(':')[1].strip()
        subject_title = callback.data.split(':')[1]
        markup = show_or_dell_post_by_subject(subject_title, 'for_dell')
        bot.send_message(callback.from_user.id, "Вот посты", reply_markup = markup)
        
    elif callback.data.split(':')[0] == 'dell_post':
        post_title = callback.data.split(':')[1].strip()
        database = Knowledge_Basket()
        print(post_title)
        database.dell_post(post_title)
        bot.send_message(callback.from_user.id, 'Пост был удален')


def cancel_command(func):
    #Декоратор
    def addendum(message, *args, **kwargs):
        if message.text == 'Отмена':
            bot.send_message(message.chat.id, 'Омена задачи')
        else:
            return func(message, *args, **kwargs)
    return addendum

@cancel_command
def add_post_title(message, subject):
    title = message.text
    bot.send_message(message.chat.id, 'Теперь прекрепите фото или отправьте что-нибудь')
    bot.register_next_step_handler(message, add_post_photo, subject, title)


        
@cancel_command
def add_post_photo(message, subject, title):
    try:
        photo_id = message.photo[-1].file_id
        photo_id = bot.get_file(photo_id)
        photo = bot.download_file(photo_id.file_path)
        photo_name = 'media\\' + str(date.today()) + subject + title
        with open(photo_name, 'wb') as file:
            file.write(photo)
        bot.send_message(message.chat.id, 'Теперь введите текст записи.')
    except:
        photo_name = None
        bot.send_message(message.chat.id, 'Изображение не добавлено. \n Теперь введите текст записи.')
    bot.register_next_step_handler(message, add_post, subject, title, photo_name)

@cancel_command
def add_post(message, subject, title, photo):
    text = message.text
    database = Knowledge_Basket()
    database.add_post(title, subject, text, photo)
    bot.send_message(message.chat.id, 'Запись добавлена')

@cancel_command
def add_subject_title(message):
    subject_title = message.text
    bot.send_message(message.chat.id, 'Введите описание темы')
    bot.register_next_step_handler(message, add_subject_description, subject_title = subject_title)

@cancel_command
def add_subject_description(message, subject_title):
    subject_description = message.text
    database = Knowledge_Basket()
    database.add_subject(subject_title,subject_description)
    bot.send_message(message.chat.id, 'Запись добавленна')




        
bot.polling(none_stop=True)
