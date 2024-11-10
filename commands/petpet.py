from discord import app_commands
import discord
import discord.ext
from petpetgif import petpet as petpetgif
from typing import Optional
from io import BytesIO

from utils.logging_handler import logger

def setup_petpet(bot):
	@bot.tree.command(
		name="petpet",
		description="Imagine having a pet, but it's your discord buddy"
	)
	@app_commands.describe(
		user="The user to petpet",
		emoji="The custom emoji to petpet (use the actual emoji)"
	)
	async def petpet(
			interaction: discord.Interaction,
			user: Optional[discord.Member] = None,
			emoji: Optional[str] = None
	):
		try:
			if user is not None and emoji is not None:
				await interaction.response.send_message("You can't petpet a user and an emoji at the same time!")
				return
			# Cannot petpet user with ID 836562950713769994
			if user is not None and user is 836562950713769994:
				await interaction.response.send_message("Bruh tu crois quoi mdr ? Que t'allais me troll comme ça ?")
				return
			if user is None and emoji is None:
				target = interaction.user
				if target.avatar is None:
					await interaction.response.send_message("You don't have an avatar!")
					return
				image = await target.avatar.read()
			elif user is not None:
				if user.avatar is None:
					await interaction.response.send_message("That user has no avatar!")
					return
				image = await user.avatar.read()
			elif emoji is not None:
				try:
					# Try to convert the emoji string to a partial emoji
					partial_emoji = discord.PartialEmoji.from_str(emoji)
					if not partial_emoji.is_custom_emoji():
						await interaction.response.send_message("Please use a custom emoji, not a default one!")
						return
					image = await partial_emoji.read()
				except:
					await interaction.response.send_message("That doesn't seem to be a valid custom emoji!")
					return
		except Exception as e:
			logger.error(f"Error while processing petpet command: {str(e)}")
			await interaction.response.send_message("An error occurred while processing your request!")
			return
		source = BytesIO(image)
		dest = BytesIO()
		petpetgif.make(source, dest)
		dest.seek(0)

		await interaction.response.send_message(
			file=discord.File(dest, filename="petpet.gif")
		)