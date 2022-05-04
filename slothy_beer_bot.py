import telebot
from datetime import time
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
Hi! I'm a bot that lets you know if any of the chat users want to go for a beer!
To do this, text me the command /beer and I will show you which of the users want to go drink beer.
You can also indicate whether you would or not like to go drinking beer.
Learn the bot commands with /help and start using it!
"""

# Message for '/help' command response
HELP_MESSAGE = """
Available commands:
/start - Start using the bot
/help - List of available commands
/beer - Display whether or not users want to drink beer today
/ready_for_beer - Set your desire to go and drink beer
/sloth_today - Set your refusal to go and drink beer
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
        output = 'Willingness of users to go drink beer: \n\n'
        for user in cls.get_instances():
            if user.get_beer_status():
                output += f'User {user.username} - is READY to go drink beer today \n'
            else:
                output += f'User {user.username} - is NOT ready to go drink beer today \n'

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
        BOT.send_message(message.chat.id, 'You do not have access to the bot')


# Function for stopping bot
@BOT.message_handler(commands=['bot_stop'])
def interupt_command(message):
    if message.from_user.id == ALLOWED_USERS[0]:
        BOT.send_message(message.chat.id, f'The bot is stopped by the user {message.from_user.username}')
        BOT.stop_polling()
    else:
        BOT.send_message(message.chat.id, f'Only user {message.from_user.username} can stop the bot')


# Function for unknown commands
def unknown_command(message):
    BOT.send_message(
        message.chat.id, 'Unfortunately, I only know how to deal with these commands": ')
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
            message.chat.id, f'User {message.from_user.username} confirmed his willingness to go drink beer')


# Function for /sloth_today command
def sloth_command(message, current_user):
    current_user.set_beer_status(False)

    if STATUS_RESPONSE:
        BOT.send_message(
            message.chat.id, f'User {message.from_user.username} refuses to go drink beer')



# Function for starting bot
def main():
    BOT.infinity_polling(timeout=30, long_polling_timeout = 5)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            with open('./logs/log.txt', 'a') as f:
                f.write(f'{e}\n')
            time.sleep(10)
