from disnake import Role
from disnake.ext import commands
import disnake
import json
from config import OWNERS

SETTINGS_FILE = 'role_settings.json'

def save_settings(settings, filename=SETTINGS_FILE):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def load_settings(filename=SETTINGS_FILE):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class SetRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Установить роль для пользователей с определенным badge из API")
    async def set_role(
        self,
        inter: disnake.ApplicationCommandInteraction,
        api_badge: str = commands.Param(
            description="Выберите должность на которую вы хотите настроить роль.",
            name="классификация",
            choices=["Президент",
                     "Судья",
                     "Банкир",
                     "Прайм",
                     'Администратор',
                     'Премьер министр',
                     'Министерство Инфраструктуры',
                     "Модератор",
                     "Хелпер",
                     'МВД',
                     'Министерство экономики',
                     'Гвардия',
                     'Министерство культуры'] #choices=["prime"] 
        ),
        discord_role: disnake.Role = commands.Param(
            name="роль",
            description="Выберите роль на которую вы хотите настроить должность."),
    ):
        if not inter.author.guild_permissions.administrator and inter.author.id not in OWNERS:
            await inter.response.send_message(embed=disnake.Embed(
                colour=disnake.Color.red(),
                description="У вас нет прав",
            ), ephemeral=True)
            return

        settings = load_settings()
        guild_id = str(inter.guild.id)

        if guild_id not in settings:
            settings[guild_id] = {}

        settings[guild_id][api_badge.strip()] = discord_role.id
        save_settings(settings)

        await inter.response.send_message(embed=disnake.Embed(
            colour=disnake.Color.green(),
            title='Роль назначена',
            description=f'Роль {discord_role.mention} отныне будет выдаваться пользователям классификации: {api_badge}'
        ))

def setup(bot):
    bot.add_cog(SetRole(bot))
