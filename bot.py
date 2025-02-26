import disnake
from disnake.ext import commands
from disnake import Option
import os, sqlite3
import atexit
import json
from tabulate import tabulate #удобный модуль для рисования таблиц
import json #используется только для обработки инвентаря, но ему можно найти и другое применение
import random
conn = sqlite3.connect("Discord.db") # или :memory:
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS shop (
    id INTEGER PRIMARY KEY,
    type TEXT,
    name TEXT,
    cost INTEGER
)
''')

# Создание таблицы users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    nickname TEXT,
    mention TEXT,
    money INTEGER,
    rep_rank TEXT,
    inventory TEXT,
    lvl INTEGER,
    xp INTEGER
)
''')

intents = disnake.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    print("Bot Has been runned")#сообщение о готовности
    for guild in bot.guilds:#т.к. бот для одного сервера, то и цикл выводит один сервер
        print(guild.id)#вывод id сервера
        serv=guild#без понятия зачем это
        for member in guild.members:#цикл, обрабатывающий список участников
            cursor.execute(f"SELECT id FROM users where id={member.id}")#проверка, существует ли участник в БД
            if cursor.fetchone()==None:#Если не существует
                cursor.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 50000, 'S','[]',0,0)")#вводит все данные об участнике в БД
            else:#если существует
                pass
            conn.commit()#применение изменений в БД


@bot.event
async def on_member_join(member):
    cursor.execute(f"SELECT id FROM users where id={member.id}")#все также, существует ли участник в БД
    if cursor.fetchone()==None:#Если не существует
        cursor.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 50000, 'S','[]',0,0)")#вводит все данные об участнике в БД
    else:#Если существует
        pass
    conn.commit()#применение изменений в БД

@bot.event
async def on_message(message):
    if len(message.content) > 10:#за каждое сообщение длиной > 10 символов...
        for row in cursor.execute(f"SELECT xp,lvl,money FROM users where id={message.author.id}"):
            expi=row[0]+random.randint(5, 40)#к опыту добавляется случайное число
            cursor.execute(f'UPDATE users SET xp={expi} where id={message.author.id}')
            lvch=expi/(row[1]*1000)
            print(int(lvch))
            lv=int(lvch)
            if row[1] < lv:#если текущий уровень меньше уровня, который был рассчитан формулой выше,...
                await message.channel.send(f'Новый уровень!')#то появляется уведомление...
                bal=1000*lv
                cursor.execute(f'UPDATE users SET lvl={lv},money={bal} where id={message.author.id}')#и участник получает деньги
    await bot.process_commands(message)#Далее это будет необходимо для ctx команд
    conn.commit()#применение изменений в БД



@bot.command()
async def ping(ctx):
    await ctx.reply(f'Понг! {round(bot.latency * 1000)} мс')

@bot.slash_command(name='giverole', description='Выдача роли пользователю')
async def give_role(interaction, member: disnake.Member, role: disnake.Role):
    await member.add_roles(role)
    await interaction.response.send_message('Роль выдана!')


@bot.slash_command(name='removerole', description='Забор роли у пользователя')
async def take_role(interaction, member: disnake.Member, role: disnake.Role):
    await member.remove_roles(role)
    await interaction.response.send_message('Роль убрана!')

@bot.slash_command(name='changenick', description='Изменяет никнейм пользователя')
async def set_nick(interaction, member: disnake.Member, nick: str):
    await member.edit(nick=nick)
    await interaction.response.send_message('Никнейм изменен!')

	

intents = disnake.Intents.default()
intents.members = True  # Не забудьте включить этот интент в вашем приложении Discord

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

MUTE_ROLE_NAME = "Заглушенный"
LOG_CHANNEL_ID = 1158183124648337473  # ID канала для логов
VOICE_CHANNEL_ID = 1245376471040655462
ROLE_ID = 1269621671636107345
DATA_FILE = 'user_data.json'
ALLOWED_USER_ID = 812358905421889546  # Замените на ваш Discord ID
color_roles = {
    "Aquamarine": 1342858191934984193,
    "Rainbow": 1342859043823161436,
    "Wine Red": 1342862328214978581,
    "Pale Green": 1342862553511891064,
    "Снять цвет": None
}


