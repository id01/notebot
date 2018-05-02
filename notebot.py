#!/usr/bin/python3

# Import libs
import os, glob
from base64 import b64encode, b64decode
# Import discord libs
import discord
import asyncio
# Import leveldb libs
import plyvel

# Configuration
helptext = '''Commands are:
!write [name] [text] -> Writes [text] to a note [name]
!append [name] [text] -> Appends [text] to a note [name]
!read [name] -> Prints note [name]
!readall -> Prints all notes
!pop [name] -> Prints and removes note [name]
!del [name] -> Removes note [name]
''' # Help menu text
mychannel = 'ctf-notes' # Discord channel to be active in
mytoken = 'NDQxMDU2NDY3MzgzMjIyMjcy.Dcqtjg.zgSc8wwiyMyW045S5OI7O3OCZmA' # Discord token
db = plyvel.DB('notes/', create_if_missing=True) # Compression is integrated

# Init client
client = discord.Client()

# Write note given user-specified name and text to write
def note_write(name, text):
	# Input validation
	if len(name) > 32:
		raise ValueError("Note name too long")
	if len(text) == 0 or len(name) == 0:
		raise ValueError("Cannot write empty note")
	# Put into database and log
	db.put(name.encode('utf-8'), text.encode('utf-8'))

# Append to note given user-specified name and text to append
def note_append(name, text):
	note_write(name, note_read(name) + '\n' + text)

# Read note given user-specified name
def note_read(name):
	# Input validation
	if len(name) > 32:
		raise ValueError("Note name too long")
	# Get value from database and return
	text = db.get(name.encode('utf-8'), None)
	if text == None:
		raise ValueError("No such note")
	return text.decode('utf-8')

# Read all notes
def note_readall():
	# Init tosend
	tosend = ""
	# Iterate through database reading everything and return
	for name, text in db:
		tosend += "\n---------------------------------\nNote '%s':\n%s\n\n" % (name.decode('utf-8'), text.decode('utf-8'))
	return tosend

# Pop note given user-specified name
def note_pop(name):
	# Read and delete
	res = note_read(name)
	db.delete(name.encode('utf-8'))
	return res

# Delete note given user-specified name and username
def note_del(name):
	# Input validation
	if len(name) > 32:
		raise ValueError("Note name too long")
	# Delete
	db.delete(name.encode('utf-8'))

# When ready do this
@client.event
async def on_ready():
	print('Logged in as (%s, %s)' % (client.user.name, client.user.id))

# Upon every message
@client.event
async def on_message(message):
	if str(message.channel) == mychannel:
		msgsplit = message.content.rstrip(' ').split(' ')
		try:
			name = msgsplit[1].lower()
		except IndexError:
			pass

		if msgsplit[0] == '!write':
			try:
				note_write(name, ' '.join(msgsplit[2:]))
				reply = '%s, added %s' % (message.author, name)
				print("%s wrote note '%s'" % (message.author, name))
			except (UnboundLocalError, IndexError):
				reply = "Usage: !write [name] [text]"
			except ValueError as ex:
				reply = str(ex)
		elif msgsplit[0] == '!append':
			try:
				note_append(name, ' '.join(msgsplit[2:]))
				reply = '%s, edited %s' % (message.author, name)
				print("%s edited note '%s'" % (message.author, name))
			except (UnboundLocalError, IndexError):
				reply = "Usage: !append [name] [text]"
			except ValueError as ex:
				reply = str(ex)
		elif msgsplit[0] == '!read':
			try:
				res = note_read(name)
				reply = '%s, %s reads:\n%s' % (message.author, name, res)
				print("%s accessed note '%s'" % (message.author, name))
			except (UnboundLocalError, IndexError):
				reply = "Usage: !read [name]"
			except ValueError as ex:
				reply = str(ex)
		elif msgsplit[0] == '!readall':
			res = note_readall()
			if res:
				reply = "%s, printing ALL notes:\n\n%s" % (message.author, res)
			else:
				reply = "%s, no notes found." % message.author
			print("%s printed ALL notes" % message.author)
		elif msgsplit[0] == '!pop':
			try:
				res = note_pop(name)
				reply = '%s, %s has been removed. It read:\n%s' % (message.author, name, res)
				print("%s popped '%s'" % (message.author, name))
			except (UnboundLocalError, IndexError):
				reply = "Usage: !pop [name]"
			except ValueError as ex:
				reply = str(ex)
		elif msgsplit[0] == '!del':
			try:
				res = note_del(name)
				reply = '%s, %s has been removed.' % (message.author, name)
				print("%s deleted '%s'" % (message.author, name))
			except (UnboundLocalError, IndexError):
				reply = "Usage: !del [name]"
		elif msgsplit[0] == '!help':
			reply = helptext
		else:
			reply = None

		if reply:
			await client.send_message(message.channel, reply)

# Run bot
client.run(mytoken)