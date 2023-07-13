import time
import telebot
import pymysql
from telebot import types
import key
from config import host, port, user, password, database

bot = telebot.TeleBot(key, parse_mode=None)

# Вызов главного меню с категориями постов
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('🏙Города')
    btn2 = types.KeyboardButton('🌲Природа')
    btn3 = types.KeyboardButton('🪆Культура')
    btn4 = types.KeyboardButton('📖История')
    btn5 = types.KeyboardButton('👨‍👩‍👧‍👦Люди')
    btn6 = types.KeyboardButton('🍀Разное')
    btn7 = types.KeyboardButton('➡Смотреть сайт')

    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)
    markup.row(btn7)
    bot.send_message(message.from_user.id, 'Выбери категорию', reply_markup=markup)

# Вызов постов соответствующих выбраной категории
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    list = ['🏙Города', '🌲Природа', '🪆Культура', '📖История', '👨‍👩‍👧‍👦Люди', '🍀Разное']

    if message.text in list:
        #  Для каждого вызова подключаемся к базе данных
        try:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("successfully connected...")
            print("#" * 20)

            # Для выбранной категории реализуем cursor и потом закрываем соединение с базой данных
            try:
                with connection.cursor() as cursor:
                    cat = list.index(message.text)+1
                    select_all_rows = f"SELECT * FROM mysite_post WHERE cat_id = {cat}"
                    cursor.execute(select_all_rows)
                    rows = cursor.fetchall()
                    markup = types.InlineKeyboardMarkup()

                    # Функция для отображение кнопок в боте (от 1 до 3 в ряд)
                    def button(i):
                        btn = types.InlineKeyboardButton(rows[i]['title'], callback_data=str(rows[i]['slug']))
                        i = i + 1
                        if i <= len(rows) - 1:
                            btn1 = types.InlineKeyboardButton(rows[i]['title'], callback_data=str(rows[i]['slug']))
                            i = i + 1
                            if i <= len(rows) - 1:
                                 btn2 = types.InlineKeyboardButton(rows[i]['title'], callback_data=str(rows[i]['slug']))
                                 markup.row(btn, btn1, btn2)
                            else:
                                 markup.row(btn, btn1)

                        else:
                            markup.row(btn)

                    i = 0
                    while i <= len(rows)-1:
                        button(i)
                        i = i + 3

                    bot.send_message(message.chat.id, 'Выбирете интересующее вас в категории: ' + message.text, reply_markup=markup)

           # Закрываем соединение с базой данных
            finally:
                connection.close()
                print("close connected...")
                print("#" * 10)


        except Exception as ex:
            print("Connection refused...")
            print(ex)

    elif message.text == '➡Смотреть сайт':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Перейти', url='https://openrussianow.ru'))
        bot.send_message(message.chat.id, "Сайт: openrussianow.ru", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "Неверная команда. Выбери категорию из меню")
        bot.send_message(message.chat.id, "/start")


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    # Для выбранного поста подлючаемся к базе данных
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("successfully connected...")
        print("#" * 20)

        # Вызываем cursor для все постов и потом, взависимости от выбранного поста, возвращаем описание и фото
        try:
            with connection.cursor() as cursor:

                select_all_rows = f"SELECT * FROM mysite_post"
                cursor.execute(select_all_rows)
                post = cursor.fetchall()

                for el in post:
                    if call.data == str(el['slug']):
                        markup = types.InlineKeyboardMarkup()
                        url = 'https://openrussianow.ru/post/' + str(el['slug'])
                        markup.add(types.InlineKeyboardButton('Смотреть на сайте', url=str(url)))
                        bot.send_message(call.message.chat.id, el['content'][:150] + '...')
                        if el['photo']:
                           bot.send_photo(call.message.chat.id, photo='https://openrussianow.ru/media/' + el['photo'], reply_markup=markup)
                        else:
                           bot.send_message(call.message.chat.id, "Здесь должно быть Фото", reply_markup=markup)

        # Закрываем соединение
        finally:
            connection.close()
            print("close connected...")
            print("#" * 10)

    except Exception as ex:
        print("Connection refused...")
        print(ex)

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        time.sleep(15)