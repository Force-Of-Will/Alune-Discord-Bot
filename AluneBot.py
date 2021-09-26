#   Benjamin Longwell
#   Discord Bot (Alune)
#   Using Discord Library: 
#       https://discordpy.readthedocs.io/en/latest/migrating.html
#   Using SQL Python Connector
#   Purpose: Alune Bot sheds her moonlight on individual activity in a discord server. 
#       Discord can only prune / keep track of users of inactivity within 7 or 30+ days, 
#       Why not be able to specify a date to keep track of Activity? 
#           i.e. Keep track of users inactivity after exactly (x) days
#       Alune can also see your League Of Legends Solo-Queue Rank (Prepare to call out your friends)
#   Date: Last Modified 9/23/2021
#   Input: Enter your RAPI, Bot Token, and SQL database password into the creds.txt file
#   - Imports - #
import discord
import random
import requests
import mysql.connector
from datetime import date, datetime

#   - Globals   - #
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

#shows a default activity listing for users who are in guilds the bot can see
#   is in the form of a embed
def checkActivity(guildID):
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    mycursor = mydb.cursor()
    query = "SELECT Username, DateLastActive FROM ServerActivity, User WHERE ServerActivity.UserID = User.UserID AND GuildID = {}".format(guildID)
    print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query);
        myresult = mycursor.fetchall();
        for x in myresult:
            print(x); 
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    retString = ""
    embed = getEmbed(myresult, "Activity Check", "Checks all user's activity")
    for tuple in myresult:
        retString = retString + "{0:<32s}{1:>12s}\n".format(tuple[0], str(tuple[1]))
        #retString = retString + tuple[0].ljust(32, " ")
        #retString = retString + str(tuple[1]).rjust(10, " ") + "\n"
    return embed
#       -End checkActivity()-      #

#shows a default activity listing for users who are in guilds the bot can see
#   is in the form of a embed
def checkInctivity(guildID, date):
    formattedDate = str(date.strftime("%Y/%m/%d"))
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    mycursor = mydb.cursor()
    query = "SELECT Username, DateLastActive FROM ServerActivity, User WHERE ServerActivity.UserID = User.UserID AND GuildID = \"{}\" AND DateLastActive < \"{}\"".format(str(guildID), formattedDate)
    print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query);
        myresult = mycursor.fetchall();
        for x in myresult:
            print(x); 
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    retString = ""
    embed = getEmbed(myresult, "Inactivity Check", "Checks inactivity before date:{}".format(formattedDate))
    for tuple in myresult:
        retString = retString + "{0:<32s}{1:>12s}\n".format(tuple[0], str(tuple[1]))
        #retString = retString + tuple[0].ljust(32, " ")
        #retString = retString + str(tuple[1]).rjust(10, " ") + "\n"
    return embed
#       -End checkActivity()-      #

#This function determines based on the message a user has sent wether or not they exist in the server database
# Outputs:
#       True - User exists in the serveractivity table
#       False - User does not exist in the serveractivity table
def userExistsInServer(message):
    #check to see if the user has sent any messages to that guild before with a query,  
    #if they havent, add them to serverActivity / user tables if needed
    #access the db
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    #create a cursor
    mycursor = mydb.cursor()
    #gathering the userID + guildID
    msgUserID = message.author.id
    msgGuildID = message.guild.id 
    #format messageID + guildID to see if it already exists in the table
    query = "SELECT COUNT(1) FROM serveractivity WHERE userID = {} AND guildID = {}".format(msgUserID, msgGuildID)
    #print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query)
        myresult = mycursor.fetchall()
        #print(len(myresult))
        #testing Statements
        #for x in myresult:
        #    print(x); 
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    #myresult[0][0] holds a zero or a one. 0 means user does not exist in this particular server , 1 means they do exist already in this server
    bool = True if myresult[0][0] == 1 else False
    return bool

#This function determines based on the message a user has sent wether or not they exist in the general database
# Outputs:
#       True - User exists in the users table
#       False - User does not exist in the users table
def userExistsInDB(message):
    #check to see if the user has sent any messages ANYWHERE before with a query,  
    #access the db
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    #create a cursor
    mycursor = mydb.cursor()
    #gathering the userID + guildID
    msgUserID = message.author.id
    msgGuildID = message.guild.id #we technically dont need this here because the user table doesnt look at guild IDs
    #format messageID + guildID to see if it already exists in the table
    query = "SELECT COUNT(1) FROM User WHERE userID = {}".format(msgUserID)#see if the user is in the user table
    #print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query)
        myresult = mycursor.fetchall()
        #print(len(myresult))
        #testing Statements
        #for x in myresult:
        #    print(x); 
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    #myresult[0][0] holds a zero or a one. 0 means user does not exist in this particular server , 1 means they do exist already in this server
    bool = True if myresult[0][0] == 1 else False
    return bool

#   inserts a user's data into the serveractivity table (Assumed to not exist previously)
#   Input: The message the user sent passed from main
def insertIntoServer(message):
    #gathering the userID + guildID
    msgUserID = message.author.id
    msgGuildID = message.guild.id
    #create and format the date 
    today = date.today()
    formattedDate = today.strftime("%Y/%m/%d")
    print("The formatted date is " + formattedDate)
    #create the connection
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    #make the cursor
    mycursor = mydb.cursor()
    query = "INSERT INTO serveractivity VALUES ({},{},\"{}\")".format(msgGuildID, msgUserID, str(formattedDate))
    print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query)
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    mydb.commit()
    return

