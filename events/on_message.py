from utils.logging_handler import logger, send_error_embed

async def on_message_event(client, message):
	"""
	Handle incoming messages.

	Args:
		client: Discord client instance
		message: Message to process
	"""
	try:
		if message.author.bot:
			return

	except Exception as e:
		logger.error(f"Error while processing message: {e}")
		await send_error_embed(message, e)