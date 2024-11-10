import discord
from discord import app_commands
from typing import Optional
from utils.logging_handler import logger
from events.on_message import on_message_event
from load_config import get_environment

class DiscordBot(discord.Client):
	def __init__(self, config: dict, **kwargs):
		super().__init__(**kwargs)
		self.config = config
		self.tree = app_commands.CommandTree(self)  # Initialize tree as instance variable
		self._setup_bot()

	def _setup_bot(self) -> None:
		"""Initialize bot configuration and settings."""
		self.log_channel_id = self.config["log_channel_id"]
		self.moderation_settings = self.config["moderation_settings"]
		self.banned_words = self.config["banned_words"]

		# Setup commands
		from commands.petpet import setup_petpet
		setup_petpet(self)

	async def on_ready(self):
		"""Handle bot ready event."""
		logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
		logger.info(f'Connected to {len(self.guilds)} guilds')
		await self.tree.sync()
		logger.info('Bot is ready!')

	async def on_message(self, message: discord.Message):
		"""Handle message events."""
		try:
			await on_message_event(self, message)
		except Exception as e:
			logger.error(f"Error while processing message: {str(e)}", exc_info=True)

	async def on_error(self, event: str, *args, **kwargs):
		"""Handle any errors that occur during bot operation."""
		logger.error(f"Error in {event}", exc_info=True)

	async def close_bot(self):
		"""Safely close the bot connection."""
		await self.close()
		logger.info("Bot connection closed.")


def setup_bot() -> Optional[DiscordBot]:
	"""Setup and configure the Discord bot."""
	try:
		# Load environment configuration
		env = get_environment()
		config = env.configuration

		# Setup Discord intents
		intents = discord.Intents.default()
		intents.message_content = True

		# Initialize bot with configuration
		bot = DiscordBot(
			config=config,
			intents=intents
		)
		return bot

	except Exception as e:
		logger.error(f"Failed to initialize bot: {str(e)}", exc_info=True)
		return None


def main():
	"""Main entry point for the Discord bot."""
	bot = setup_bot()
	if not bot:
		logger.error("Failed to setup bot. Exiting.")
		return

	try:
		# Get the token from configuration
		token = bot.config["bot_token"]

		# Run the bot
		logger.info("Starting bot...")
		bot.run(token, log_handler=None)

	except KeyboardInterrupt:
		logger.info("Bot stopping with KeyboardInterrupt.")
		if bot and not bot.is_closed():
			bot.loop.run_until_complete(bot.close_bot())
	except Exception as e:
		logger.error(f"Critical error: {str(e)}", exc_info=True)
	finally:
		if bot and bot.loop and not bot.is_closed():
			try:
				logger.info("Closing bot event loop")
				bot.loop.close()
				logger.info("Bot event loop closed")
			except Exception as e:
				logger.error(f"Error while closing bot event loop: {str(e)}", exc_info=True)

if __name__ == "__main__":
	main()