# bot.py
from asyncio.windows_events import NULL
import os

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
        place = findData(bot.data, str(countsIndex.displayChannel()))
        if ( place == -1 ):
            bot.data.append(str(countsIndex.displayChannel()) + ' ' + str(countsIndex.displayCount()) + ' ' + str(countsIndex.displayHigh()) + '\n')
        else:
            bot.data[place-1] = str(countsIndex.displayChannel()) + ' ' + str(countsIndex.displayCount()) + ' ' + str(countsIndex.displayHigh()) + '\n'
    writeData(file, bot.data)
    print("\nData written succesfully")

#Function to read all counts data from a file
def readCounts():
    counts = bot.counts
    data = bot.data
    for dataIndex in data:
        line = dataIndex.split()
        counts.append(count(line[0], int(line[1]), int(line[2])))
    print("\nData read succesfully")

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
        self.number += 2
    #Sets the value of the count to zero
    def resetCount(self):
        self.number = 0
    #Sets the highscore
    def setHigh(self, highscore):
        self.highscore = highscore
    #Returns the highscore
    def displayHigh(self):
        return self.highscore

bot.counts = []                                             #The list of all counts
bot.data = readData('server.txt')

# Command Definitions
#Start Count Command
@bot.command(name='sc', help='Starts the count for the current channel')
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
    count = current.displayCount()                          #The value of the count
    print(f'\nThe count is: ' + (str(count)))
    await ctx.send('The current count is ' + (str(count)) + '. The next number is ' + (str(count+1)))  #Sending the count to the channel

#Prints the current highscore of the channel
@bot.command(name='hs', help='Prints the highscore for the channel')
async def returnHighScore(ctx):
    channel = ctx.channel
    current = searchList(channel, bot.counts)
    highscore = current.displayHigh()
    await channel.send('The highscore is ' + str(highscore))

#Saves counts to file
@bot.command(name='save')
async def saveCounts():
    writeCounts('server.txt')

#Loads counts from file
@bot.command(name='load')
async def loadCounts():
    readCounts()

# Event detection systems
#Triggers upon bot being ready
@bot.event
async def on_ready():
    await loadCounts()
    print(f'{bot.user.name} has connected to Discord!')

#Triggers upon a message being sent
@bot.event
async def on_message(message):
    text = message.content                                  #Text of the message
    author = message.author
    if author == bot.user:                                  #Confirming the author isn't a bot
        return
    elif len(bot.counts) != 0:
        current = searchList(message.channel, bot.counts)   #Current is the count for the channel
        if text.isnumeric() & (current != NULL):            #Making sure current is in the list and message is a number
            if int(text) == (current.displayCount() + 1):   #Confirming its the correct number
                if (current.displayCount() + 1) > current.displayHigh():    #Checking to see if the new count is a new highscore
                    current.setHigh(current.displayCount() + 1)
                    await message.add_reaction('☑️')
                else:
                    await message.add_reaction('✅')
                current.addCount()
                channel = current.displayChannel()
                await message.channel.send(current.displayCount())  #Sending the new number
            else:
                channel = current.displayChannel()
                current.resetCount()                        #Reseting the count upon a mess up of it
                await message.add_reaction('❌')
                await message.channel.send('You broke the count!')  #Sending the count has been broken
        elif (not (text.isnumeric()) )& (not (text.startswith('sc!', 0, 4))):   #Checks to see if it is not numeric or is not a command
            channel = current.displayChannel()
            current.resetCount()                            #Reseting the count upon a mess up of it
            await message.add_reaction('❌')
            await message.channel.send('Only Count here please!')   #Sending the count has been broken
    await saveCounts()
    await bot.process_commands(message)

#Search List function
def searchList(element, list):
    element = str(element)
    for listIndex in list:
        if listIndex.displayChannel() == element:
            return listIndex
    return NULL

#Running the bot
bot.run(TOKEN)
