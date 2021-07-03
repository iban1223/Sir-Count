# bot.py
from asyncio.windows_events import NULL, PipeServer
import os
import discord

from discord.ext import commands

from dotenv import load_dotenv

# Loading the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setting the command prefix
bot = commands.Bot(command_prefix='sc!')

# File reading editing and printing handlers
#Reading in file
def readData(file):
    with open(file, 'r') as file:
        data = file.readlines()                                 #read a list of lines into data
    return data

#Writing Data to a file
def writeData(file, data):
    with open(file, 'w') as file:
        file.writelines(data)                                   #writing lines to the file

#Returns the line number of a line starting with a value
def findData(data, start):
    x = 0
    for dataIndex in data:
        x += 1
        if dataIndex.startswith(start, 0, len(start)):
            return x
    return -1

#Function to write all counts data to a file
def writeCounts(file):
    counts = bot.counts
    for countsIndex in counts:
        place = findData(bot.data, str('c ' + countsIndex.displayChannel()))
        if ( place == -1 ):
            bot.data.append('c ' + str(countsIndex.displayChannel()) + ' ' + str(countsIndex.displayCount()) + ' ' + str(countsIndex.displayHigh()) + '\n')
        else:
            bot.data[place-1] = str('c ' + countsIndex.displayChannel()) + ' ' + str(countsIndex.displayCount()) + ' ' + str(countsIndex.displayHigh()) + '\n'
    writeData(file, bot.data)

#Function to read all counts data from a file
def readCounts():
    counts = bot.counts
    data = bot.data
    for dataIndex in data:
        line = dataIndex.split()
        if line[0] == 'c':
            counts.append(count(line[1], int(line[2]), int(line[3])))

#Function to write all people data to a file
def writePeople(file):
    people = bot.people
    for peopleIndex in people:
        place = findData(bot.data, str('p ' + peopleIndex.showName()))
        if ( place == -1 ):
            bot.data.append('p ' + str(peopleIndex.showName()) + ' ' + str(peopleIndex.showScore()) + '\n')
        else:
            bot.data[place-1] = 'p ' + str(peopleIndex.showName()) + ' ' + str(peopleIndex.showScore())  + '\n'
    writeData(file, bot.data)

#Function to read all People data from a file
def readPeople():
    people = bot.people
    data = bot.data
    for dataIndex in data:
        line = dataIndex.split()
        if line[0] == 'p':
            people.append(person(line[1], int(line[2])))

# Counting Class
class count:
    #Initializing function
    def __init__(self, cur_channel, number, highscore): 
        self.cur_channel = str(cur_channel)
        self.number = int(number)
        self.highscore = highscore
    #Returns the value of the count
    def displayCount(self):
        return self.number
    #Returns the channel of the count
    def displayChannel(self):
        return self.cur_channel
    #Sets the value of the count
    def setCount(self, number):
        self.number = number
    #Adds 2 to the value of the count
    def addCount(self):
        self.number += 1
    #Sets the value of the count to zero
    def resetCount(self):
        self.number = 0
    #Sets the highscore
    def setHigh(self, highscore):
        self.highscore = highscore
    #Returns the highscore
    def displayHigh(self):
        return self.highscore

# Person Class
class person:
    #Initializing function
    def __init__(self, name, countScore):
        self.countScore = countScore
        self.name = name
    #Returns the name
    def showName(self):
        return self.name
    #Add to countScore
    def addScore(self):
        self.countScore += 1
    #Resets countScore
    def resetScore(self):
        self.countScore = 0
    #Returns countScore
    def showScore(self):
        return self.countScore

bot.counts = []                                             #The list of all counts
bot.people = []
bot.previous = ''
bot.data = readData('server.txt')

# Command Definitions
#Start Count Command
@bot.command(name='sc', help='Starts the count for the current channel')
@commands.has_any_role(  "Protectors of the Count", "Knights of the Count")
async def startCount(ctx):
    if (searchList(ctx.channel, bot.counts) == NULL):
        bot.counts.append(count(ctx.channel, 0, 0))             #Adding the current channel to the list of counting channels
        print(f'\nA count has been started')                    
        channel = ctx.channel
        await channel.send('A count has begun!')                #Sending that a count has started
    else:
        await ctx.channel.send('There is already a count here')
    await saveCounts()

#Check Count Command
@bot.command(name='cc', help='Displays the count for the current channel')
async def check_count(ctx):
    current = searchList(ctx.channel, bot.counts)           #Count variable for the current channel
    if (current != NULL):
        count = current.displayCount()                          #The value of the count
        print(f'\nThe count is: ' + (str(count)))
        await ctx.send('The current count is ' + (str(count)) + '. The next number is ' + (str(count+1)))  #Sending the count to the channel
    else:
        await ctx.send('There is no count here!')

