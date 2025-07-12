import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Only needed if you're reading user messages

bot = commands.Bot(command_prefix="!", intents=intents)

# Channel IDs
FORM_TRIGGER_CHANNEL_ID = 1393370417334325253
SELL_CHANNEL_ID = 1393553183963353231
TRADE_CHANNEL_ID = 1393553313550565426
DEST_SELL_CHANNEL_ID = 1392968357942399017
DEST_TRADE_CHANNEL_ID = 1393214835193286678
QUESTION_CHANNEL_ID = 1393260216639815710

# Store temporary form data by user ID
user_form_data = {}


# ----- MODAL FORM (Text Inputs) -----
class SellApplicationForm(discord.ui.Modal, title="פרסום בושם למכירה"):
    name = discord.ui.TextInput(label="שם הבושם", placeholder="Xerjoff Pikovaya Dama", max_length=100, required=True)
    amount = discord.ui.TextInput(label='כמות במ"ל', placeholder="95", style=discord.TextStyle.short, required=True, max_length=4)
    capacity = discord.ui.TextInput(label='מתוך כמה במ"ל', placeholder="100", style=discord.TextStyle.short, required=True, max_length=4)
    city = discord.ui.TextInput(label='מאיפה?', placeholder="אשקלון", required=True, max_length=30)
    url = discord.ui.TextInput(label='קישור לתמונה של הבושם (מתוך דיסקורד בלבד!)', placeholder="https://....", max_length=300, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # Validate numbers
        try:
            amount_val = int(self.amount.value)
            capacity_val = int(self.capacity.value)
            if not (0 <= amount_val <= 300 and 0 <= capacity_val <= 300):
                raise ValueError("Value out of range")
            if amount_val > capacity_val:
                raise EnvironmentError()
            if not ("discordapp" in self.url.value):
                raise KeyError()
        except ValueError:
            await interaction.response.send_message("❌ אנא הזן מספרים תקינים בין 0 ל-300.", ephemeral=True)
            return
        except EnvironmentError:
            await interaction.response.send_message("❌ הכמות בבושם לא יכולה להיות יותר גדולה מגודל הבקבוק", ephemeral=True)
            return
        except KeyError:
            await interaction.response.send_message("❌ הקישור לתמונה צריך להיות מדיסקורד בלבד", ephemeral=True)
            return

        # Store temporarily and show shipping dropdown
        user_form_data[interaction.user.id] = {
            "name": self.name.value,
            "amount": amount_val,
            "capacity": capacity_val,
            "city": self.city.value,
            "url": self.url.value,
        }

        await interaction.response.send_message(
            "כמעט סיימנו! אנא בחר האם יש אפשרות למשלוח:",
            view=ShippingOptionView(),
            ephemeral=True
        )


class TradeApplicationForm(discord.ui.Modal, title="פרסום בושם להחלפה"):
    name = discord.ui.TextInput(label="שם הבושם", placeholder="Xerjoff Pikovaya Dama", max_length=50, min_length=10, required=True)
    amount = discord.ui.TextInput(label='כמות במ"ל', placeholder="95", style=discord.TextStyle.short, required=True, max_length=4)
    capacity = discord.ui.TextInput(label='מתוך כמה במ"ל', placeholder="100", style=discord.TextStyle.short, required=True, max_length=4)
    city = discord.ui.TextInput(label='מאיפה?', placeholder="אשקלון", required=True, max_length=30)
    url = discord.ui.TextInput(label='קישור לתמונה של הבושם (מתוך דיסקורד בלבד!)', placeholder="https://....", max_length=300, required=True)
    prefer = discord.ui.TextInput(label='יש לך העדפות ספציפיות?', placeholder="לא", default="לא", max_length=100, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Validate numbers
        try:
            amount_val = int(self.amount.value)
            capacity_val = int(self.capacity.value)
            if not (0 <= amount_val <= 300 and 0 <= capacity_val <= 300):
                raise ValueError("Value out of range")
            if amount_val > capacity_val:
                raise EnvironmentError()
            if not ("discordapp" in self.url.value):
                raise KeyError()
        except ValueError:
            await interaction.response.send_message("❌ אנא הזן מספרים תקינים בין 0 ל-300.", ephemeral=True)
            return
        except EnvironmentError:
            await interaction.response.send_message("❌ הכמות בבושם לא יכולה להיות יותר גדולה מגודל הבקבוק", ephemeral=True)
            return
        except KeyError:
            await interaction.response.send_message("❌ הקישור לתמונה צריך להיות מדיסקורד בלבד", ephemeral=True)
            return

        submission_channel = bot.get_channel(TRADE_CHANNEL_ID)
        if submission_channel:
            embed = discord.Embed(title="בושם חדש להחלפה", color=discord.Color.blue())
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="שם הבושם", value=self.name.value, inline=False)
            embed.add_field(name="כמות", value=f'{amount_val} מ"ל מתוך {capacity_val} מ"ל', inline=False)
            embed.add_field(name="מהעיר", value=self.city.value, inline=False)
            embed.add_field(name="העדפות נוספות", value=self.prefer.value, inline=False)
            embed.set_image(url=self.url.value)

            await submission_channel.send(embed=embed)
            await interaction.response.send_message("✅ הפרטים נשלחו בהצלחה!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ לא ניתן למצוא את הערוץ", ephemeral=True)

class QuestionApplicationForm(discord.ui.Modal, title="פרסום שאלה ליועצים"):
    question = discord.ui.TextInput(label="מה השאלה?", placeholder="בושם טוב לקיץ ב400-500 שקל", max_length=200, min_length=5, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        submission_channel = bot.get_channel(QUESTION_CHANNEL_ID)
        if submission_channel:
            user_mention = f"<@{interaction.user.id}>"
            message = f'{self.question.value} שואל: {user_mention}'
            await submission_channel.send(content=message)
            await interaction.response.send_message("✅ הפרטים נשלחו בהצלחה!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ לא ניתן למצוא את הערוץ", ephemeral=True)

class ShippingOptionView(discord.ui.View):
    @discord.ui.select(
        placeholder="יש אפשרות למשלוח?",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="כן", value="כן"),
            discord.SelectOption(label="כן בתוספת תשלום", value="בתוספת תשלום"),
            discord.SelectOption(label="לא", value="לא"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        form_data = user_form_data.pop(interaction.user.id, None)

        if not form_data:
            await interaction.response.send_message("❌ לא נמצאו נתוני טופס קודמים.", ephemeral=True)
            return

        # Send the full result to the submission channel
        submission_channel = bot.get_channel(SELL_CHANNEL_ID)
        if submission_channel:
            embed = discord.Embed(title="בושם חדש למכירה", color=discord.Color.blue())
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="שם הבושם", value=form_data["name"], inline=False)
            embed.add_field(name="כמות", value=f'{form_data["amount"]} מ"ל מתוך {form_data["capacity"]} מ"ל', inline=False)
            embed.add_field(name="מהעיר", value=form_data["city"], inline=False)
            embed.add_field(name="משלוח", value=value, inline=False)
            embed.set_image(url=form_data["url"])

            await submission_channel.send(embed=embed)
            await interaction.response.send_message("✅ הפרטים נשלחו בהצלחה!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ לא ניתן למצוא את הערוץ", ephemeral=True)


class SellApplicationButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לחץ כאן", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SellApplicationForm())

class TradeApplicationButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לחץ כאן", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TradeApplicationForm())

class QuestionApplicationButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לחץ כאן", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(QuestionApplicationForm())


# ----- ON BOT READY -----
@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user}")
    bot.add_view(SellApplicationButtonView())
    bot.add_view(TradeApplicationButtonView())

    # Optional: send form button message only once
    channel = bot.get_channel(FORM_TRIGGER_CHANNEL_ID)
    if channel:
        await channel.send("לפרסום בושם למכירה:", view=SellApplicationButtonView())
        await channel.send("לפרסום בושם להחלפה:", view=TradeApplicationButtonView())
        await channel.send("אם יש לכם שאלה ליועצים:", view=QuestionApplicationButtonView())
    else:
        print("⚠️ Trigger channel not found.")


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # Make sure it's the ✅ emoji (or whatever emoji you use)
    if str(payload.emoji) != "✅":
        return

    if (payload.channel_id != TRADE_CHANNEL_ID) and (payload.channel_id != SELL_CHANNEL_ID):
        return

    dest_channel_id = DEST_SELL_CHANNEL_ID
    if payload.channel_id == TRADE_CHANNEL_ID:
        dest_channel_id = DEST_TRADE_CHANNEL_ID

    # Fetch message and channel
    source_channel = await bot.fetch_channel(payload.channel_id)
    channel = bot.get_channel(dest_channel_id)
    try:
        message = await source_channel.fetch_message(payload.message_id)
        original_embed = message.embeds[0] if message.embeds else None
        if original_embed:
            await channel.send(embed=original_embed)
            await message.delete()
    except discord.NotFound:
        print("Message not found. It may have been deleted.")
        return
    except discord.Forbidden:
        print("Bot doesn't have permission to view this message.")
        return
    except discord.HTTPException as e:
        print(f"Failed to fetch message: {e}")
        return

    # Edit the embed or resend it for public view



# ----- START -----
bot.run(os.environ["DISCORD_TOKEN"])
