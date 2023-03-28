import discord
import random
import Levenshtein
import json
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Define file paths
FLAG_FILE = "flags.txt"
DATA_FILE = "data.json"

# Load flags into dictionary
flags = {}
with open(FLAG_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue  # skip empty lines
        parts = line.split(" : ")
        flag = parts[0]
        points = int(parts[1]) if len(parts) > 1 else 0  # set points to 0 if not present
        help_message = parts[2] if len(parts) > 2 else ""  # set help message to empty string if not present
        flags[flag] = (points, help_message)

# Load user data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {}

# Define functions
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def update_user(user_id, flag):
    if user_id not in data:
        data[user_id] = {"completed_flags": [], "total_points": 0}
    if flag not in data[user_id]["completed_flags"]:
        data[user_id]["completed_flags"].append(flag)
        data[user_id]["total_points"] += flags[flag][0]
        save_data()

@bot.command()
async def flag(ctx, flag=None, option=None):
    if flag is None:
        await ctx.send("Please provide a flag to submit.")
        return
    user_id = str(ctx.author.id)
    if flag in flags:
        if option == "help":
            await ctx.send(flags[flag][1])
        elif flag not in data.get(user_id, {}).get("completed_flags", []):
            update_user(user_id, flag)
            await ctx.message.delete()
            await ctx.send(f"{ctx.author.mention} Correct flag!")
        else:
            await ctx.message.delete()
            await ctx.send(f"Sorry, {ctx.author.mention}, you have already submitted that flag, keep hunting")
    else:
        await ctx.send(f"{ctx.author.mention} Incorrect flag!")

@bot.command()
async def leaderboard(ctx):
    sorted_data = sorted(data.items(), key=lambda x: x[1]["total_points"], reverse=True)
    message = "Leaderboard:\n"
    for i, (user_id, user_data) in enumerate(sorted_data):
        user = await bot.fetch_user(user_id)
        message += f"{i+1}. {user.name}: {user_data['total_points']} points\n"
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def flaghelp(ctx, flag_num=None):
    if flag_num is None:
        await ctx.send("Please provide a flag number to get help for.")
        return
    with open(FLAG_FILE, "r") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if i == int(flag_num):
                parts = line.split(" : ")
                help_message = parts[2] if len(parts) > 2 else ""  # set help message to empty string if not present
                await ctx.send(help_message)
                return
    await ctx.send(f"Flag {flag_num} not found.")  # if the flag number is not found, send an error message


bot.run('')
