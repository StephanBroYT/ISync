import config
import asyncio

from disnake.ext.commands import LargeInt
import disnake
from disnake.ext import commands




class AdminTools(commands.Cog):

    def __init__(self, bot: disnake.ext.commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.is_owner()
    @commands.slash_command(name="guild", guild_ids=[config.DevServers, config.DevServers])
    async def guild_placeholder(self, inter: disnake.ApplicationCommandInteraction):
        """
        Placeholder for /get
        """

    @commands.guild_only()
    @guild_placeholder.sub_command(name="list")
    async def get_guilds_command(self, inter: disnake.ApplicationCommandInteraction):
        """
        Выводит список всех серверов, где установлен бот
        """
        all_guilds_string = "Name - Members count - ID\n"
        for guild in self.bot.guilds:
            all_guilds_string += f"{guild.name} - {guild.member_count}  <@{guild.owner_id}> ({guild.id})\n"

        for stroke in [
            all_guilds_string[i: i + 2000]
            for i in range(0, len(all_guilds_string), 2000)
        ]:
            await inter.send(content=stroke, ephemeral=True)

    @commands.guild_only()
    @guild_placeholder.sub_command(name="get")
    async def get_guild_command(
            self, inter: disnake.ApplicationCommandInteraction, guild_id: LargeInt
    ):
        """
        Получить информацию о сервере
        """
        await inter.response.defer(ephemeral=True)
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await inter.edit_original_message(content="404 Not found")
            return

        guild_embed = disnake.Embed(title=guild.name, description=guild.description)
        guild_owner = guild.get_member(guild.owner_id)
        guild_embed.add_field(
            name="Owner", value=f"{guild_owner} {guild_owner.mention}", inline=False
        )
        guild_embed.add_field(
            name="Member count", value=guild.member_count, inline=False
        )
 

        await inter.edit_original_message(embed=guild_embed)

    @commands.guild_only()
    @guild_placeholder.sub_command(name="leave")
    async def leave_guild_command(
            self, inter: disnake.ApplicationCommandInteraction, guild_id: LargeInt
    ):
        """
        Выйти с сервера
        """
        print("Leaving ", guild_id)

        if guild_id in [config.DevServers]:
            await inter.send("Unable to leave dev guild")
        await inter.response.defer(ephemeral=True)
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await inter.edit_original_message(content="404 Not found")
            return

        await guild.leave()

        await inter.edit_original_message(
            embed=disnake.Embed(title=f"Left {guild}", description=repr(guild))
        )


def setup(client):
    client.add_cog(AdminTools(client))
    print("Loaded AdminTools")



