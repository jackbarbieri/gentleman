import discord
import helpers, interpreter
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os
import multiprocessing as mp

load_dotenv()

token = os.getenv("TOKEN")

f = open("default.fs", 'r')
default_env = f.read()
f.close()

interpreters = mp.Manager().dict()

def forth_run(id, code, q = None):
    forth = interpreters[id]
    stdout = forth.run(helpers.tokenize(code))
    interpreters[id] = forth
    if q != None:
        q.put(stdout)
class Bot(discord.Client):
    async def on_ready(self):
        print('logged in')
    async def on_message(self, message):
        command = message.content
        if command != '' and command[0] == '$':
            if message.author.id not in interpreters:
                interpreters[message.author.id] = interpreter.Interpreter()
                forth_run(message.author.id, default_env)
            if command == '$reset':
                interpreters[message.author.id] = interpreter.Interpreter()
                forth_run(message.author.id, default_env)
                return
            q = mp.Queue()
            p = mp.Process(target=forth_run, args= (message.author.id, command[1:], q))
            p.start()
            p.join(3)
            if p.is_alive():
                p.terminate()
                await message.reply("Error: timeout")
            else:
                stdout = interpreters[message.author.id].interpretState.stdout
                if stdout != '':
                    await message.reply(stdout)
intents = discord.Intents.all()
client = Bot(intents=intents)
client.run(token)