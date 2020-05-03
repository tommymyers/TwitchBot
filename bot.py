import logging
import re
import shlex
from websocket import WebSocketApp


class BotApp:

    def send(self, message):
        self.ws.send(f'PRIVMSG #{self.channel} :{message}')

    def process_command(self, msg, sender):
        msg = msg[1:-1].strip()
        command_name = msg.split(' ')[0].lower()
        if command_name in self.commands:
            command = self.commands[command_name]
            if len(msg) > len(command_name):
                full_args_string = msg[len(command_name)+1:]
                args = shlex.split(full_args_string)
                command(sender, *args)
            else:
                command(sender, None)

    def process_message(self, ws: WebSocketApp, msg: str):
        if msg.startswith('@'):
            tags_string = msg[msg.index('@')+1 : msg.index(' ')]
            tags = {k: v for (k, v) in [item.split('=') for item in tags_string.split(';')]}
            user_display_name = tags['display-name']
            regex = r':.*!.*@.*tmi\.twitch\.tv (PRIVMSG) #(.*) :(.*)'
            msg = msg[msg.index(' ') + 1:]
            match = re.match(regex, msg)
            if match:
                msg_type = match.group(1)
                channel = match.group(2)
                chat_message = match.group(3)
                self.logger.info(f'{user_display_name} said: {chat_message}')
                if chat_message.startswith('!'):
                    self.process_command(chat_message, user_display_name)

    def command(self, name):
        def wrapper(func):
            if name.lower() in self.commands:
                raise ValueError('Command already exists')
            self.commands[name] = func
            self.logger.info(f'Registered command {name}')
            return func
        return wrapper

    def on_error(self, ws: WebSocketApp, error):
        self.logger.error(f'WebSocket Error: {error}')

    def on_close(self, ws: WebSocketApp):
        self.logger.info('WebSocket disconnected')

    def on_open(self, ws: WebSocketApp):
        self.logger.info('WebSocket connected')
        ws.send(f'PASS {self.oauth_token}')
        ws.send(f'NICK {self.nick}')
        ws.send(f'JOIN #{self.channel}')
        ws.send(f'CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership')
        self._callback(self.post_login)

    def __init__(self, oauth_token, channel, nick, logger=None, post_login=None):
        self.commands = {}
        self.oauth_token = oauth_token
        self.channel = channel
        self.nick = nick
        self.logger = logger
        self.post_login = post_login
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        ws = WebSocketApp('wss://irc-ws.chat.twitch.tv:443')

        def on_open(sock):
            self.on_open(sock)
        ws.on_open = on_open

        def on_message(sock, msg):
            self.process_message(sock, msg)
        ws.on_message = on_message
        self.ws = ws

    def start(self):
        self.ws.run_forever()

    def _callback(self, func, *args):
        if func is not None:
            func(*args)