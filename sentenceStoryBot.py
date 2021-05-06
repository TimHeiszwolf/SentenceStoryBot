import os
import time
import random
import math

import discord
from discord.ext import commands, tasks

client = commands.Bot(command_prefix = '/')

channels = {'storysuggestions': client.get_channel('820793577981345823'), 'storyvoting': client.get_channel('820793625209208863'), 'storyresults': client.get_channel('820793645581074432'), 'storybotmessages':client.get_channel('820793577981345823')}# This currently doesn't work. A work around is sending a messege into each channel before the start of the 
print(channels)

collectingTime = 60# The minimum about of time (in seconds) the suggestion/collection phase lasts.
votingTime = 60# The amount of time (in seconds) that a vote lasts.
minimumAmountOfLines = 3# Minimum number of lines needed before a vote can start.
modeStartTime = time.time()
endTime = time.time() + 60*5# How many seconds the bot will last.
timeLeftWarning = 4*60# How many seconds before the end warnings will be given.

mode = 'collecting'
newLines = []
votes = {}
totalStory = []


"""

- Edits don't work
- Slow mode is on.
- Max 140 characters
- While voting it doesn't take suggestions
- 

"""

@client.event
async def on_ready():
    print('Starting')
    
    checkMode.start()
    

@tasks.loop(seconds=5)# Loops every 5 seconds, might want to make quicker (or longer).
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
        # If the minimum amount of lines (and time) have been collected then inform everybody that voting has started and start the voting procces.
            await channels['storyvoting'].send("**Now voting for new lines:**")
            
            random.shuffle(newLines)# Shuffle the lines to make the procces fair.
            
            votes = {}# Create the data structure for collecting the votes.
            for line in newLines:
                votes[line] = [0, 0]# The structure is a dictonairy with the line itself as the key, the element inside is a list with the number of upvotes and downvotes.
            
            print('Now voting', votes)
            for line in newLines:# Yeet all the lines into the voting chat.
                await channels['storyvoting'].send(line)
            
            
            modeStartTime = time.time()
            mode = 'voting'
            
        else:
        # If the time has not yet passed (or not enough lines have been gathered, then do nothing (except inform the admin).
            print('Still collecting lines (' + str((time.time() - modeStartTime))+' seconds).')
            await channels['storybotmessages'].send('Still collecting lines (' + str((time.time() - modeStartTime))+' seconds).')
            #print('Current lines: ', newLines)
            #await channels['storybotmessages'].send('Current lines: ' + str(newLines))
            
    if mode == 'voting':
        
        if (time.time() - modeStartTime) >= votingTime:
        # If the voting time is over then we start counting and proccesing the votes.
            
            for key in votes:
            # For each suggestion calculate the net vote (in this case just the sum of the postive and negative votes).
                votes[key] = votes[key][0] - votes[key][1]
            
            print('Voting results', votes)
            await channels['storybotmessages'].send('Voting results' + str(votes))
            
            bestLine = ""
            highestVotes = -100000000
            
            for key in votes:
                if votes[key] >= highestVotes:
                # If the number of votes is higher (or equal) to the current highest votes then that becomes the result. If multiple suggestions recieve the same amount of votes then 
                    highestVotes = votes[key]
                    bestLine = key
            
            totalStory.append(bestLine)# Appends the best line to the total story and puts it in the results chat.
            await channels["storyresults"].send(bestLine)
            await channels["storysuggestions"].send("Precise voting results: " + str(votes))# Sends the precize voting results and starts accepting new suggestions again.
            await channels["storysuggestions"].send("**You can start sending suggestions now again.**")
            newLines = []
            modeStartTime = time.time()
            mode = 'collecting'
            
            if (endTime - time.time()) <=0:
            # If the time is up the bot stops.
                mode = 'end'
                
                for chan in ['storyvoting', 'storysuggestions', 'storyresults', 'storybotmessages']:
                # The bot sends one final message to their channels and then does nothing for the rest of its life.
                    await channels[chan].send("**The story is now finished, thank you for playing and I hope you enjoyed Lunafest!**")
                
                print('Ended program.')
                await channels['storybotmessages'].send('Ended program')
                print(str(totalStory))
                await channels['storybotmessages'].send(str(totalStory))
                
            elif (endTime - time.time()) <= timeLeftWarning:
            # If there is little time left it sends a warning.
                await channels['storysuggestions'].send("The story will end soon, " + str(round((endTime - time.time())/60, 1)) + ' minutes left. At most ' + str(math.ceil((endTime - time.time())/(votingTime + collectingTime))) + ' rounds left.')
            
        else:
        # If the time for voting is not yet finished then continue.
            print('Still collecting votes (' + str((time.time() - modeStartTime))+' seconds).')
            await channels['storybotmessages'].send('Still collecting votes (' + str((time.time() - modeStartTime))+' seconds).')



@client.event
async def on_message(message):
    global newLines
    global channels
    global mode
    
    channels[str(message.channel)] = message.channel# A hacky way to make the bot learn the channel names. You can do this by sending a message into each of the channels.
    
    #print(mode == 'collecting', (str(message.channel) == 'storysuggestions'),len(message.content) < 140, (not message.author == client.user))
    if mode == 'voting' and (str(message.channel) == 'storysuggestions') and (not message.author == client.user):
        await message.reply("Currently busy voting (and thus not accepting suggestions). Please vote and wait.")# Informs the user that their message was not proccesed due the bot being in voting mode.
        
    elif (str(message.channel) == 'storysuggestions') and len(message.content) > 140 and (not message.author == client.user):
        await message.reply("Your suggestion is longer than 140 characters. Please remove " + str(len(message.content) - 140) + " characters.")# Informs the user that their message was not proccesed due to length.
        
    elif (str(message.channel) == 'storysuggestions') and len(message.content) <= 140 and (not message.author == client.user):
        newLines.append(message.content)
        await message.add_reaction("☑️")# Gives feedback to the user that the request was proccesed.
        #print('appended line:', message.content)
        
    elif (str(message.channel) == 'storyvoting') and not (message.content == "**Now voting for new lines:**"):
    
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        #await message.add_reaction("🅾️")

@client.event
async def on_reaction_add(reaction, user):
    global votes
    
    if (str(reaction.message.content) in newLines) and (mode == 'voting'):
    
        #print('Added reaction', reaction.message.content, type(reaction.message.content), reaction.emoji)
        if reaction.emoji == "✅":           
            votes[reaction.message.content][0] = reaction.count
            
        elif reaction.emoji == "❌":
            votes[reaction.message.content][1] = reaction.count

client.run("")
