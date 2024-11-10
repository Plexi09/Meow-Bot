import os
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import json
from utils.logging_handler import logger


@dataclass
class ModerationConfig:
	"""Data class to store moderation configuration."""
	settings: Dict[str, Any]
	banned_words: List[str]
	log_channel_id: int

	@classmethod
	def validate(cls, config: Dict[str, Any]) -> 'ModerationConfig':
		"""Validate and create a ModerationConfig instance from dictionary."""
		banned_words = config.get('BANNED_WORDS', [])
		moderation_settings = config.get('MODERATION_SETTINGS', {})
		log_channel_id = config.get('LOG_CHANNEL_ID')

		if not isinstance(banned_words, list):
			raise ValueError("'BANNED_WORDS' must be a list")
		if not isinstance(moderation_settings, dict):
			raise ValueError("'MODERATION_SETTINGS' must be a dictionary")
		if not log_channel_id:
			raise ValueError("'LOG_CHANNEL_ID' must be set")

		return cls(
			settings=moderation_settings,
			banned_words=banned_words,
			log_channel_id=int(log_channel_id)
		)


class Environment:
	"""Handles environment configuration and validation."""

	DEFAULT_CONFIG_PATH = Path('config.json')
	EXAMPLE_CONFIG_URL = "https://github.com/your-repo/example-config.json"

	def __init__(self, config_path: Path = None):
		self.config_path = config_path or self.DEFAULT_CONFIG_PATH
		self._load_env()
		self.config = self._load_config_file()
		self.bot_token = self._get_bot_token()
		self.moderation = ModerationConfig.validate(self.config)

	def _load_env(self) -> None:
		"""Load environment variables from .env file."""
		load_dotenv()

	def _get_bot_token(self) -> str:
		"""Retrieve and validate bot token from environment variables."""
		bot_token = os.getenv('BOT_TOKEN')
		if not bot_token:
			raise EnvironmentError(
				"BOT_TOKEN environment variable is not set. "
				"Please set it in your .env file."
			)
		return bot_token

	def _load_config_file(self) -> Dict[str, Any]:
		"""Load and parse the configuration file."""
		try:
			with open(self.config_path, 'r') as config_file:
				return json.load(config_file)
		except FileNotFoundError:
			self._create_empty_config()
			raise FileNotFoundError(
				f"Configuration file not found at {self.config_path}. "
				f"An empty file has been created. Please fill it using the "
				f"example config at: {self.EXAMPLE_CONFIG_URL}"
			)
		except json.JSONDecodeError as e:
			raise ValueError(
				f"Invalid JSON format in {self.config_path}: {str(e)}. "
				f"Please check the example config at: {self.EXAMPLE_CONFIG_URL}"
			)

	def _create_empty_config(self) -> None:
		"""Create an empty configuration file."""
		self.config_path.touch()
		logger.info(f"Created empty configuration file at {self.config_path}")

	@property
	def configuration(self) -> Dict[str, Any]:
		"""Return the complete configuration."""
		return {
			"bot_token": self.bot_token,
			"log_channel_id": self.moderation.log_channel_id,
			"moderation_settings": self.moderation.settings,
			"banned_words": self.moderation.banned_words
		}


def get_environment(config_path: str = None) -> Environment:
	"""Factory function to create and validate environment configuration."""
	try:
		return Environment(Path(config_path) if config_path else None)
	except (EnvironmentError, FileNotFoundError, ValueError) as e:
		logger.error(str(e))
		raise SystemExit(1)