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

TOKEN = 'MTI0NDU3ODY3MjU5MDA2NTcxNA.GH4xN9.h7kTnNW92juxM_amJOpN0VuOC6gIiB-IRZxhiw'

OWNERS = [
    986355526948515870,
    986355526948515870
]