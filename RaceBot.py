import os
import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from datetime import date
import random
import json
import requests


#read token from config.json
with open('resources/config.json', 'r') as configFile:
	config = json.loads(configFile.read().replace('\n', ''))


bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['bot_prefix']), description=config['bot_description'], pm_help=True)


def log(message):
	formattedMessage = str(datetime.now())[:-7] + ":  " + message
	print(formattedMessage, flush=True)
	today = date.today()
	if not os.path.isdir(config['log_dir']):
		os.mkdir(config['log_dir'])
	fileName = "{}/{}.log".format(config['log_dir'], today.strftime("%Y-%m-%d"))
	with open(fileName, 'a+') as f:
		f.write(formattedMessage + "\n")

def is_me():
    def predicate(ctx):
        return ctx.message.author.id == 85309593344815104
    return commands.check(predicate)

@bot.event
async def on_ready():
	log('Connected!')
	log('Username: ' + bot.user.name)
	log('ID: ' + str(bot.user.id))
	log('====================')

@bot.event
async def on_message_edit(before, after):
	#if message is a DM
    if(isinstance(after.channel, discord.abc.PrivateChannel)):
        log("""Direct message>{}: "{}" --> "{}" """.format(str(after.author), before.content, after.content))
	#if message is in server
    else:
        log("""{}>{}>{}: "{}" --> "{}" """.format(str(after.guild), str(after.channel), str(after.author), before.content, after.content))

@bot.event
async def on_message(message):
	if(isinstance(message.channel, discord.abc.PrivateChannel)):
		log("Direct message>" + str(message.author) + ": \"" + message.content + "\"")
	else:
		log(str(message.guild) + ">" + str(message.channel) + ">" + str(message.author) + ": \"" + message.content + "\"")
	
	#allow the bot to process the message as a command
	await bot.process_commands(message)

@bot.command(pass_context=True, brief="Checks if iRacing is down for maintenance")
async def isdown(ctx):
	"""
	Sends a request to iRacing, and if it's redirected to the maintenance page, we know it's down

	Usage: .isdown
	"""
	r = requests.get(config['iracing_url'])
	await ctx.send(config["iracing_status_down"] if r.url.split('/')[3] == 'maintenance' else config["iracing_status_up"])

@bot.command()
@commands.has_role("Dev")
async def shutdown(brief="Shuts the bot down"):
	"""
	Shuts the bot down
	Requires "Dev" role
	Usage: .shutdown
	"""
	await bot.logout()
	

bot.run(os.environ['TOKEN'])