#   inserts a user's data into the users table (Assumed to not exist previously)
#   Input: The message the user sent passed from main
def insertIntoDB(message):
    #gathering the userID + guildID
    msgUserID = message.author.id
    msgUserName = message.author.name
    #create and format the date 
    today = date.today()
    formattedDate = today.strftime("%Y/%m/%d")
    #create the connection
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    #make the cursor
    mycursor = mydb.cursor()
    query = "INSERT INTO User VALUES ({},\"{}\")".format(msgUserID, msgUserName)
    print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query)
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    mydb.commit()
    return

#updates lastActiveDate in a Server given passed message ID
def updateServerWithUser(message):
    #gathering the userID + guildID
    msgUserID = message.author.id
    msgGuildID = message.guild.id
    #create and format the date 
    today = date.today()
    formattedDate = today.strftime("%Y/%m/%d")
    print("The formatted date is " + formattedDate)
    #create the connection
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    #make the cursor
    mycursor = mydb.cursor()
    query = "UPDATE ServerActivity Set DateLastActive = \"{}\" WHERE UserID = \"{}\" AND GuildID = \"{}\"".format(str(formattedDate), msgUserID, msgGuildID)
    print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query)
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    mydb.commit()
    return

#Updates a user's username in the database
def updateDBWithUser(message):
    #gathering the userID + guildID
    msgUserID = message.author.id
    msgUserName = message.author.name
    #create and format the date 
    today = date.today()
    formattedDate = today.strftime("%Y/%m/%d")
    #create the connection
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = SQLPW,
        database = "alunebot"
    )
    #make the cursor
    mycursor = mydb.cursor()
    query = "UPDATE User Set Username = \"{}\" WHERE UserID = \"{}\"".format(msgUserName, msgUserID)
    print("The query is : \"" + query +"\"")
    try:
        mycursor.execute(query)
    except mysql.connector.Error as err:
        print("Error Querying Data. Try Again. Error: {}".format(err))
    mydb.commit()
    return

#Creates an Embed assuming tuple list input, embed title, and embed description
def getEmbed(myResult, embedTitle, desc):
    embed = discord.Embed(
        title = embedTitle,
        description = desc,
        colour = discord.Colour.light_gray()
    )

    #embed.set_footer(text= "This is a test footer")
    #embed.set_image(url= 'https://static.wikia.nocookie.net/leagueoflegends/images/9/97/03MT215-full.png/revision/latest/scale-to-width-down/250?cb=20210203093534')
    #embed.set_thumbnail(url= 'https://static.wikia.nocookie.net/leagueoflegends/images/2/22/03MT053-full.png/revision/latest/scale-to-width-down/250?cb=20200825193243')
    embed.set_author(name= "Alune Bot", icon_url= 'https://cdn.discordapp.com/avatars/687741583327887396/65effd5ff1f46f0530c2f44c65437e12.webp?size=32')
    for tuple in myResult:
        embed.add_field(name=tuple[0], value=str(tuple[1]), inline=False)
    return embed

#When the bot sees someone sent a message, looks at the message to see if anything can be done with it.
@client.event
async def on_message(message):
    #print("User exists in server: " + str(userExistsInServer(message)))
    #print("User exists in DB " + str(userExistsInDB(message)))
    isInDB = userExistsInDB(message)
    isInServer = userExistsInServer(message)
    if(isInDB and isInServer):
        print("We need to update this person in all the places.")
        updateDBWithUser(message)
        updateServerWithUser(message)
    elif(isInDB and not isInServer):
        print("We need to add this person to the Server Database, and update their User info")
        insertIntoServer(message)
    elif(not isInDB and not isInServer):
        print("We need to add this person to the Server DB AND the main DB")
        insertIntoDB(message)
        insertIntoServer(message)
    else:
        print("We have a user who does not exist in the DB but NOT in the Server. Consider this an error.")

    #if they HAVE sent a message here before, we should try and update their 
    #Username, dateLastActive, and 
    #start msg as null so we can see if it was properly managed at the end
    msg = 'null'
    #if this message is coming from the bot, ignore it, 
    #otherwise she might talk to herself. 
    if message.author == client.user:
        return
    #the quoting mechanism
    elif message.content.startswith('!quote'):
        channel = client.get_channel(message.channel.id)
        msg = chooseQuote()
        await channel.send(msg) 
    #!rank command with riot API
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
    #checks user activity using sql database
    elif message.content.startswith("!checkActivity"):
        activityEmbed = checkActivity(message.guild.id)
        channel = client.get_channel(message.channel.id)
        await channel.send(embed= checkActivity(message.guild.id))
    elif message.content.startswith("!checkInactivity"):
        channel = client.get_channel(message.channel.id)
        date = message.content.replace("!checkInactivity ", "")
        dateObj = datetime.strptime(date, "%Y/%m/%d")
        inactivityEmbed = checkInctivity(message.guild.id, dateObj)
        await channel.send(embed= inactivityEmbed)
    elif message.content.startswith("!embedTest"):
        channel = client.get_channel(message.channel.id)
        await channel.send("Command Depreciated")
    #can be used to close the bot via discord
    elif message.content.startswith('!die'):
        channel = client.get_channel(message.channel.id)
        msg = "Logging out..."
        await channel.send(msg)
        await client.logout()
    print("Sent message in channel: " + message.content)
    print('---------')
    return

#when the bot starts   
@client.event
async def on_ready():
   print('Logged in under: ' + client.user.name)
   print('Bot user ID: ' + str(client.user.id))
   await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Lunari Pools"))
   print('---------')
def main():
    client.run(TOKEN)
main()
