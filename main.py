import os
import discord
import yaml

from datetime import datetime
from datetime import timedelta

from dotenv import load_dotenv
from discord_slash import SlashCommand, SlashContext

from functions import*
from database import Database

liste_insultes = ['putain', 'con', 'connard', 'connasse', 'pute', 'tg', 'ta gueule', 'sex', 'sexuelement', 'viol', 'violer', 'winnie l\'ourson', 'taiwan', 'negro', 'nez gros', 'nee gros', 'batard', 'couiles', 'casse les couilles']
persos = {
    "yae": datetime(2022, 2, 16, 0, 4, 0),
    "ayato": datetime(2022, 3, 31, 0, 4, 0)
}

db = Database("Jean-Michel.db")

guild_ids = yaml.safe_load(db.get_value("guild_ids"))
serveurs_avec_censure = yaml.safe_load(db.get_value("censored_guilds"))
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
        print(f"{msg.author} a dit \"{msg.content}\" dans #{msg.channel} sur {msg.guild.name}")
        if contain_bad_word(msg.content, liste_insultes) and not msg.author.bot and str(msg.guild.id) in serveurs_avec_censure:
            print(f"message pas gentil: \"{msg.content}\", message supprimé")
            await msg.delete()
            await msg.author.send("Tu as dit un mot pas gentil, ton message a été supprimé")
    except AttributeError:
        pass

@slash.slash(name="tempsPerso", guild_ids=guild_ids, description="Donne le temps restant avant la sortie d'un personnage de Genshin Impact")
async def temps_perso(ctx, perso: str):
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


jean_michel.run(TOKEN)
