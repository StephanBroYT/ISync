import json
import disnake
import requests
from disnake.ext import commands
from disnake import Embed
from config import OWNERS

API_URL = 'https://api.inless.ru/player/'
SETTINGS_FILE = 'role_settings.json'

badge_value = {
    'vicep': 'Администратор',
    'banker': 'Банкир',
    'president': 'Президент',
    'judge': 'Судья',
    'preministr': 'Премьер министр',
    'builder': 'Министерство Инфраструктуры',
    'moderator': 'Модератор',
    'helper': 'Хелпер',
    'mvd': 'МВД',
    'police': 'Гвардия',
    'mineco': 'Министерство экономики',
    'culture': 'Министерство культуры'
}

def load_settings(filename=SETTINGS_FILE):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(description="Синхронизировать роли и никнеймы для пользователей на сервере")
    async def sync(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.author.guild_permissions.administrator and inter.author.id not in OWNERS:
            await inter.response.send_message(embed=disnake.Embed(
                colour=disnake.Color.red(),
                description="У вас нет прав",
            ), ephemeral=True)
            return

        await inter.response.defer()

        settings = load_settings()
        guild_id = str(inter.guild.id)

        if guild_id not in settings or not settings[guild_id]:
            await inter.followup.send(
                f'Нет настроек для синхронизации ролей на сервере {inter.guild.name}. Используйте команду /set-role или /set-default-role для настройки.'
            )
            return

        sync_nicknames = settings[guild_id].get("sync_nicknames", False)
        sync_roles = settings[guild_id].get("sync_roles", False)

        if not sync_nicknames and not sync_roles:
            await inter.followup.send(embed=disnake.Embed(
                colour=disnake.Color.orange(),
                title='Синхронизация отключена.',
                description='Включите синхронизацию ников или ролей в настройках.'
            ))
            return

        # members_updated = []
        nicknames_updated = []
        roles_added = []
        roles_removed = []
        errors = []

        default_role_id = settings[guild_id].get('Игрок')
        default_role = inter.guild.get_role(default_role_id) if default_role_id else None

        for member in inter.guild.members:
            if member.bot:
                continue  # Пропускаем ботов включая самого бота

            user_id = f"@{member.id}"
            api_request_url = f"{API_URL}{user_id}"

            try:
                response = requests.get(api_request_url, timeout=10)
                response.raise_for_status()

                try:
                    user_data = response.json()
                except json.JSONDecodeError:
                    user_data = response.text  

            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    print(f'Информация не найдена у пользователя {member.name}: {e}')
                    errors.append(member.name)
                else:
                    print(f'Пользователь {member.name}: {e}')
                    errors.append(member.name)
                continue
            except requests.exceptions.RequestException as e:
                print(f'Пользователь {member.name}: {e}')
                errors.append(member.name)
                continue

            if not user_data or 'Неправильный игрок' in user_data or 'Неправильный дискорд' in user_data:
                errors.append(member.name)
                continue

            # print(f"Информация о {member.name}: {user_data}")

            # Синхронизация никнеймов
            if sync_nicknames:
                nickname = user_data.get('nickname')
                if nickname and member.nick != nickname:
                    if inter.guild.me.guild_permissions.manage_nicknames:
                        try:
                            await member.edit(nick=nickname)
                            nicknames_updated.append((member.name, nickname))
                        except disnake.Forbidden:
                            print(f"Не удалось изменить ник {member.name} у бота отсутсвуют права.")
                    else:
                        print(f"У бота отсутствуют права на сервере: {inter.guild.name}.")

            # Синхронизация ролей
            if sync_roles:
                banned = user_data.get('banned', 'false').lower() == 'true'
                has_prime = user_data.get('has_prime', 'false').lower() == 'true'
                badges = user_data.get('badges', "") if isinstance(user_data, dict) else ""
                if isinstance(badges, str):
                    badges = badges.split(",") if badges else []

                badges = [badge.strip() for badge in badges]
                # print(badges)
                #TEST-------------
                badges_rename = [badge_value.get(badge, badge) for badge in badges]
                # for i in range(len(badges)):
                #     if badges[i] == 'vicep':
                #         badges[i] = 'Администратор'
                #     if badges[i] == 'banker':
                #         badges[i] = 'Банкир'
                #     if badges[i] == 'president':
                #         badges[i] = 'Президент'
                #     if badges[i] == 'judge':
                #         badges[i] = 'Судья'
                #     if badges[i] == 'preministr':
                #         badges[i] = 'Премьер министр'
                #     if badges[i] == 'builder':
                #         badges[i] = 'Министерство Инфраструктуры'
                        
                #     if badges[i] == 'moderator':
                #         badges[i] = 'Модератор'
                #     if badges[i] == 'helper':
                #         badges[i] = 'Хелпер'
                #     if badges[i] == 'mvd':
                #         badges[i] = 'МВД'
                #     if badges[i] == 'police':
                #         badges[i] = 'Гвардия'
                #     if badges[i] == 'mineco':
                #         badges[i] = 'Министерство экономики'
                #     if badges[i] == 'culture':
                #         badges[i] = 'Министерство культуры'
                
                # Удаляем все вхождения 'sub+'
                badges_rename = [item for item in badges_rename if item != 'sub+']
                # print(badges)
                #--------------------------------------------------------
                # if banned: Значение banned нету в апи (сервер инцест говно)
                #     badges_rename.append("Забанен")

                if banned:
                    badges_rename.append("Забанен")
                if has_prime:
                    badges_rename.append("Прайм")

                valid_roles = set()
                roles_to_assign = set()

                for api_badge, role_id in settings[guild_id].items():
                    if api_badge in ["sync_nicknames", "sync_roles"]:
                        continue  # Пропускаем настройки синхронизации

                    role = inter.guild.get_role(role_id)
                    if role:
                        valid_roles.add(role)
                        if api_badge == 'default' or api_badge in badges_rename:
                            roles_to_assign.add(role)

                # Добавление недостающих ролей
                for role in roles_to_assign:
                    if role not in member.roles:
                        try:
                            await member.add_roles(role)
                            roles_added.append((member.name, role.name))
                        except disnake.Forbidden:
                            print(f"Не удалось выдать роль {role.name} пользователю {member.name} у бота отсутствуют права.")
                        except Exception as e:
                            print(f"Не удалось выдать роль {role.name} пользователю {member.name}: {e}")

                # Удаление лишних ролей которые настроены и отсутствуют в roles_to_assign
                for role in member.roles:
                    if role not in roles_to_assign and role in valid_roles:
                        try:
                            await member.remove_roles(role)
                            roles_removed.append((member.name, role.name))
                        except disnake.Forbidden:
                            print(f"Не удалось убрать роль {role.name} с пользователя {member.name} у бота отсутсвуют права.")
                        except Exception as e:
                            print(f"Не удалось убрать роль {role.name} с пользователя {member.name}: {e}")

                # Выдача роли "Игрок" если она настроена и если пользователь есть в API
                if default_role and default_role not in member.roles:
                    try:
                        await member.add_roles(default_role)
                        roles_added.append((member.name, default_role.name))
                    except disnake.Forbidden:
                        print(f"Не удалось выдать роль игрока пользователю {member.name} у бота отсутсвуют права.")
                    except Exception as e:
                        print(f"Не удалось выдать роль игрока пользователю {member.name}: {e}")

        # Отправка сообщения (результат синхронизации)
        response_message = ""
        embed_color = disnake.Color.green()

        if nicknames_updated:
            updated_nicknames = ', '.join([f"{name} -> {nickname}" for name, nickname in nicknames_updated])
            response_message += f'* Никнеймы успешно синхронизированы: {updated_nicknames}.\n'

        if roles_added:
            added_roles = ', '.join([f"{name} ({role})" for name, role in roles_added])
            response_message += f'* Роли успешно добавлены пользователям: {added_roles}.\n'

        if roles_removed:
            removed_roles = ', '.join([f"{name} ({role})" for name, role in roles_removed])
            response_message += f'* Лишние роли удалены у пользователей: {removed_roles}.\n'

        if errors:
            error_users = ', '.join(errors)
            response_message += f'* Возникли проблемы с синхронизацией пользователей: {error_users}.\n'
            embed_color = disnake.Color.orange()

        if not response_message:
            response_message = '* Ни один пользователь не имеет соответствующих данных в API.'
            embed_color = disnake.Color.red()

        embed = Embed(
            title="Результат синхронизации",
            description=response_message,
            color=embed_color
        )

        await inter.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        """Крч говоря тут настройки"""

        settings = load_settings()
        guild_id = str(member.guild.id)

        sync_nicknames = settings[guild_id].get("sync_nicknames", False)
        sync_roles = settings[guild_id].get("sync_roles", False) 

        default_role_id = settings[guild_id].get('Игрок')
        default_role = member.guild.get_role(default_role_id) if default_role_id else None

        user_id = f"@{member.id}"
        api_request_url = f"{API_URL}{user_id}"

        try:
            response = requests.get(api_request_url, timeout=10)
            response.raise_for_status()
            try:
                user_data = response.json()
            except json.JSONDecodeError:
                user_data = response.text  

        except requests.exceptions.RequestException as e:
            print(f'Пользователь {member.name}: {e}')
            return

        if guild_id not in settings or not settings[guild_id]: # Если отсутствуют настройки
            return

        if not sync_nicknames and not sync_roles: # Если отключена синхронизация
            return

        if not user_data or 'Неправильный игрок' in user_data or 'Неправильный дискорд' in user_data:
            return

        # Синхронизация ника
        if sync_nicknames:
            nickname = user_data.get('nickname')
            if nickname and member.nick != nickname:
                if member.guild.me.guild_permissions.manage_nicknames:
                    try:
                        await member.edit(nick=nickname)
                    except disnake.Forbidden:
                        print(f"Не удалось изменить ник {member.name} у бота отсутсвуют права.")
                else:
                    print(f"У бота отсутствуют права на сервере: {member.guild.name}.")
        # Синхронизация роли
        if sync_roles:
            banned = user_data.get('banned', 'false').lower() == 'true'
            has_prime = user_data.get('has_prime', 'false').lower() == 'true'
            badges = user_data.get('badges', "") if isinstance(user_data, dict) else ""
            if isinstance(badges, str):
                badges = badges.split(",") if badges else []

            badges = [badge.strip() for badge in badges]

            if banned:
                badges.append("Забанен")
            if has_prime:
                badges.append("Прайм")

            valid_roles = set()
            roles_to_assign = set()

            for api_badge, role_id in settings[guild_id].items():
                if api_badge in ["sync_nicknames", "sync_roles"]:
                    continue

                role = member.guild.get_role(role_id)
                if role:
                    valid_roles.add(role)
                    if api_badge == 'default' or api_badge in badges:
                        roles_to_assign.add(role)
        # Выдача недостоющих ролей
        for role in roles_to_assign:
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                except disnake.Forbidden:
                    print(f"Не удалось выдать роль {role.name} пользователю {member.name} у бота отсутствуют права.")
                except Exception as e:
                    print(f"Не удалось выдать роль {role.name} пользователю {member.name}: {e}")
        
        # Выдача роли игрок
        
        if default_role and default_role not in member.roles:
            try:
                await member.add_roles(default_role)
            except disnake.Forbidden:
                print(f"Не удалось выдать роль игрока пользователю {member.name} у бота отсутсвуют права.")
            except Exception as e:
                print(f"Не удалось выдать роль игрока пользователю {member.name}: {e}")


def setup(bot):
    bot.add_cog(Sync(bot))
