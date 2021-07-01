# bot.py
from asyncio.windows_events import NULL
import os
import random

from discord.ext import commands

from dotenv import load_dotenv

# Loading the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Counting Class
class count:
    #Initializing function
    def __init__(self, cur_channel, number): 
        self.cur_channel = cur_channel
        self.number = number
    #Returns the value of the count
    def displayCount(self):
        return self.number
    #Returns the channel of the count
    def displayChannel(self):
        return self.cur_channel
    #Adds 2 to the value of the count
    def addCount(self):
        self.number += 2
    #Sets the vlue of the count to zero
    def resetCount(self):
        self.number = 0

# Setting the command prefix
bot = commands.Bot(command_prefix='sc!')

bot.counts = []                                             #The list of all counts

# Command Definitions
#Start Count Command
@bot.command(name='sc', help='Starts the count for the current channel')
async def startCount(ctx):
    bot.counts.append(count(ctx.channel, 0))                #Adding the current channel to the list of counting channels
    print(f'\nA count has been started')                    
    channel = ctx.channel
    await channel.send('A count has begun!')                #Sending that a count has started

#Check Count Command
@bot.command(name='current', help='Displays the count for the current channel')
async def check_count(ctx):
    current = searchList(ctx.channel, bot.counts)           #Count variable for the current channel
    count = current.displayCount()                          #The value of the count
    print(f'\nThe count is: ' + (str(count)))
    await ctx.send('The current count is ' + (str(count)))  #Sending the count to the channel

# Event detection systems
#Triggers upon bot being ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#Triggers upon a message being sent
@bot.event
async def on_message(message):
    text = message.content                                  #Text of the message
    if message.author == bot.user:                          #Confirming the author isn't a bot
        return
    elif len(bot.counts) != 0:                              #Checking there is a count occuring
        current = searchList(message.channel, bot.counts)   #Current is the count for the channel
        if text.isnumeric() & (current != NULL):            #Making sure current is in the list and message is a number
            if int(text) == (current.displayCount() + 1):   #Confirming its the correct number
                current.addCount()
                await message.add_reaction('✅')
                channel = current.displayChannel()
                await channel.send(current.displayCount())  #Sending the new number
            else:
                channel = current.displayChannel()
                current.resetCount()                        #Reseting the count upon a mess up of it
                await message.add_reaction('❌')
                await channel.send('You broke the count!')  #Sending the count has been broken
    await bot.process_commands(message)

#Search List function
def searchList(element, list):
    for listIndex in list:
        if listIndex.displayChannel() == element:
            return listIndex
    return NULL

#Running the bot
bot.run(TOKEN)
