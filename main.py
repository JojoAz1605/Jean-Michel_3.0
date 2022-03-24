import os
import discord
import ast

from datetime import datetime
from datetime import timedelta

from dotenv import load_dotenv
from discord_slash import SlashCommand, SlashContext
from discord.ext import tasks

from functions import*
from database import Database

liste_insultes = ['putain', 'con', 'connard', 'connasse', 'pute', 'tg', 'ta gueule', 'sex', 'sexuelement', 'viol', 'violer', 'winnie l\'ourson', 'taiwan', 'negro', 'nez gros', 'nee gros', 'batard', 'couiles', 'casse les couilles']
persos = {
    "yae": datetime(2022, 2, 16, 0, 4, 0),
    "ayato": datetime(2022, 3, 31, 0, 4, 0)
}

db = Database("Jean-Michel.db")

guild_ids = ast.literal_eval(db.get_value("guild_ids"))
serveurs_avec_censure = ast.literal_eval(db.get_value("censored_guilds"))
announce_channels = ast.literal_eval(db.get_value("announce_channels"))
jean_michel = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(jean_michel, sync_commands=True)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


@jean_michel.event
async def on_ready():
    """Event qui se déclenche lorsque que le bot est prêt"""
    print(f'{jean_michel.user.name} s\'est connecté à Discord')
    await jean_michel.change_presence(status=discord.Status.online, activity=discord.Game("être tout beau parce que je suis parfait"))  # Défini le jeu du bot

@jean_michel.event
async def on_message(msg: discord.Message):
    """Event qui se déclenche lorsqu'un message est envoyé par une personne"""
    try:
        print(f"{msg.author} a dit \"{msg.content}\" dans #{msg.channel} sur {msg.guild.name}(id: {msg.guild.id}")
        if contain_bad_word(msg.content, liste_insultes) and not msg.author.bot and msg.guild.id in serveurs_avec_censure:
            print(f"message pas gentil: \"{msg.content}\", message supprimé")
            await msg.delete()
            await msg.author.send("Tu as dit un mot pas gentil, ton message a été supprimé")
    except AttributeError:
        pass

@tasks.loop(minutes=1)
async def called_once_a_day():
    global announce_channels
    for channel in announce_channels:
        await jean_michel.get_channel(channel).send("oui")

@slash.slash(name="activateThisChan", guild_ids=guild_ids, description="Permet d'activer le salon comme salon d'annonce du bot")
async def activate_this_chan(ctx: SlashContext):
    global announce_channels
    announce_channels.append(ctx.channel_id)
    db.set_value("announce_channels", announce_channels)
    print(f"Le salon {ctx.channel.name} d'id {ctx.channel_id} a été défini comme salon d'annonce!")


@slash.slash(name="tempsPerso", guild_ids=guild_ids, description="Donne le temps restant avant la sortie d'un personnage de Genshin Impact")
async def temps_perso(ctx: SlashContext, perso: str):
    global persos
    if perso.lower() not in persos:  # si le perso n'est pas dans la liste
        await ctx.send(f"Le personnage {perso} n'est pas dans ma base de données.") # dit qu'il n'est pas dans la liste
    else:
        tformat = "{days} jour(s) {hours}h, {minutes} minutes et {seconds} secondes"  # donne le format de la phrase
        temps_avant_perso = strfdelta((persos[perso.lower()] - datetime.now()), tformat)  # forme la réponse avec le temps restant
        await ctx.send(f"{temps_avant_perso} avant {perso}")  # l'envoie

@slash.slash(name="supp", guild_ids=guild_ids, description="Supprime les messages datant de plus de 24h dans le salon actuel")
async def supp(ctx: SlashContext, nb_messages: int = None):
    """Commande pour supprimer des messages qui date d'une certaine durée"""
    message_state = await ctx.send("Je commence la suppression...")
    compteur = 0
    print(f"Suppression des messages dans #{ctx.channel} sur {ctx.guild}")
    messages = await ctx.channel.history(limit=nb_messages).flatten()  # liste des messages du salon, la limite est de 100
    a_supp = []  # liste des messages à supprimer
    now = datetime.now()  # prend la date actuelle
    for msg in messages:  # parcours les messages dans la liste crée plus tôt
        msg_diff = now - msg.created_at  # calcule la différence entre la date actuelle et la date du msg
        if msg_diff > timedelta(days=13, hours=23):
            print(f"Suppression du msg \"{msg.content}\"")
            await msg.delete()
            compteur += 1
        elif msg_diff > timedelta(days=1):  # si la différence est dans l'intervalle donné
            a_supp.append(msg)  # ajoute le msg à la liste pour être supprimé après
            print(f"Le msg \"{msg.content}\", qui date du {msg.created_at}, va été supprimé")
    compteur += len(a_supp)
    await ctx.channel.delete_messages(a_supp)  # supprime les messages dans la liste
    await message_state.edit(content=f"J'ai fini la suppression des messages datant de plus de 24h, j'en ai supprimé {compteur}")
    print("Fin de la suppression \n")

@slash.slash(name="listMembers", description="Donne la liste des membres du serveur", guild_ids=guild_ids)
async def list_members(ctx: SlashContext):
    members = []
    for member in ctx.guild.members:
        members.append(member.name)
    await ctx.send(str(members))

@slash.slash(name="serverCensorState", description="Donne l'état actuel de la censure sur le serveur", guild_ids=guild_ids)
async def server_censor_state(ctx: SlashContext):
    if ctx.guild.id in serveurs_avec_censure:
        await ctx.send("La censure est activée sur ce serveur")
    else:
        await ctx.send("La censure n'est pas activée sur ce serveur")

@slash.slash(name="toggleCensoring", description="Permet de changer l'état de la censure sur ce serveur", guild_ids=guild_ids)
async def toggle_censor_state(ctx: SlashContext):
    if ctx.author.id == ctx.guild.owner.id:
        if ctx.guild.id in serveurs_avec_censure:
            serveurs_avec_censure.remove(ctx.guild.id)
            await ctx.send("La censure est maintenant désactivée")
        else:
            serveurs_avec_censure.append(ctx.guild.id)
            await ctx.send("La censure est maintenant activée")
        db.set_value("censored_guilds", serveurs_avec_censure)
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande")

@slash.slash(name="addSlashSupport", description="Ajoute le support des commandes slash sur le serveur")
async def add_slash_support(ctx: SlashContext):
    if ctx.guild.id not in guild_ids and ctx.author.id == ctx.guild.owner.id:
        guild_ids.append(ctx.guild.id)
        db.set_value("guild_ids", guild_ids)
        await ctx.send("Ce serveur supporte maintenant mes commandes slash")
    else:
        await ctx.send("Ce serveur supporte déjà mes commandes slash")

jean_michel.run(TOKEN)
