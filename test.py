from bot import BotApp
import util


config = util.load_config('config.json')
logger = util.setup_logger(config['log_file'])
bot = BotApp(oauth_token=config['auth_token'],
             channel=config['join_channel'],
             nick=config['nick'])

boops = 0


@bot.command(name='test')
def test(sender, *args):
    bot.send(f'Hello, @{sender}')


@bot.command(name='addboop')
def add_boop(sender, *args):
    bot.send(f'Incremented boop count')
    global boops
    boops += 1


@bot.command(name='boops')
def print_boops(sender, *args):
    bot.send(f'Total boops: {boops}')


def post_login():
    bot.send('/me has arrived!')


logger.info('Starting bot')
bot.post_login = post_login
bot.start()