# Создаем экземпляр бота
intents = disnake.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)
intents = disnake.Intents.default()
intents.message_content = True  # Включаем намерение для работы с сообщениями
intents.members = True
# Функция для загрузки данных из JSON-файла
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # Возвращаем пустой словарь в случае ошибки

# Функция для сохранения данных в JSON-файл
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Команда /myinfo
@bot.slash_command(name="myinfo", description="Показать информацию о себе")
async def myinfo(ctx: disnake.ApplicationCommandInteraction):
    user_id = str(ctx.author.id)
    data = load_data()

    # Получаем информацию о пользователе или создаем новую запись, если ее нет
    if user_id not in data:
        data[user_id] = {"nickname": ctx.author.name, "money": 0, "lvl": 1, "xp": 0}
        save_data(data)  # Сохраняем новую запись

    user_info = data[user_id]
    emojiadm = '<:authoritybot:1340048069864984698>'  # Замените my_emoji на имя вашего эмодзи
    emojicoins = '<:babkiblyat:1342914669538578443>'
    emojilvl = '<:lvl:1342914640883224636>'
    emojixp = '<:exp:1342914432774438922>'
    # Создаем embed сообщение
    embed = disnake.Embed(title=f"{emojiadm} Статистика пользователя {ctx.author.name}", color=disnake.Color.light_gray())
    embed.add_field(name="💰 Баланс AS", value=f"`{user_info['money']:,} AS-коинов`", inline=True)  # Добавление эмодзи к полю
    embed.add_field(name="📈 Уровень", value=f"`{user_info['lvl']}`", inline=True)  # Эмодзи для уровня
    embed.add_field(name="⚡️ Опыт", value=f"`{user_info['xp']:,}`", inline=False)  # Эмодзи для опыта

    await ctx.send(embed=embed)


# Команда /givexp
@bot.slash_command(name="givexp", description="Выдать опыт пользователю")
async def givexp(ctx: disnake.ApplicationCommandInteraction, user: disnake.User, value: int):
    # Проверяем, что команду вызывает разрешенный пользователь
    if ctx.author.id != ALLOWED_USER_ID:
        await ctx.send("У вас нет прав на использование этой команды.")
        return

    # Проверяем, что значение опыта больше нуля
    if value <= 0:
        await ctx.send("Количество опыта должно быть положительным числом.")
        return

    data = load_data()
    user_id = str(user.id)

    # Если пользователя нет в данных, создаем новую запись
    if user_id not in data:
        data[user_id] = {"nickname": user.name, "money": 0, "lvl": 1, "xp": 0, "messages": 0}

    # Добавляем опыт пользователю
    data[user_id]["xp"] += value

    # Проверка на уровень (например, 100 XP для повышения уровня)
    while data[user_id]["xp"] >= 100:
        data[user_id]["lvl"] += 1
        data[user_id]["xp"] -= 100  # Сброс XP на следующий уровень

    # Сохраняем обновленные данные в файл
    save_data(data)

    # Создаем Embed сообщение для уведомления о выдаче опыта
    embed = disnake.Embed(title="Выдача опыта пользователю", color=disnake.Color.light_gray())
    embed.add_field(name="", value=f"Разработчик {ctx.author.mention} выдал {value} опыта пользователю {user.mention}", inline=False)

    await ctx.send(embed=embed)
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Игнорируем сообщения от ботов

    user_id = str(message.author.id)
    data = load_data()

    # Получаем информацию о пользователе или создаем новую запись, если ее нет
    if user_id not in data:
        data[user_id] = {"nickname": message.author.name, "money": 0, "lvl": 1, "xp": 0, "messages": 0}

    user_info = data[user_id]

    # Увеличиваем счетчик сообщений
    user_info["messages"] += 1

    # За каждое сообщение добавляем случайное количество XP (например, от 5 до 15)
    xp_gained = random.randint(5, 15)
    user_info["xp"] += xp_gained

    # Проверка на уровень (например, 100 XP для повышения уровня)
    if user_info["xp"] >= 100:
        user_info["lvl"] += 1
        user_info["xp"] -= 100  # Сброс XP на следующий уровень

    # Обновляем данные пользователя в словаре
    data[user_id] = user_info

    # Сохраняем обновленные данные в файл
    save_data(data)

    await bot.process_commands(message)  # Позволяет обрабатывать команды

