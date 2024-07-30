from disnake.ext import commands
import disnake

intents = disnake.Intents.all()
intents.members = True

bot = commands.Bot(
    command_prefix='/',
    intents=intents,
    activity=disnake.Game('Синхронизирую пользователей'),
    status=disnake.Status.idle
    )

TOKEN = ''

OWNERS = [
    986355526948515870,
    986355526948515870
]
