import json
import disnake
import requests
from disnake.ext import commands
from disnake import Embed
from config import OWNERS

API_URL = 'https://api.inless.ru/player/'
SETTINGS_FILE = 'role_settings.json'



class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.slash_command(description="Профиль игрока")
    async def profile(self, inter: disnake.ApplicationCommandInteraction, nickname):
        
        api_request_url = f"{API_URL}{nickname}"
        try:
            response = requests.get(api_request_url, timeout=10)
            response.raise_for_status()
            try:
                user_data = response.json()
            except json.JSONDecodeError:
                user_data = response.text  
        except Exception as e:
            await inter.response.send_message(f"Ошибка {e}")
                
        nickname = user_data.get('nickname')
        health = user_data.get('health')
        total_time = user_data.get('total_time')
        has_prime = user_data.get('has_prime')
        uuid = user_data.get('uuid')
        discord_id = user_data.get('discord_id')

        if has_prime == True:
            has_prime = "Да"
        else:
            has_prime = "Нет"
        await inter.response.send_message(embed=disnake.Embed(
            colour=disnake.Color.green(),
            title=nickname,
            description=f'Никнейм: {nickname}\n Здоровье: {health}\n Время в игре: {total_time}\n Есть ли прайм?: {has_prime}\n UUID: {uuid}\n Discord ID: {discord_id}'
        ).set_thumbnail(url=f"https://vzge.me/bust/256/{nickname}"), ephemeral=True)

        
        
def setup(bot):
    bot.add_cog(Profile(bot))
