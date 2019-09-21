import os
import codecs
import json
import re
import random
import asyncio
import time
from datetime import datetime
from datetime import date

import discord
from discord.ext import commands
from discord.utils import get

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
	with codecs.open(fileName, 'a+', 'utf-8') as f:
		f.write(formattedMessage + "\n")

def is_owner():
    def predicate(ctx):
        return ctx.message.author.id == config["owner_id"]
    return commands.check(predicate)

def is_dev():
    def predicate(ctx):
        return ctx.message.guild.get_role(config["dev_role"]) in ctx.message.author.roles
    return commands.check(predicate)

def is_bot_channel():
    def predicate(ctx):
        return ctx.message.channel.id == config["bot_channel_id"]
    return commands.check(predicate)

def has_name():
    def predicate(ctx):
        return ctx.message.guild.get_role(config["has_name_role"]) in ctx.message.author.roles
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
    if isinstance(after.channel, discord.abc.PrivateChannel):
        log("""Direct message>{}: "{}" --> "{}\"""".format(str(after.author), before.content, after.content))
	#if message is in server
    else:
        log("""{}>{}>{}: "{}" --> "{}\"""".format(str(after.guild), str(after.channel), str(after.author), before.content, after.content))

@bot.event
async def on_message(message):
	#Log the message
	if isinstance(message.channel, discord.abc.PrivateChannel):
		log("Direct message>" + str(message.author) + ": \"" + message.content + "\"")
	else:
		log(str(message.guild) + ">" + str(message.channel) + ">" + str(message.author) + ": \"" + message.content + "\"")
	
	if message.channel == get(bot.get_all_channels(), id=config["intro_channel_id"]):
		match = re.findall(r'(?<=Name:).*', message.content, re.IGNORECASE)[0].strip()
		if match != None:
			await message.author.edit(nick=match)

			hasName = message.guild.get_role(config["has_name_role"])
			newRoles = message.author.roles
			if hasName not in newRoles:
				newRoles.append(hasName)
				await message.author.edit(roles=newRoles)
				

	#allow the bot to process the message as a command
	await bot.process_commands(message)

@is_bot_channel()
@bot.command(pass_context=True, brief="Checks if iRacing is down for maintenance")
async def isdown(ctx):
	"""
	Sends a request to iRacing, and if it's redirected to the maintenance page, we know it's down

	Usage:
	.isdown
	"""
	r = requests.get(config['iracing_url'])
	await ctx.send(config["isdown_down"] if r.url.split('/')[3] == 'maintenance' else config["isdown_up"])

@is_bot_channel()
@bot.command(pass_context=True, brief="Mentions the user when iRacing is back online")
async def mentionwhenup(ctx, user = config["owner_id"]):
	"""
	Mentions the user when iRacing is back online
	You can specify which user to mention, if you are a dev

	Usage:
	.mentionwhenup
	.mentionwhenup [User]
	"""
	if not is_owner():
		user = ctx.message.author
	else:
		user = get(bot.get_all_members(), id=user)

	while True:
		r = requests.get(config['iracing_url'])
		if r.url.split('/')[3] != 'maintenance':
			break
		time.sleep(config["mentionwhenup_interval"])
	await ctx.send(config["mentionwhenup_message"].format(user.mention))

@is_owner()
@bot.command(pass_context=True, brief="Shuts the bot down")
async def shutdown(ctx):
	"""
	Shuts the bot down
	Requires "Dev" role
	Usage: .shutdown
	"""
	await bot.logout()
	

bot.run(os.environ['TOKEN'])