#Prints the current highscore of the channel
@bot.command(name='hs', help='Prints the highscore for the channel')
async def returnHighScore(ctx):
    channel = ctx.channel
    current = searchList(channel, bot.counts)
    highscore = current.displayHigh()
    await channel.send('The highscore is ' + str(highscore))

#Saves counts to file
@bot.command(name='saveCount', help='Manual save of the current scores and counts')
@commands.has_any_role(  "Protectors of the Count", "Knights of the Count")
async def saveCounts():
    writeCounts('server.txt')

#Loads counts from file
@bot.command(name='loadCount', help='Manual load of counts and scores')
@commands.has_any_role(  "Protectors of the Count", "Knights of the Count")
async def loadCounts():
    readCounts()

#Saves people to file
@bot.command(name='savePeople', help='Manual save of the current people and their counts')
@commands.has_any_role(  "Protectors of the Count", "Knights of the Count")
async def savePeople():
    writePeople('server.txt')

#Loads people from file
@bot.command(name='loadPeople', help='Manual load of people and their counts')
@commands.has_any_role(  "Protectors of the Count", "Knights of the Count")
async def loadPeople():
    readPeople()

#Displays authors current score
@bot.command(name='ps', help='Prints your current correct number score')
@commands.has_any_role(  "Protectors of the Count", "Knights of the Count")
async def showPersonalScore(ctx):
    author = searchName(ctx.author, bot.people)
    score = author.showScore()
    await ctx.channel.send('Your current consecutive counts is ' + str(score))

# Event detection systems
#Triggers upon bot being ready
@bot.event
async def on_ready():
    await loadCounts()
    await loadPeople()
    print(f'{bot.user.name} has connected to Discord!')

#Triggers upon a message being sent
@bot.event
async def on_message(message):
    text = message.content                                  #Text of the message
    author = message.author
    currentPerson = searchName(author, bot.people)
    if author == bot.user:                                  #Confirming the author isn't a bot
        return
    elif len(bot.counts) != 0:
        current = searchList(message.channel, bot.counts)   #Current is the count for the channel
        if currentPerson == NULL:
            bot.people.append(person(str(author), 0))
            currentPerson = searchName(author, bot.people)
        if text.isnumeric() & (current != NULL):            #Making sure current is in the list and message is a number
            if int(text) == (current.displayCount() + 1):   #Confirming its the correct number
                currentPerson.addScore()
                await checkCons(currentPerson.showScore(), author)
                if (current.displayCount() + 1) > current.displayHigh():    #Checking to see if the new count is a new highscore
                    current.setHigh(current.displayCount() + 1)
                    await message.add_reaction('☑️')
                else:
                    await message.add_reaction('✅')
                current.addCount()
                #await message.channel.send(current.displayCount())  #Sending the new number
            else:
                currentPerson.resetScore()
                current.resetCount()                        #Reseting the count upon a mess up of it
                await checkCons(currentPerson.showScore(), author)
                await message.add_reaction('❌')
                await message.channel.send('You broke the count!')  #Sending the count has been broken
        elif (not (text.isnumeric()) )& (not (text.startswith('sc!', 0, 4))):   #Checks to see if it is not numeric or is not a command
            current.resetCount()                            #Reseting the count upon a mess up of it
            currentPerson.resetScore()
            await checkCons(currentPerson.showScore(), author)
            await message.add_reaction('❌')
            await message.channel.send('Only Count here please!')   #Sending the count has been broken
    await saveCounts()
    await savePeople()
    await bot.process_commands(message)

#Search List function
def searchList(element, list):
    element = str(element)
    for listIndex in list:
        if listIndex.displayChannel() == element:
            return listIndex
    return NULL

#Search Names function
def searchName(element, list):
    element = str(element)
    for listIndex in list:
        if listIndex.showName() == element:
            return listIndex
    return NULL

#Detect Consecutive counts and change role function
async def checkCons(number, user):
    roleLow = discord.utils.get(user.guild.roles, name="Bottom Tier Counters")
    roleMid = discord.utils.get(user.guild.roles, name="Middle Tier Counters")
    roleHigh = discord.utils.get(user.guild.roles, name="Top Tier Counters")
    if (number >= 10) & (roleLow in user.roles):
        await user.remove_roles(roleLow)
        await user.add_roles(roleMid)
    elif (number == 50) & (roleMid in user.roles):
        await user.remove_roles(roleMid)
        await user.add_roles(roleHigh)
    if (number == 0):
        if roleMid in user.roles:
            await user.remove_roles(roleMid)
            await user.add_roles(roleLow)
        elif roleHigh in user.roles:
            await user.remove_roles(roleHigh)
            await user.add_roles(roleMid)

#Running the bot
bot.run(TOKEN)