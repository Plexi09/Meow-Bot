import gzip
import logging
import shutil
from datetime import datetime
from pathlib import Path
import discord


class CustomLogger:
	"""Custom logger with file rotation and compression."""

	def __init__(
			self,
			name: str = 'discord',
			log_dir: str = 'logs',
			max_log_files: int = 1,
			level: int = logging.INFO
	):
		self.log_dir = Path(log_dir)
		self.max_log_files = max_log_files
		self.logger = logging.getLogger(name)

		self._setup_logger(level)
		self._setup_log_directory()
		self._setup_handlers()
		self._clean_old_logs()

	def _setup_logger(self, level: int) -> None:
		"""Configure basic logger settings."""
		self.logger.setLevel(level)
		logging.getLogger('discord.http').setLevel(level)

	def _setup_log_directory(self) -> None:
		"""Create log directory if it doesn't exist."""
		self.log_dir.mkdir(exist_ok=True)

	def _setup_handlers(self) -> None:
		"""Setup file and console handlers."""
		formatter = logging.Formatter(
			'[{asctime}] [{levelname:<8}] {name}: {message}',
			'%Y-%m-%d %H:%M:%S',
			style='{'
		)

		# File handler
		log_filename = self.log_dir / f"discord_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
		file_handler = logging.FileHandler(log_filename, encoding='utf-8')
		file_handler.setFormatter(formatter)
		self.logger.addHandler(file_handler)

		# Console handler
		console_handler = logging.StreamHandler()
		console_handler.setFormatter(formatter)
		self.logger.addHandler(console_handler)

	def _compress_log(self, filename: Path) -> None:
		"""Compress a log file using gzip."""
		with open(filename, 'rb') as f_in:
			with gzip.open(f"{filename}.gz", 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)
		filename.unlink()

	def _clean_old_logs(self) -> None:
		"""Remove old log files keeping only the specified maximum."""
		log_files = sorted(self.log_dir.glob("discord_*.log.gz"))
		if len(log_files) > self.max_log_files:
			for old_log in log_files[:len(log_files) - self.max_log_files]:
				old_log.unlink()

	@property
	def get_logger(self) -> logging.Logger:
		"""Return the configured logger instance."""
		return self.logger

async def send_error_embed(message, error):
	embed = discord.Embed(
		title='An error occurred:',
		description=f"```{error}```",
		color=discord.Color.red()
	)
	embed.add_field(name='User', value=message.author.mention, inline=False)
	embed.add_field(name='Message Content', value=message.content, inline=False)
	embed.add_field(name='Channel', value=message.channel.mention, inline=False)
	embed.set_author(name='Bot Exception', icon_url=message.author.display_avatar.url if message.author.display_avatar else None)
	embed.set_footer(text=f'User ID: {message.author.id}')
	embed.timestamp = datetime.utcnow()

	channel = message.channel
	await channel.send(embed=embed)

# Create and configure the logger
logger = CustomLogger(
	name='discord',
	log_dir='logs',
	max_log_files=1,
	level=logging.INFO
).get_logger