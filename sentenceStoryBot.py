import os
import time
import random
import math

import discord
from discord.ext import commands, tasks

client = commands.Bot(command_prefix = '/')

collectingTime = 30
votingTime = 30
minimumAmountOfLines = 3


channels = {'storysuggestions': client.get_channel('820793577981345823'), 'storyvoting': client.get_channel('820793625209208863'), 'storyresults': client.get_channel('820793645581074432')}#Hier misschien dingus toevoegen
print(channels)


modeStartTime = time.time()
endTime = time.time() + 60*5#int(input('How many minutes should the program last? '))
timeLeftWarning = 3*60
mode = 'collecting'
newLines = []
votes = {}
totalStory = []

@client.event
async def on_ready():
    print('Starting')
    
    checkMode.start()
    

@tasks.loop(seconds=5)
async def checkMode():
    global mode
    global modeStartTime
    global newLines
    global collectingTime
    global votingTime
    global channels
    global totalStory
    global votes
    global minimumAmountOfLines
    
    if mode == 'collecting':
        
        if len(newLines) >= minimumAmountOfLines and (time.time() - modeStartTime) >= collectingTime:
            
            
            await channels['storyvoting'].send("Now voting for new lines:")
            
            random.shuffle(newLines)
            
            votes = {}
            for line in newLines:
                votes[line] = [0, 0]
            
            print('Now voting', votes)
            for line in newLines:
                await channels['storyvoting'].send(line)
            
            
            modeStartTime = time.time()
            mode = 'voting'
            
        else:
            print('Still collecting lines (' + str((time.time() - modeStartTime))+' seconds).')
            print('Current lines: ', newLines)
            
    if mode == 'voting':
        
        if (time.time() - modeStartTime) >= votingTime:
            
            for key in votes:
                votes[key] = votes[key][0] - votes[key][1]
            
            print('Voting results', votes)
            
            bestLine = ""
            highestVotes = -100000000
            
            for key in votes:
                if votes[key] > highestVotes:
                    highestVotes = votes[key]
                    bestLine = key
            
            totalStory.append(bestLine)
            await channels["storyresults"].send(bestLine)
            await channels["storysuggestions"].send("Precise voting results: " + str(votes))
            
            newLines = []
            modeStartTime = time.time()
            mode = 'collecting'
            
            if (endTime - time.time()) <=0:
                mode = 'end'
                print('Ended program.')
            elif (endTime - time.time()) <= timeLeftWarning:
                await channels['storysuggestions'].send("The story will end soon, " + str(math.round((endTime - time.time())/60, 1)) + ' minutes left. At most ' + str(math.ceil((endTime - time.time())/(votingTime + collectingTime))) + ' rounds left.')
            
            
        else:
            print('Still collecting votes (' + str((time.time() - modeStartTime))+' seconds).')



@client.event
async def on_message(message):
    global newLines
    global channels
    global mode
    
    channels[str(message.channel)] = message.channel
    
    #print(mode == 'collecting', (str(message.channel) == 'storysuggestions'),len(message.content) < 140, (not message.author == client.user))
    if (str(message.channel) == 'storysuggestions') and len(message.content) < 140 and (not message.author == client.user):
        newLines.append(message.content)
        print('appended line:', message.content)
    elif (str(message.channel) == 'storyvoting') and not (message.content == "Now voting for new lines:"):
        await message.add_reaction("✅")
        await message.add_reaction("❌")

@client.event
async def on_reaction_add(reaction, user):
    global votes
    
    if (str(reaction.message.content) in newLines) and (mode == 'voting'):
        print('Added reaction', reaction.message.content, type(reaction.message.content), reaction.emoji)
        if reaction.emoji == "✅":            
            votes[reaction.message.content][0] = reaction.count
        elif reaction.emoji == "❌":
            votes[reaction.message.content][1] = reaction.count


    


client.run()
