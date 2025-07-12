import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Only needed if you're reading user messages

bot = commands.Bot(command_prefix="!", intents=intents)

# Your channel IDs
FORM_TRIGGER_CHANNEL_ID = 1393370417334325253  # The channel where the button lives
SUBMISSION_CHANNEL_ID = 1393214835193286678   # The channel where the form results go


# Define the modal form
class ApplicationForm(discord.ui.Modal, title="Application Form"):
    name = discord.ui.TextInput(label="What's your name?", placeholder="John Doe")
    is_kima_gingi = discord.ui.TextInput(label="Is Kima Gingi?", placeholder="Yes/No", style=discord.TextStyle.short)
    reason = discord.ui.TextInput(label="Why?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        submission_channel = bot.get_channel(SUBMISSION_CHANNEL_ID)
        if submission_channel:
            embed = discord.Embed(title="New Form Submission", color=discord.Color.green())
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="Name", value=self.name.value, inline=False)
            embed.add_field(name="Is Kima Gingi?", value=self.is_kima_gingi.value, inline=False)
            embed.add_field(name="Why?", value=self.reason.value, inline=False)
            await submission_channel.send(embed=embed)
            await interaction.response.send_message("✅ Your form was submitted successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Submission channel not found.", ephemeral=True)


# Define the button
class ApplicationButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view (survives bot restart)

    @discord.ui.button(label="Apply Now", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationForm())


@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    # Send the persistent button once if it doesn't exist yet (you can control this manually)
    channel = bot.get_channel(FORM_TRIGGER_CHANNEL_ID)
    if channel:
        await channel.send(
            "**Want to apply? Click below to open the form.**",
            view=ApplicationButtonView()
        )
    else:
        print("⚠️ Form trigger channel not found!")

    # Register the persistent view (important after restarts)
    bot.add_view(ApplicationButtonView())

bot.run(os.environ["DISCORD_TOKEN"])