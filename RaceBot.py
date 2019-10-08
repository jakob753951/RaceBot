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
import db
import scrape

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
	fileName = f"{config['log_dir']}/{today.strftime('%Y-%m-%d')}.log"
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
        log(f"""Direct message>{str(after.author)}: "{before.content}" --> "{after.content}\"""")
	#if message is in server
    else:
        log(f"""{str(after.guild)}>{str(after.channel)}>{str(after.author)}: "{before.content}" --> "{after.content}\"""")

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

@is_bot_channel()
@bot.command(pass_context=True, brief="Get licenses for the user")
async def licenses(ctx, id = None):
	"""
	Gets the licenses for a specific user

	Usage:
	.licenses [UserId]
	"""

	msg = await ctx.send("`Fetching data...`")
	
	
	if id is None:
		id = db.getCustFromDiscord(ctx.author.id)

	if str(id).replace('!', '').startswith("<@"):
		id = db.getCustFromDiscord(int(str(id).replace('!', '')[2:-1]))

	if id is None:
		await msg.edit(content="`No id set for this user`")
		return

	licenseNames = ["Oval", "Road", "Dirt Oval", "Dirt Road"]

	licenses = scrape.getLicenses(id)
	username = licenses["username"]
	try:
		finalText = f"```licenses for {username}:\n"
		for i in range(len(licenseNames)):
			finalText += licenseNames[i] + ":\n\t"
			finalText += licenses["safetyRatings"][i] + "\n\t"
			finalText += licenses["iRatings"][i] + "\n\n"
		finalText += "```"

		await msg.edit(content=finalText)
	except:
		await msg.edit(content=f"Could not get data for user {id}")

@bot.command(pass_context=True, brief="Shuts the bot down")
async def createuser(ctx, custid, discordId = None):

	if discordId is None:
		discordId = ctx.author.id
	
	if isinstance(discord, str):
		discordId = int(discordId.translate({ord(i): None for i in '<@!>'}))
	
	altered = db.createUser(discordId, custid)

	if altered is 0:
		await ctx.send("User not created. that Customer ID, or Discord user has already been assigned")
	else:
		await ctx.send("User successfully created!")

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