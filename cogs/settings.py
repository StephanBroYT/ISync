import json
import disnake
from disnake.ext import commands
from config import OWNERS

SETTINGS_FILE = 'role_settings.json'

def save_settings(settings, filename=SETTINGS_FILE):
    """Сохранение настроек в файл."""
    with open(filename, 'w') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def load_settings(filename=SETTINGS_FILE):
    """Загрузка настроек из файла."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class SettingsView(disnake.ui.View):
    """Пользовательский интерфейс для отображения кнопок настроек."""

    def __init__(self, sync_nicknames, sync_roles):
        super().__init__(timeout=None)
        self.sync_nicknames = sync_nicknames
        self.sync_roles = sync_roles
        self.add_buttons()

    def add_buttons(self):
        """Добавление кнопок настроек."""
        self.clear_items()
        sync_nick_button = disnake.ui.Button(
            label="Синхронизировать ники",
            style=disnake.ButtonStyle.green if self.sync_nicknames else disnake.ButtonStyle.gray,
            custom_id="toggle_sync_nicknames"
        )
        sync_role_button = disnake.ui.Button(
            label="Синхронизировать роли",
            style=disnake.ButtonStyle.green if self.sync_roles else disnake.ButtonStyle.gray,
            custom_id="toggle_sync_roles"
        )
        self.add_item(sync_nick_button)
        self.add_item(sync_role_button)

class Settings(commands.Cog):
    """Класс для работы с настройками."""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Показать текущие настройки ролей")
    async def settings(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.author.guild_permissions.administrator and inter.author.id not in OWNERS:
            await inter.response.send_message(embed=disnake.Embed(
                  colour=disnake.Color.red(),
                description="У вас нет прав",
            ), ephemeral=True)
            return
        
        """Отображение текущих настроек ролей."""
        guild_id = str(inter.guild.id)
        settings = load_settings()

        if guild_id not in settings:
            settings[guild_id] = {
                "sync_nicknames": False,
                "sync_roles": False,
            }
            save_settings(settings)

        sync_nicknames = settings[guild_id].get("sync_nicknames", False)
        sync_roles = settings[guild_id].get("sync_roles", False)

        # Собираем информацию о ролях
        roles = {k: v for k, v in settings[guild_id].items() if k not in ["sync_nicknames", "sync_roles"]}
        role_info = "\n".join([f"*{badge}*: {inter.guild.get_role(role_id).mention}" for badge, role_id in roles.items() if inter.guild.get_role(role_id)])

        # Определяем статус синхронизации
        sync_status_nick = "Включено" if sync_nicknames else "Отключено"
        sync_status_role = "Включено" if sync_roles else "Отключено"

        settings_message = f"""

        **Настроенные роли на данный момент:**
        {role_info}

        Синхронизация ников: {sync_status_nick}
        Синхронизация ролей: {sync_status_role}
        """

        await inter.response.send_message(
            embed=disnake.Embed(
                title="Настройки",
                description=settings_message,
                colour=disnake.Color.blue()
            ),
            view=SettingsView(sync_nicknames, sync_roles)
        )

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        """Обработка нажатия кнопок настроек."""
        guild_id = str(inter.guild.id)
        settings = load_settings()

        if guild_id not in settings:
            settings[guild_id] = {
                "sync_nicknames": False,
                "sync_roles": False,
            }

        # Проверка и инициализация ключей "sync_nicknames" и "sync_roles"
        if "sync_nicknames" not in settings[guild_id]:
            settings[guild_id]["sync_nicknames"] = False
        if "sync_roles" not in settings[guild_id]:
            settings[guild_id]["sync_roles"] = False

        data = inter.data
        if data['custom_id'] == "toggle_sync_nicknames":
            settings[guild_id]["sync_nicknames"] = not settings[guild_id]["sync_nicknames"]
        elif data['custom_id'] == "toggle_sync_roles":
            settings[guild_id]["sync_roles"] = not settings[guild_id]["sync_roles"]

        save_settings(settings)
        sync_nicknames = settings[guild_id]["sync_nicknames"]
        sync_roles = settings[guild_id]["sync_roles"]

        # Обновляем сообщение с настройками
        roles = {k: v for k, v in settings[guild_id].items() if k not in ["sync_nicknames", "sync_roles"]}
        role_info = "\n".join([f"*{badge}*: {inter.guild.get_role(role_id).mention}" for badge, role_id in roles.items() if inter.guild.get_role(role_id)])
        sync_status_nick = "Включено" if sync_nicknames else "Отключено"
        sync_status_role = "Включено" if sync_roles else "Отключено"

        settings_message = f"""

        **Настроенные роли на данный момент:**
        {role_info}

        Синхронизация ников: {sync_status_nick}
        Синхронизация ролей: {sync_status_role}
        """

        await inter.response.edit_message(
            embed=disnake.Embed(
                title="Настройки",
                description=settings_message,
                colour=disnake.Color.blue()
            ),
            view=SettingsView(sync_nicknames, sync_roles)
        )

def setup(bot):
    bot.add_cog(Settings(bot))
