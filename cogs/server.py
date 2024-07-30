import json
import disnake
import requests
from disnake.ext import commands
from disnake import Embed
from config import OWNERS

API_URL = 'https://api.inless.ru/server'





class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.slash_command(description="Информация о сервере")
    async def server(self, inter: disnake.ApplicationCommandInteraction):
        
        api_request_url = f"{API_URL}"
        try:
            response = requests.get(api_request_url, timeout=10)
            response.raise_for_status()
            try:
                user_data = response.json()
            except json.JSONDecodeError:
                user_data = response.text  
        except Exception as e:
            await inter.response.send_message(f"Ошибка {e}")
                
        online = user_data.get('online')
        tps = user_data.get('tps')
        online_players = user_data.get('online_players')


        await inter.response.send_message(embed=disnake.Embed(
            colour=disnake.Color.green(),
            title=f'Информация о сервере',
            description=f'Онлайн: {online}\n TPS: {tps}\n Игроки онлайн:\n{online_players}'
        ).set_thumbnail(url="https://i.imgur.com/fTbywuh.png"),ephemeral=True)

        
        
def setup(bot):
    bot.add_cog(Server(bot))
