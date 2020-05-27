import json
import os
import proba
from proba import TirageImpossible
import discord
import autorisation
from discord.utils import get
# ajouter un composant de discord.py
from discord.ext import commands
#lien du bot : https://discord.com/api/oauth2/authorize?client_id=712698954227253339&permissions=0&scope=bot
# import pyNaCl

bot = commands.Bot(command_prefix='!')
bot.remove_command("help")
#récupération du jeton
token = autorisation.token
comptePath = autorisation.compteArena
decksPath = autorisation.decks
prochainDeck = {}

@bot.event
#détection de l'allumage du bot
async def on_ready():
    await bot.change_presence(status=discord.Status.online,activity=discord.CustomActivity("Fais des gauffres !"))

@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(colour=discord.Colour.orange())
    embed.set_author(name="help")
    embed.add_field(name = "!calendrier", value="renvoye un lien vers un site ayant un calendrier des évènements limités",inline = True)
    embed.add_field(name="!graph A B C",value="Renvoie la répartition de probabilité de piocher des cartes spécifiques\
 dans un deck de A cartes en contenant B, lorsque l'on en pioche C",inline=True)
    embed.add_field(name="!ajouterCompte A",value="ajouter le compte Arena à la liste des comptes de joueurs.",inline=True)
    embed.add_field(name="!voirCompte",value="Vois les compte des différents membres du serveur l'ayant renseigné.")
    embed.add_field(name="!addDeck NomDeck exportDeck",value="Permet d'ajouter un deck avec le nom que l'on veut à la base de données consultable.")
    embed.add_field(name="!voirDeck A",value="Permet de voir les decks entrés par le membre A")
    embed.add_field(name="!codes",value="renvoie un lien répertoriant les codes bonus de MTGA")
    # embed.add_field(name="!quote",value="sort une citation aléatoire (doit encore trouver un receuil de citation)")
    await ctx.send(embed=embed)

@bot.command()
async def ajouterCompte(ctx,compte):
    arenaID = {}
    authorID = str(ctx.author.id)
    authorName = str(ctx.author.name)
    serveur = str(ctx.guild.id)
    if os.path.isfile(comptePath):
        with open(comptePath,"r",encoding="utf8") as f:
            arenaID = json.load(f)
    if not serveur in arenaID.keys():
        arenaID[serveur] = [{"authorID" : authorID,"nom":authorName,"ArenaID":compte}]
    ajout = True
    for membre in arenaID[serveur]:
        if membre["authorID"] == authorID:
            ajout = False
    if ajout:
        arenaID[serveur].append({"authorID" : authorID,"nom":authorName,"ArenaID":compte})
    with open(comptePath,"w",encoding="utf8") as f:
        json.dump(arenaID,f,indent=4)
    await ctx.send("ajout effectué, je crois")

@bot.command()
async def voirCompte(ctx):
    serveur = str(ctx.guild.id)
    arenaID = {}
    if os.path.isfile(comptePath):
        with open(comptePath,"r",encoding= "utf8") as f:
            arenaID = json.load(f)
    if serveur in arenaID.keys():
        message = "Les comptes arena des gens sur le serveur sont : \n"
        for membre in arenaID[serveur]:
            message += "{}  :  {}\n".format(membre["nom"] , membre["ArenaID"])
        await ctx.send(message)
    else:
        await ctx.send("Pas de compte Arena enregistré par les membres de ce serveur !")

