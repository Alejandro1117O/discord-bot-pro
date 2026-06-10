import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import asyncio
import random

# ========== CONFIGURACIÓN ==========

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Archivos de datos
DATA_FILE = "data.json"
XP_FILE = "xp_data.json"

def cargar_json(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_json(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

datos = cargar_json(DATA_FILE)
xp_data = cargar_json(XP_FILE)

# ========== EVENTOS ==========

@bot.event
async def on_ready():
    print("="*70)
    print(f"✓ Bot conectado como {bot.user}")
    print(f"✓ Estoy en {len(bot.guilds)} servidor(es)")
    print(f"✓ Versión: BOT PRO v3.0")
    print("="*70)
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!ayuda | Bot PRO v3.0"
        )
    )

@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.channels, name="bienvenidas")
    
    if canal:
        embed = discord.Embed(
            title=f"Bienvenido {member.name}",
            description=f"Ahora somos {member.guild.member_count} miembros",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await canal.send(embed=embed)
    
    rol_auto = discord.utils.get(member.guild.roles, name="Miembro")
    if rol_auto:
        await member.add_roles(rol_auto)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Dar XP
    guild_id = str(message.guild.id)
    user_id = str(message.author.id)
    
    if guild_id not in xp_data:
        xp_data[guild_id] = {}
    
    if user_id not in xp_data[guild_id]:
        xp_data[guild_id][user_id] = {"xp": 0, "level": 1}
    
    xp_ganado = random.randint(5, 15)
    xp_data[guild_id][user_id]["xp"] += xp_ganado
    
    nivel_actual = xp_data[guild_id][user_id]["level"]
    xp_necesario = nivel_actual * 100
    
    if xp_data[guild_id][user_id]["xp"] >= xp_necesario:
        xp_data[guild_id][user_id]["level"] += 1
        xp_data[guild_id][user_id]["xp"] = 0
        guardar_json(XP_FILE, xp_data)
        
        embed = discord.Embed(
            title="LEVEL UP",
            description=f"{message.author.mention} subio a nivel {xp_data[guild_id][user_id]['level']}",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed, delete_after=10)
    
    guardar_json(XP_FILE, xp_data)
    await bot.process_commands(message)

# ========== COMANDOS ==========

@bot.command(name='ayuda')
async def ayuda(ctx):
    embed = discord.Embed(
        title="AYUDA - BOT PRO v3.0",
        description="Todos los comandos disponibles",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="MODERACION", value="`!ban` `!kick` `!mute` `!warn` `!advertencias`", inline=False)
    embed.add_field(name="INFORMACION", value="`!info` `!usuario` `!stats` `!ping`", inline=False)
    embed.add_field(name="TICKETS", value="`!ticket crear` `!ticket cerrar`", inline=False)
    embed.add_field(name="NIVELES", value="`!nivel` `!top` `!xp`", inline=False)
    embed.add_field(name="UTILIDAD", value="`!encuesta` `!giveaway` `!lock` `!unlock`", inline=False)
    embed.add_field(name="ADMIN", value="`!limpiar` `!rol`", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    latencia = round(bot.latency * 1000)
    embed = discord.Embed(
        title="PING",
        description=f"Latencia: {latencia}ms",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, razon="Sin razon"):
    if member == ctx.author:
        await ctx.send("No puedes banearte a ti mismo")
        return
    
    await member.ban(reason=razon)
    
    embed = discord.Embed(
        title="USUARIO BANEADO",
        color=discord.Color.red()
    )
    embed.add_field(name="Usuario", value=member.mention, inline=False)
    embed.add_field(name="Razon", value=razon, inline=False)
    embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, razon="Sin razon"):
    if member == ctx.author:
        await ctx.send("No puedes expulsarte a ti mismo")
        return
    
    await member.kick(reason=razon)
    
    embed = discord.Embed(
        title="USUARIO EXPULSADO",
        color=discord.Color.orange()
    )
    embed.add_field(name="Usuario", value=member.mention, inline=False)
    embed.add_field(name="Razon", value=razon, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, tiempo: int = 60):
    rol_mute = discord.utils.get(ctx.guild.roles, name="Silenciado")
    
    if not rol_mute:
        rol_mute = await ctx.guild.create_role(name="Silenciado")
        for canal in ctx.guild.channels:
            await canal.set_permissions(rol_mute, send_messages=False, speak=False)
    
    await member.add_roles(rol_mute)
    
    embed = discord.Embed(
        title="USUARIO SILENCIADO",
        color=discord.Color.yellow()
    )
    embed.add_field(name="Usuario", value=member.mention, inline=False)
    embed.add_field(name="Duracion", value=f"{tiempo} segundos", inline=False)
    
    await ctx.send(embed=embed)
    
    await asyncio.sleep(tiempo)
    try:
        await member.remove_roles(rol_mute)
        await ctx.send(f"✓ {member.mention} dessilenciado")
    except:
        pass

@bot.command(name='warn')
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, razon="Sin razon"):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in datos:
        datos[guild_id] = {}
    
    if str(member.id) not in datos[guild_id]:
        datos[guild_id][str(member.id)] = {"nombre": member.name, "advertencias": []}
    
    datos[guild_id][str(member.id)]["advertencias"].append({
        "razon": razon,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "moderador": ctx.author.name
    })
    
    guardar_json(DATA_FILE, datos)
    
    total = len(datos[guild_id][str(member.id)]["advertencias"])
    
    embed = discord.Embed(
        title="ADVERTENCIA",
        color=discord.Color.red()
    )
    embed.add_field(name="Usuario", value=member.mention, inline=False)
    embed.add_field(name="Razon", value=razon, inline=False)
    embed.add_field(name="Total", value=total, inline=False)
    
    if total >= 3:
        await member.ban(reason="3 advertencias")
        embed.add_field(name="ACCION", value="Usuario baneado automáticamente", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='advertencias')
