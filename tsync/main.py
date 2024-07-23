import config

bot = config.bot

@bot.event
async def on_ready():
    print(f'Бот активирован {bot.user.name} ({bot.user.id})')
    print('  ')
    print('  ')

bot.load_extension('cogs.sync')
bot.load_extension('cogs.set-role')
bot.load_extension('cogs.set-default-role')
bot.load_extension('cogs.settings')

# Bot creator's -> @Genes1us, @StephanBro_YT

bot.run(config.TOKEN)


# ----
# import requests
# import json
# API_URL = 'http://api.burnhouse.online:20177/api/playerdata?trg='
# SETTINGS_FILE = 'role_settings.json'
# ----
# ЕЩКЕРЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕ
#  (токен бота)
# это как заметка просто
