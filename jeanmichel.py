import os
import discord

from random import randint
from datetime import datetime
from datetime import timedelta

from discord.ext import commands
from dotenv import load_dotenv

from functions import*


liste_insultes = ['putain', 'con', 'connard', 'connasse', 'pute', 'tg', 'ta gueule', 'sex', 'sexuelement', 'viol', 'violer', 'winie l\'ourson', 'taiwan', 'negro', 'nez gros', 'nee gros', 'batard', 'couiles', 'casse les couilles']
persos = {
    "yae": datetime(2022, 2, 16, 0, 4, 0),
    "ayato": datetime(2022, 3, 31, 0, 4, 0)
}

jean_michel = commands.Bot(command_prefix='..', help_command=None)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Event qui se déclenche lorsque que le bot est prêt
@jean_michel.event
async def on_ready():
    print(f'{jean_michel.user.name} s\'est connecté à Discord')
    await jean_michel.change_presence(status=discord.Status.online, activity=discord.Game("être une version 3.0 de moi-même"))  # Défini le jeu du bot

@jean_michel.event
async def on_message(msg: discord.Message):
    print(f"{msg.author} a dit \"{msg.content}\" dans #{msg.channel} sur {msg.guild.name}")
    if contain_bad_word(msg.content, liste_insultes) and not msg.author.bot:
        await msg.delete()
        await msg.author.send("Tu as dit un mot pas gentil, ton message a été supprimé")
        print("message pas gentil, message supprimé")

@jean_michel.command(name="tempsPerso")
async def temps_perso(ctx, perso: str):
    global persos
    if perso.lower() not in persos:
        await ctx.send(f"Le personnage {perso} n'est pas dans ma base de données.")
    else:
        tformat = "{days} jour(s) {hours}h, {minutes} minutes et {seconds} secondes"
        temps_avant_perso = strfdelta((persos[perso.lower()] - datetime.now()), tformat)

        await ctx.send(f"{temps_avant_perso} avant {perso}")

@jean_michel.command(name="supp")
async def supp(ctx):
    """Commande pour supprimer des messages qui date d'une certaine durée"""
    # TODO si les messages sont là depuis plus de 14 jours, les supprimer "manuellement"
    msg = await ctx.channel.history(limit=100).flatten()  # liste des messages du salon, la limite est de 100
    a_supp = []  # liste des messages à supprimer
    now = datetime.now()  # prend la date actuelle
    for message in msg:  # parcours les messages dans la liste crée plus tôt
        msg_diff = now - message.created_at  # calcule la différence entre la date actuelle et la date du message
        if timedelta(days=1) < msg_diff < timedelta(days=13, hours=23):  # si la différence est dans l'intervalle donné
            a_supp.append(message)  # ajoute le message à la liste pour être supprimé après
            print(f"Le message \"{message.content}\", qui date du {message.created_at}, va été supprimé")
    await ctx.channel.delete_messages(a_supp)  # supprime les messages dans la liste