# Обработчик событий на отправку сообщения
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Игнорируем сообщения от ботов

    user_id = str(message.author.id)
    data = load_data()

    # Получаем информацию о пользователе или создаем новую запись, если ее нет
    if user_id not in data:
        data[user_id] = {"nickname": message.author.name, "money": 0, "lvl": 1, "xp": 0}

    user_info = data[user_id]

    # За каждое сообщение добавляем случайное количество XP (например, от 5 до 15)
    xp_gained = random.randint(5, 15)
    user_info["xp"] += xp_gained

    # Проверка на уровень (например, 100 XP для повышения уровня)
    if user_info["xp"] >= 100:
        user_info["lvl"] += 1
        user_info["xp"] -= 100  # Сброс XP на следующий уровень

    # Обновляем данные пользователя в словаре
    data[user_id] = user_info

    # Сохраняем обновленные данные в файл
    save_data(data)


@bot.slash_command(name='vc', description='Управление доступом к подключению к подвалу.')
async def vc_command(ctx: disnake.ApplicationCommandInteraction, option: str):
    # Проверяем, что пользователь является администратором
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("У вас нет прав для выполнения этой команды.", ephemeral=True)
        return

    # Получаем голосовой канал по ID
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not isinstance(voice_channel, disnake.VoiceChannel):
        await ctx.send("Голосовой канал не найден.", ephemeral=True)
        return

    # Получаем роль по ID
    role = ctx.guild.get_role(ROLE_ID)
    if role is None:
        await ctx.send("Роль не найдена.", ephemeral=True)
        return

    if option == 'ОТКРЫТЫЙ':
        # Устанавливаем разрешения для роли, чтобы они могли подключаться
        await voice_channel.set_permissions(role, connect=True)
        await ctx.send("Подвал теперь открыт для подключения.")
    elif option == 'ЗАКРЫТЫЙ':
        # Устанавливаем разрешения для роли, чтобы они не могли подключаться
        await voice_channel.set_permissions(role, connect=False)
        await ctx.send("Подвал теперь закрыт для подключения.")
    else:
        await ctx.send("Выберите правильный вариант: 'ЗАКРЫТЫЙ' или 'ОТКРЫТЫЙ'.", ephemeral=True)

