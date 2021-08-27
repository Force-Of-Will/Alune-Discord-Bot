#Benjamin Longwell
#Discord Bot (Alune)
#using discord.py https://discordpy.readthedocs.io/en/latest/migrating.html
#https://discordpy.readthedocs.io/en/latest/index.html
import discord
import random
import requests
import mysql.connector
#Globals
f = open("creds.txt", "r")
TOKEN = f.readline().replace("TOKEN: ", "")
client = discord.Client()
APIKey = f.readline().replace("APIKEY: ", "")
SQLPW = f.readline().replace("SQL_Password: ", "")

#Gets a user's summoner ID given their IGN and the API key
def getSummID(summonerName, APIKey):
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    #print(summonerName + " " + URL)
    response = requests.get(URL)
    response = response.json()
    #print(response);
    ID = response['id']
    ID = str(ID)
    return ID

#gets a user's summoner name given s nonformatted IGN and API key
def getSName(summonerName, APIKey):
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    #print(summonerName + " " + URL)
    response = requests.get(URL)
    response = response.json()
    #print(response);
    sName = response['name']
    sName = str(sName)
    return sName

#Returns a string representation of a person's LOL rank
def getRankedData(ID, APIKey):
    URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + ID + "?api_key=" + APIKey
    response = requests.get(URL)
    response = response.json()
    print(response)
    #response = json.dumps(response);
    #response = ast.literal_eval(response)
    try:
        tier = response[0]['tier']
        tier = str(tier)
        rank = response[0]['rank']
        rank = str(rank)
        lp = response[0]['leaguePoints']
        lp = str(lp)
        msg = " is a " + tier + " " + rank + " ranked hoe with " + lp + " LP."
    except:
        tier = response[1]['tier']
        tier = str(tier)
        rank = response[1]['rank']
        rank = str(rank)
        lp = response[1]['leaguePoints']
        lp = str(lp)
        msg = " is a " + tier + " " + rank + " ranked hoe with " + lp + " LP."
    return msg

#Goes into the reactions.txt file, picks a random quote, returns the quote
def chooseQuote():
    reactions = open("reactions.txt", "r")
    value = random.randrange(1, 45, 1)
    msg = 'null'
    for x in range(value):
        msg = reactions.readline()
    reactions.close()
    return msg
#test an array of roles (as strings) andreturn whether or not the user has the role or not.
def testRoles(myRoles, forRole):
    for role in myRoles:
        print("Testing role " + str(role) + " == " + forRole + ".")
        if (str(role) == forRole): return True
    return False

def checkActivity():
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    mycursor = mydb.cursor()
    query = "SELECT Username, DateLastActive FROM ServerActivity, User WHERE ServerActivity.UserID = User.UserID"
    print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query);
        myresult = mycursor.fetchall();
        for x in myresult:
            print(x); 
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
#       -End checkActivity()-      #

#When the bot sees someone sent a message, looks at the message to see if anything can be done with it.
@client.event
async def on_message(message):
    #start msg as null so we can see if it was properly managed at the end
    msg = 'null'
    #if this message is coming from the bot, ignore it, 
    #otherwise she might talk to herself. 
    if message.author == client.user:
        return
    elif message.content.startswith('!quote'):
        channel = client.get_channel(message.channel.id)
        msg = chooseQuote()
        await channel.send(msg) 
    elif message.content.startswith("!rank"):
        msg = message.content
        msg = msg.replace("!rank","")
        msg = msg.replace(" ","")
        print("Getting rank for " + msg + " from RAPI.")
        ID = getSummID(msg, APIKey)
        sName = getSName(msg, APIKey)
        msg = sName + getRankedData(ID, APIKey)
        channel = client.get_channel(message.channel.id)
        await channel.send(msg)
    elif message.content.startswith("!checkActivity"):
        checkActivity()
    elif message.content.startswith('!die'):
        channel = client.get_channel(message.channel.id)
        msg = "Logging out..."
        await channel.send(msg)
        await client.logout()
    print("Sent message in channel: " + message.content)
    print('------')
    return

#sees when someone is typing, acts accordingly
@client.event
async def on_typing(channel, user, when):
   print("User " + str(user.display_name) + " began typing at " + str(when) + " and has the roles:")
   userRoles = user.roles
   for role in userRoles: print(role)
   print("\n")
   if(userRoles[0] == "@everyone"): userRoles.pop(0)
   #Test the userRoles for a role.
   #amSimp = testRoles(userRoles, "Aspect of the Moon")
   #FIXME if you want her to simp.
   #if(amSimp): await channel.send("UwU notice me senpai.")
   #else: await channel.send("Stop typing, hoe.")
   #await channel.send("Stop typing, hoe.")
   
#when the bot starts   
@client.event
async def on_ready():
   print('Logged in as: ' + client.user.name)
   print('ID: ' + str(client.user.id))
   print('------')
def main():
    client.run(TOKEN)
main()
