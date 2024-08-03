import config

bot = config.bot

@bot.event
async def on_ready():
    bot.load_extension('cogs.sync')
    bot.load_extension('cogs.set-role')
    bot.load_extension('cogs.set-default-role')
    bot.load_extension('cogs.settings')
    # bot.load_extension('cogs.profile')
    bot.load_extension('cogs.admin_tools')
    # bot.load_extension('cogs.server')
    print(f'Бот активирован {bot.user.name} ({bot.user.id})')
    print('  ')
    print('  ')



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
