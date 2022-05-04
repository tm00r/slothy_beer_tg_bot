import telebot
from dotenv import dotenv_values

# Load .env file
ENV = dotenv_values('.env')

# Bot instance
BOT = telebot.TeleBot(ENV.get('TELEGRAM_BOT_API'))

# List of allowed user's Telegram IDs
ALLOWED_USERS = list(map(int, ENV.get('ALLOWED_USERS').split(',')))

# Response on status change
STATUS_RESPONSE = False

# Delete command messages
DELETE_COMMAND_LINES = True

# Message for '/start' command response
START_MESSAGE = """
Привет! Я бот, который позволяет узнать желает ли кто-то из пользователей чата пойти выпить пивас!
Для этого напиши мне команду /beer и я покажу, кто из пользователей желает пойти пить пивас.
Также, ты можешь выразить свое желание или НЕжелание пойти пить пивас другим пользователям.
Изучи команды бота с помощью /help и начни им пользоваться!
"""

# Message for '/help' command response
HELP_MESSAGE = """
Доступные команды:
/start - Начало работы с ботом
/help - Список доступных команд
/beer - Показать желание или НЕжелание пользователей идти пить пивас
/ready_for_beer - Выразить свое желание пойти выпить пивас
/sloth_today - Выразить свое НЕжелание пойти выпить пивас
"""

# List of commands allowed for users
COMMAND_LIST = [
    'help',
    'help@beer_status_bot',
    'start',
    'start@beer_status_bot',
    'ready_for_beer',
    'ready_for_beer@beer_status_bot',
    'sloth_today',
    'sloth_today@beer_status_bot',
    'beer',
    'beer@beer_status_bot'
]


# Class for caching user's Telegram ID
class CachedInstance(type):
    _instances = {}

    def __call__(cls, *args):
        index = cls, args
        if index not in cls._instances:
            cls._instances[index] = super(CachedInstance, cls).__call__(*args)
        return cls._instances[index]


# User class
class User(metaclass=CachedInstance):

    instances = []

    def __init__(self, id, username):
        self.id = id
        self.username = username
        self.beer_status = False
        self.instances.append(self)

    def set_beer_status(self, status):
        self.beer_status = status

    def get_beer_status(self):
        return self.beer_status

    @classmethod
    def get_instances(cls):
        return cls.instances

    @classmethod
    def users_beer_status(cls):
        output = 'Готовность пользователей идти пить пивас: \n\n'
        for user in cls.get_instances():
            if user.get_beer_status():
                output += f'Пользователь {user.username} - ГОТОВ идти пить пивас \n'
            else:
                output += f'Пользователь {user.username} - НЕ готов идти пить пивас \n'

        return output


# Handler for commands from COMMAND_LIST
@BOT.message_handler(commands=COMMAND_LIST)
def executecomands(message):

    if message.from_user.id in ALLOWED_USERS:

        current_user = User(message.from_user.id, message.from_user.username)

        match message.text.split('@')[0]:

            case '/start':
                start_command(message)

            case '/help':
                help_command(message)

            case '/ready_for_beer':
                beer_command(message, current_user)

            case '/sloth_today':
                sloth_command(message, current_user)

            case '/beer':
                BOT.send_message(message.chat.id, User.users_beer_status())

        if DELETE_COMMAND_LINES:
            BOT.delete_message(message.chat.id, message.message_id, timeout=1)

    else:
        BOT.send_message(message.chat.id, 'Вы не имеете доступа к боту')


# Function for stopping bot
@BOT.message_handler(commands=['bot_stop'])
def interupt_command(message):
    if message.from_user.id == ALLOWED_USERS[0]:
        BOT.send_message(message.chat.id, f'Бот остановлен пользователем {message.from_user.username}')
        BOT.stop_polling()
    else:
        BOT.send_message(message.chat.id, f'Только {message.from_user.username} может остановить бота')


# Function for unknown commands
def unknown_command(message):
    BOT.send_message(
        message.chat.id, 'К сожалению или к счастью, я умею работать только с этими командами: ')
    help_command(message)


# Function for /start command
def start_command(message):
    BOT.send_message(message.chat.id, START_MESSAGE)


# Function for /help command
def help_command(message):
    BOT.send_message(message.chat.id, HELP_MESSAGE)


# Function for /ready_for_beer command
def beer_command(message, current_user):
    current_user.set_beer_status(True)

    if STATUS_RESPONSE:
        BOT.send_message(
            message.chat.id, f'Пользователь {message.from_user.username} подтвердил свое ЖЕЛАНИЕ пойти пить пивас')


# Function for /sloth_today command
def sloth_command(message, current_user):
    current_user.set_beer_status(False)

    if STATUS_RESPONSE:
        BOT.send_message(
            message.chat.id, f'Пользователь {message.from_user.username} выразил НЕжелание идти пить пивас')



# Function for starting bot
def main():
    BOT.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
