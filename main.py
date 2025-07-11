import asyncio
import os

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Important for reading user messages

bot = commands.Bot(command_prefix='!', intents=intents)

# Channel ID where submissions will be posted
SUBMISSION_CHANNEL_ID = 1392968357942399017  # Replace with your actual channel ID

@bot.command(name="form")
async def form(ctx):
    questions = [
        "What's your name?",
        "Is Kima Gingi?",
        "Why?",
    ]
    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Let's begin the form. Please answer the following questions:")

    for question in questions:
        await ctx.send(question)
        try:
            msg = await bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Cancelling form.")
            return
        answers.append(msg.content)

    # Format the submission
    submission = "\n".join(f"**{q}** {a}" for q, a in zip(questions, answers))

    # Send it to the designated channel
    channel = bot.get_channel(SUBMISSION_CHANNEL_ID)
    if channel:
        await channel.send(f"**New Form Submission from {ctx.author.mention}:**\n{submission}")
        await ctx.send("Thanks! Your form has been submitted.")
    else:
        await ctx.send("Error: Submission channel not found.")

bot.run(os.environ["DISCORD_TOKEN"])

