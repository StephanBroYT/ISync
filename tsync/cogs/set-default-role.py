from disnake.ext import commands
import disnake
import json
from config import OWNERS

SETTINGS_FILE = 'role_settings.json'

def save_settings(settings, filename=SETTINGS_FILE):
    with open(filename, 'w') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def load_settings(filename=SETTINGS_FILE):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

class SetDefaultRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Установить роль для всех пользователей, присутствующих на сервере (игрок)")
    async def set_default_role(
        self, 
        inter: disnake.ApplicationCommandInteraction, 
        discord_role: disnake.Role = commands.Param(
            name="роль",
            description="Выберите роль которая будет по умолчанию у игрока"
        )
    ):
        if not inter.author.guild_permissions.administrator and inter.author.id not in OWNERS:
            await inter.response.send_message(
                embed=disnake.Embed(
                    colour=disnake.Color.red(),
                    description="У вас нет прав",
                ),
                ephemeral=True
            )
            return

        settings = load_settings()
        guild_id = str(inter.guild.id)

        if guild_id not in settings:
            settings[guild_id] = {}

        settings[guild_id]['Игрок'] = discord_role.id
        save_settings(settings)

        await inter.response.send_message(
            embed=disnake.Embed(
                colour=disnake.Color.green(),
                title=f'Роль назначена', 
                description=f'Роль {discord_role.mention} по умолчанию теперь стоит как на роль игрока.'
            )
        )

def setup(bot):
    bot.add_cog(SetDefaultRole(bot))