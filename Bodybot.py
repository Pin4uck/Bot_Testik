import telebot
from exchange import secrets
import currency_try_except


bot = telebot.TeleBot(secrets.TOKEN)
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Привет', 'Пока')


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я могу показать вам курсы валют.\n' +
        'Чтобы узнать курсы валют, нажмите /exchange.\n' +
        'Чтобы получить помощь, нажмите /help.'
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Написать разработчику', url='t.me/pin4uck'
        )
    )
    bot.send_message(
        message.chat.id,
        '1) Чтобы получить список доступных волют, нажмите /exchange.\n' +
        '2) Нажмите на интересующую вас валюту.\n' +
        '3) Вы получите сообщение, содержащее информацию об курсе валюты, установленным Национальным банком РБ.\n',
        reply_markup=keyboard
    )


@bot.message_handler(commands=['exchange'])
def exchange_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
            telebot.types.InlineKeyboardButton('USD', callback_data='get-USD')
    )
    keyboard.row(
            telebot.types.InlineKeyboardButton('EUR', callback_data='get-EUR'),
            telebot.types.InlineKeyboardButton('RUB', callback_data='get-RUB')
    )
    bot.send_message(
            message.chat.id,
            'Нажмите на необходимую валюту:',
            reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        get_ex_callback(query)


def get_ex_callback(query):
    bot.answer_callback_query(query.id)
    send_exchange_result(query.message, query.data[4:])


def send_exchange_result(message, ex_code):
    bot.send_chat_action(message.chat.id, 'typing')
    ex = currency_try_except.inquiry(ex_code)
    bot.send_message(
        message.chat.id, serialize_ex(ex, ex_code),
        parse_mode='HTML'
    )


def serialize_ex(ex_json, ex_code):
    result = '<b>' + ex_code + ' -> ' + 'BYN' + ':</b>\n\n' + \
             'Rate: ' + str(ex_json)
    return result


@bot.message_handler(content_types=['text'])
def sent_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'До встречи, создатель')
    elif message.text.lower() == 'я тебя люблю':
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAM0YDaQ24SzhzkWTzYu8pVRCblOTrgAAgEAA8A2TxMYLnMwqz8tUR4E')


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


bot.polling(none_stop=True)