async def advertencias(ctx, member: discord.Member):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in datos or str(member.id) not in datos[guild_id]:
        await ctx.send(f"{member.mention} no tiene advertencias")
        return
    
    warns = datos[guild_id][str(member.id)]["advertencias"]
    
    embed = discord.Embed(
        title=f"Advertencias de {member.name}",
        color=discord.Color.orange()
    )
    
    for i, warn in enumerate(warns, 1):
        embed.add_field(
            name=f"Advertencia {i}",
            value=f"Razon: {warn['razon']}\nFecha: {warn['fecha']}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='ticket')
async def ticket(ctx, accion: str = None):
    if accion is None or accion.lower() == "crear":
        guild = ctx.guild
        categoria = discord.utils.get(guild.categories, name="Tickets")
        
        if not categoria:
            categoria = await guild.create_category("Tickets")
        
        canal = await categoria.create_text_channel(f"ticket-{ctx.author.name}")
        await canal.set_permissions(guild.default_role, view_channel=False)
        await canal.set_permissions(ctx.author, view_channel=True)
        
        embed = discord.Embed(
            title="NUEVO TICKET",
            description="Describe tu problema aqui",
            color=discord.Color.green()
        )
        await canal.send(embed=embed)
        await ctx.send(f"✓ Ticket creado: {canal.mention}")
    
    elif accion.lower() == "cerrar":
        if "ticket-" in ctx.channel.name:
            await ctx.channel.delete()
        else:
            await ctx.send("Este comando solo funciona en canales de ticket")

@bot.command(name='nivel')
async def nivel(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    if guild_id not in xp_data or user_id not in xp_data[guild_id]:
        await ctx.send(f"{member.mention} no tiene nivel aun")
        return
    
    datos_usuario = xp_data[guild_id][user_id]
    nivel = datos_usuario["level"]
    xp = datos_usuario["xp"]
    xp_necesario = nivel * 100
    
    embed = discord.Embed(
        title=f"Nivel de {member.name}",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Nivel", value=nivel, inline=True)
    embed.add_field(name="XP", value=f"{xp}/{xp_necesario}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='top')
async def top(ctx):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in xp_data:
        await ctx.send("No hay datos de XP aun")
        return
    
    usuarios = sorted(
        xp_data[guild_id].items(),
        key=lambda x: (x[1]["level"], x[1]["xp"]),
        reverse=True
    )[:10]
    
    embed = discord.Embed(
        title="TOP 10 USUARIOS",
        color=discord.Color.gold()
    )
    
    for i, (user_id, data) in enumerate(usuarios, 1):
        user = ctx.guild.get_member(int(user_id))
        if user:
            embed.add_field(
                name=f"#{i} {user.name}",
                value=f"Nivel {data['level']} - {data['xp']} XP",
                inline=False
            )
    
    await ctx.send(embed=embed)

@bot.command(name='encuesta')
async def encuesta(ctx, *, pregunta):
    embed = discord.Embed(
        title="ENCUESTA",
        description=pregunta,
        color=discord.Color.purple()
    )
    
    mensaje = await ctx.send(embed=embed)
    await mensaje.add_reaction("👍")
    await mensaje.add_reaction("👎")

@bot.command(name='giveaway')
async def giveaway(ctx, *, premio):
    embed = discord.Embed(
        title="SORTEO",
        description=f"Premio: {premio}",
        color=discord.Color.gold()
    )
    embed.add_field(name="Reacciona con 🎉", value="Para participar", inline=False)
    
    mensaje = await ctx.send(embed=embed)
    await mensaje.add_reaction("🎉")

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(title="CANAL BLOQUEADO", color=discord.Color.red())
    await ctx.send(embed=embed)

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(title="CANAL DESBLOQUEADO", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(
        title=f"Informacion de {ctx.guild.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Propietario", value=ctx.guild.owner.mention, inline=False)
    embed.add_field(name="Miembros", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Canales", value=len(ctx.guild.channels), inline=False)
    embed.add_field(name="Roles", value=len(ctx.guild.roles), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='usuario')
async def usuario(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"Informacion de {member.name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Se unio", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles[1:]]) or "Ninguno", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def stats(ctx):
    usuarios_activos = sum(1 for member in ctx.guild.members if member.status != discord.Status.offline)
    bots = sum(1 for member in ctx.guild.members if member.bot)
    
    embed = discord.Embed(
        title="ESTADISTICAS",
        color=discord.Color.purple()
    )
    embed.add_field(name="Total", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Activos", value=usuarios_activos, inline=False)
    embed.add_field(name="Bots", value=bots, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='limpiar')
@commands.has_permissions(manage_messages=True)
async def limpiar(ctx, cantidad: int = 10):
    if cantidad > 100:
        await ctx.send("Max 100 mensajes")
        return
    
    deleted = await ctx.channel.purge(limit=cantidad)
    embed = discord.Embed(
        title="CANAL LIMPIADO",
        description=f"Se eliminaron {len(deleted)} mensajes",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, delete_after=5)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes permisos")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Argumento invalido")

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERROR: Configura DISCORD_TOKEN en .env")
    exit()

bot.run(TOKEN)
