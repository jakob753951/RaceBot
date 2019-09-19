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


bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['prefix']), description='A good alternative bot', pm_help=True)


def log(message):
	formattedMessage = str(datetime.now())[:-7] + ":  " + message
	print(formattedMessage, flush=True)
	today = date.today()
	fileName = "{}/{}.log".format(config['log_dir'], today.strftime("%Y-%m-%d"))
	with open(fileName, 'a+') as f:
		f.write(formattedMessage + "\n")


@bot.event
async def on_ready():
	log('Connected!')
	log('Username: ' + bot.user.name)
	log('ID: ' + bot.user.id)
	log('====================')

@bot.event
async def on_message_edit(before, after):
	#if message is a DM
    if(after.channel.is_private):
        log("""Direct message>{}: "{}" --> "{}" """.format(str(after.author), before.content, after.content))
	#if message is in server
    else:
        log("""{}>{}>{}: "{}" --> "{}" """.format(str(after.server), str(after.channel), str(after.author), before.content, after.content))

@bot.event
async def on_message(message):
	#if the author is not the bot
	if message.author != bot.user:
		#Log message
		#if message is a DM
		if(message.channel.is_private):
			log("Direct message>" + str(message.author) + ": \"" + message.content + "\"")
		#if message is in server
		else:
			log(str(message.server) + ">" + str(message.channel) + ">" + str(message.author) + ": \"" + message.content + "\"")

	await bot.process_commands(message)

@bot.command(pass_context=True)
async def isdown(ctx):
	print("noice")
	r = requests.get(config['iracing_url'])
	await bot.say(config["iracing_status_down"] if r.url.split('/')[3] == 'maintenance' else config["iracing_status_up"])

bot.run(config['token'])