@bot.command()
async def addDeck(ctx,*arg):
    decks= {} 
    ajout = False
    authorID = str(ctx.author.id)
    serveur = str(ctx.guild.id)
    compteArena = None
    if not os.path.isfile(comptePath):
        pass
    else:
        with open(comptePath,"r",encoding="utf8") as f:
            compteArena = json.load(f)
            if serveur in compteArena.keys():
                for membre in compteArena[serveur]:
                    if membre["authorID"] == authorID:
                        ajout = True
    if not ajout:
        await ctx.send("Vous n'avez pas encore enregistrez votre compte arena à l'aide de la commande !ajouterCompte")
    else:
        keyword = ["Compagnon","Deck","Réserve"]
        i = 1
        nom = arg[0]
        deck = ""
        limiteNomDeck = False
        for i in range(1 , len(arg)):
            if arg[i] in keyword:
                limiteNomDeck = True
            if not limiteNomDeck: 
                nom += " {}".format(arg[i])
            else:
                if deck == "":
                    deck += arg[i]
                else:#je passe à une nouvelle si 2 nombre consécutif, si chiffre puis keyword avant ou si keyword puis chiffre sinon ajout espace ?
                    if ((arg[i] in keyword or arg[i].isdigit()) and arg[i-1].isdigit()) or (arg[i].isdigit() and arg[i-1] in keyword):
                        deck += "\n{}".format(arg[i])
                    else:
                        deck += " {}".format(arg[i])    
        if deck != "":
            if not os.path.isfile(decksPath): 
                pass
            else:
                with open(decksPath,"r",encoding="utf8") as f:
                    decks = json.load(f)
            if not serveur in decks.keys():
                decks[serveur] = {}
            if not authorID in decks[serveur].keys():
                decks[serveur][authorID] = {}
            decks[serveur][authorID][nom] = deck   
    with open(decksPath,"w",encoding="utf8") as f:
        json.dump(decks,f,indent=4)
    await ctx.author.send("deck {} enregistré".format(nom))

@bot.command()
async def voirDeck(ctx,arg):
    serveur = str(ctx.guild.id)
    critRech = {}
    decks = {}
    deckslist = None
    arenaID = None
    if os.path.isfile(comptePath):
        with open(comptePath,"r",encoding= "utf8") as f:
            arenaID = json.load(f)
        if serveur in arenaID.keys():
            for membre in arenaID[serveur]:
                if arg in membre["nom"]:#parcours de la liste des membre du serveur
                    critRech[membre["authorID"]] = membre["nom"]
    if os.path.isfile(decksPath):
        with open(decksPath,"r",encoding= "utf8") as f:
            deckslist = json.load(f)
        if serveur in deckslist.keys():
            for deckMakerID,deckMaker in critRech.items():
                for maker in deckslist[serveur].keys():
                    if deckMakerID == maker:
                        for nom, deck in deckslist[serveur][deckMakerID].items():
                            decks["{} par {}".format(nom,deckMaker)] = deck
    if len(decks)>0:
        for nom,deck in decks.items():
            mes = "{} :\n{}\n\n".format(nom,deck)
            await ctx.author.send(mes)
    else:
        await ctx.send("pas de deck trouvé...")

@bot.command()
async def graph(ctx,deck,nbr,pioche):
    print("demande de graphe bien reçue")
    fichierPath = "repartition_temp.png"
    try:
        deck = int(deck)
        nbr = int(nbr)
        pioche = int(pioche)
        proba.analyseProbImg(deck,nbr,pioche,fichierPath)
        fichier = discord.File(fichierPath,filename=fichierPath)
        await ctx.send(file=fichier)
    except ValueError:
        await ctx.send("Ce que vous demandez, je ne peux traiter que des nombres entiers pour ces tirages")
    except TirageImpossible:
        await ctx.send("Comment voulez-vous que je tires plus d'éléments que ce qu'il y en a ?")

@bot.command()
async def calendrier(ctx):
    message = "Le calendrier est disponible via ce lien https://mtgazone.com/events/month/"
    await ctx.send(message)

@bot.command()
async def codes(ctx):
    message = "Les codes peuvent être obtenu via le lien https://cardgamebase.com/mtg-arena-codes/"
    await ctx.send(message)

# @bot.command()
# async def join(ctx):
#     test = ctx.author.voice.channel
#     print(test)
#     await test.connect()



print("Lancement du bot...")
bot.run(token)