@vc_command.autocomplete('option')
async def vc_option_autocomplete(interaction: disnake.ApplicationCommandInteraction, current: str):
    options = ['ЗАКРЫТЫЙ', 'ОТКРЫТЫЙ']
    return [option for option in options if current.lower() in option.lower()]

   

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.event
async def on_member_update(before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        moderator = after.guild.me  # Получаем объект бота (модератора)
        # Проверка на изменения ролей
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]

        if added_roles:
            embed = disnake.Embed(title="Роль добавлена", color=disnake.Color.green())
            embed.add_field(name="Пользователь", value=after.mention, inline=False)
            embed.add_field(name="Добавленные роли", value=', '.join([role.name for role in added_roles]), inline=False)
            embed.add_field(name="Модератор", value=moderator.mention, inline=False)
            await log_channel.send(embed=embed)

        if removed_roles:
            embed = disnake.Embed(title="Роль удалена", color=disnake.Color.red())
            embed.add_field(name="Пользователь", value=after.mention, inline=False)
            embed.add_field(name="Удаленные роли", value=', '.join([role.name for role in removed_roles]), inline=False)
            embed.add_field(name="Модератор", value=moderator.mention, inline=False)
            await log_channel.send(embed=embed)

        # Проверка на изменения прав ролей
        if before.roles != after.roles:
            changed_roles = [role for role in after.roles if role not in before.roles or role.permissions != before.get_role(role.id).permissions]
            if changed_roles:
                embed = disnake.Embed(title="Изменены права ролей", color=disnake.Color.orange())
                embed.add_field(name="Пользователь", value=after.mention, inline=False)
                embed.add_field(name="Измененные роли", value=', '.join([role.name for role in changed_roles]), inline=False)
                embed.add_field(name="Модератор", value=moderator.mention, inline=False)
                await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_create(role):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        moderator = role.guild.me  # Получаем объект бота (модератора)
        embed = disnake.Embed(title="Роль создана", color=disnake.Color.green())
        embed.add_field(name="Роль", value=role.name, inline=False)
        embed.add_field(name="Модератор", value=moderator.mention, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        moderator = role.guild.me  # Получаем объект бота (модератора)
        embed = disnake.Embed(title="Роль удалена", color=disnake.Color.red())
        embed.add_field(name="Роль", value=role.name, inline=False)
        embed.add_field(name="Модератор", value=moderator.mention, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_update(before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        moderator = after.guild.me  # Получаем объект бота (модератора)

        if before.permissions != after.permissions:
            embed = disnake.Embed(title="Изменены права роли", color=disnake.Color.orange())
            embed.add_field(name="Роль", value=after.name, inline=False)
            embed.add_field(name="Старые права", value=str(before.permissions), inline=False)
            embed.add_field(name="Новые права", value=str(after.permissions), inline=False)
            embed.add_field(name="Модератор", value=moderator.mention, inline=False)
            await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        moderator = channel.guild.me  # Получаем объект бота (модератора)
        embed = disnake.Embed(title="Канал создан", color=disnake.Color.green())
        embed.add_field(name="Канал", value=channel.name, inline=False)
        embed.add_field(name="Тип канала", value=str(channel.type), inline=False)
        embed.add_field(name="Модератор", value=moderator.mention, inline=False)
        await log_channel.send(embed=embed)



@bot.event
async def on_message_delete(message):
    if message.author.bot:  # Игнорируем сообщения от ботов
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(title="Сообщение удалено", color=disnake.Color.light_gray())
        embed.add_field(name="Автор", value=message.author.mention, inline=False)
        embed.add_field(name="Содержимое", value=message.content or "Сообщение пустое", inline=False)
        embed.add_field(name="Канал", value=message.channel.mention, inline=False)
        embed.add_field(name="Дата удаления", value=disnake.utils.format_dt(disnake.utils.utcnow(), "F"), inline=False)

        await log_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:  # Игнорируем сообщения от ботов
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(title="Сообщение отредактировано", color=disnake.Color.light_gray())
        embed.add_field(name="Автор", value=before.author.mention, inline=False)
        embed.add_field(name="Старое содержимое", value=before.content or "Сообщение пустое", inline=False)
        embed.add_field(name="Новое содержимое", value=after.content or "Сообщение пустое", inline=False)
        embed.add_field(name="Канал", value=before.channel.mention, inline=False)
        embed.add_field(name="Дата редактирования", value=disnake.utils.format_dt(disnake.utils.utcnow(), "F"), inline=False)

        await log_channel.send(embed=embed)

async def log_action(action_type, member, reason, moderator, action_status):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(title="Наказание", color=disnake.Color.light_gray())
        embed.add_field(name="Тип наказания", value=f"{action_type} - {action_status}", inline=False)  # Обновлено поле
        embed.add_field(name="Дата наказания", value=disnake.utils.format_dt(disnake.utils.utcnow(), "F"), inline=False)
        embed.add_field(name="Ответственный модератор", value=moderator.mention, inline=False)
        embed.add_field(name="Пользователь", value=member.mention, inline=False)
        embed.add_field(name="Причина", value=reason if reason else 'Не указана', inline=False)

        await log_channel.send(embed=embed)

@bot.slash_command(name='listusers', description='Показать всех пользователей в базе данных')
async def list_users(interaction: disnake.ApplicationCommandInteraction):
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    if users:
        user_list = '\n'.join([f'ID: {user[0]}, Сообщения: {user[1]}, Время голоса: {user[2]}, Уровень: {user[3]}, Баланс: {user[4]}' for user in users])
        await interaction.send(f'Список пользователей:\n{user_list}')
    else:
        await interaction.send('Нет пользователей в базе данных.')


@bot.slash_command(description="Замучить пользователя")
@commands.has_permissions(manage_roles=True)
async def mute(interaction: disnake.ApplicationCommandInteraction, member: disnake.Member, duration: int, reason: str = None):
    mute_role = disnake.utils.get(interaction.guild.roles, name=MUTE_ROLE_NAME)
    
    if not mute_role:   
        await interaction.send(f"Роль '{MUTE_ROLE_NAME}' не найдена.")
        return

    await member.add_roles(mute_role, reason=reason)

    embed = disnake.Embed(title="Пользователь замучен", color=disnake.Color.light_grey())
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Длительность", value=f"{duration} минут(ы)", inline=True)
    embed.add_field(name="Причина", value=reason if reason else 'Не указана', inline=False)
    embed.add_field(name="Ответственный модератор", value=interaction.user.mention, inline=False)

    await interaction.send(embed=embed)

    # Ждем указанное время
    await asyncio.sleep(duration * 60)  # Переводим минуты в секунды

    # Удаляем роль "Muted"
    await member.remove_roles(mute_role)

    embed_unmute = disnake.Embed(title="Пользователь размучен", color=disnake.Color.light_grey())
    embed_unmute.add_field(name="Пользователь", value=member.mention, inline=True)
    embed_unmute.add_field(name="Ответственный модератор", value=interaction.user.mention, inline=False)

    await interaction.channel.send(embed=embed_unmute)
    await log_action("Unmute", member, reason, interaction.user, "Снято")

@bot.slash_command(description="Размучить пользователя")
@commands.has_permissions(manage_roles=True)
async def unmute(interaction: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = None):
    mute_role = disnake.utils.get(interaction.guild.roles, name=MUTE_ROLE_NAME)

    if not mute_role:
        await interaction.send(f"Роль '{MUTE_ROLE_NAME}' не найдена.")
        return

    await member.remove_roles(mute_role, reason=reason)

    embed = disnake.Embed(title="Пользователь размучен", color=disnake.Color.light_grey())
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Причина", value=reason if reason else 'Не указана', inline=False)
    embed.add_field(name="Ответственный модератор", value=interaction.user.mention, inline=False)

    await interaction.send(embed=embed)
    await log_action("Unmute", member, reason, interaction.user)

@bot.slash_command(name='warning', description="Выдать устное предупреждение пользователю")
@commands.has_permissions(manage_roles=True)
async def warning(interaction: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = None):
    embed = disnake.Embed(title="**Устное предупреждение**", color=disnake.Color.light_gray())
    embed.add_field(name="Сообщение", value=f"Вы получили устное предупреждение от модератора {interaction.user.mention}, пожалуйста, не нарушайте <#1158183124648337469> правила сервера, иначе в следующий раз вам будет выдано наказание.", inline=False)
    embed.add_field(name="Причина выдачи предупреждения", value=reason if reason else 'Не указана', inline=False)

    await interaction.send(content=f"{member.mention}", embed=embed)
    await log_action("Warning", member, reason, interaction.user)

@bot.slash_command(name='ban', description="Забанить пользователя")
@commands.has_permissions(ban_members=True)
async def ban(interaction: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = None):
    await interaction.guild.ban(member, reason=reason)  # Баним участника

    embed = disnake.Embed(title="**Выдача блокировки**", color=disnake.Color.light_gray())
    embed.add_field(name="Сообщение", value=f"Модератор {interaction.user.mention} выдал блокировку пользователю {member.mention}.", inline=False)
    embed.add_field(name="Причина выдачи наказания", value=reason if reason else 'Не указана', inline=False)

    await interaction.send(content=f"{member.mention}", embed=embed)
    
    # Логирование действия
    await log_action("Ban", member, reason, interaction.user, "Выдано")

@bot.slash_command(name='unban', description="Снять бан с пользователя")
@commands.has_permissions(ban_members=True)
async def unban(interaction: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = None):
    await interaction.guild.unban(member)  # Здесь должна быть логика для снятия бана

    embed = disnake.Embed(title="**Снятие бана**", color=disnake.Color.green())
    embed.add_field(name="Сообщение", value=f"Модератор {interaction.user.mention} снял блокировку пользователю {member.mention}.", inline=False)
    embed.add_field(name="Причина снятия бана", value=reason if reason else 'Не указана', inline=False)
    # Логирование действия
    await log_action("Unban", member, reason, interaction.user, "Снято")

bot.run('MTMzODQ2NjE5NTkwMDQ2NTI3NQ.GI5p8U.41WSbSYNE0anAYRoKTeGduy5isvrhYPru8xpZQ')

atexit.register(lambda: conn.close())