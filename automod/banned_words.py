import string
from nltk.stem.snowball import EnglishStemmer, FrenchStemmer
import discord
from datetime import datetime
from typing import List, Optional
import re
from utils.logging_handler import logger
import random
from itertools import product

class WordFilter:
	def __init__(self, banned_words: List[str], log_channel_id: int, webhook_url: str):
		"""
		Initialize the word filter.

		Args:
			banned_words: List of words that are not allowed
			log_channel_id: Discord channel ID where alerts will be sent
			webhook_url: URL for the webhook to use for sending messages
		"""
		self.banned_words = [word.lower() for word in banned_words]
		self.log_channel_id = log_channel_id
		self.webhook_url = webhook_url
		self.en_stemmer = EnglishStemmer()
		self.fr_stemmer = FrenchStemmer()

		# Create stems for banned words
		self.banned_stems = {
			'en': [self.en_stemmer.stem(word) for word in self.banned_words],
			'fr': [self.fr_stemmer.stem(word) for word in self.banned_words]
		}

		# Common character substitutions
		self.char_substitutions = {
			'a': ['4', '@', 'à', 'á', 'â', 'ä'],
			'e': ['3', 'é', 'è', 'ê', 'ë'],
			'i': ['1', '!', 'í', 'ì', 'î', 'ï'],
			'o': ['0', 'ó', 'ò', 'ô', 'ö'],
			'u': ['ú', 'ù', 'û', 'ü'],
			's': ['$', '5'],
		}

		# Create regex patterns for each banned word
		self.patterns = self._create_word_patterns()

	def _create_word_patterns(self) -> List[re.Pattern]:
		"""Create regex patterns that match different variations of banned words."""
		patterns = []
		for word in self.banned_words:
			# Create pattern parts for each character in the word
			pattern_parts = []
			for char in word:
				if char.lower() in self.char_substitutions:
					chars = [char.lower()] + self.char_substitutions[char.lower()]
					pattern_parts.append(f'[{"".join(chars)}]')
				else:
					pattern_parts.append(re.escape(char))

			# Allow for optional spaces or dots between characters
			pattern = r'\b'
			pattern += r'[.\s-]*'.join(pattern_parts)
			pattern += r'\b'

			patterns.append(re.compile(pattern, re.IGNORECASE))

		return patterns

	def _normalize_text(self, text: str) -> str:
		"""Remove common obfuscation techniques from text."""
		# Remove repeated characters (e.g., 'heeello' -> 'hello')
		text = re.sub(r'(.)\1+', r'\1', text)
		# Remove non-alphanumeric characters
		text = ''.join(char for char in text if char.isalnum() or char.isspace())
		return text.lower()

	def _contains_banned_word(self, content: str) -> Optional[str]:
		"""
		Check if content contains any banned words or their variations.

		Args:
			content: Message content to check

		Returns:
			Optional[str]: The found banned word if any, None otherwise
		"""
		# Check direct matches with variations
		content_lower = content.lower()
		normalized_content = self._normalize_text(content)

		# Check regex patterns (includes character substitutions)
		for pattern, word in zip(self.patterns, self.banned_words):
			if pattern.search(content):
				return word

		# Check word stems
		words = normalized_content.split()
		for word in words:
			en_stem = self.en_stemmer.stem(word)
			fr_stem = self.fr_stemmer.stem(word)

			if en_stem in self.banned_stems['en']:
				return self.banned_words[self.banned_stems['en'].index(en_stem)]
			if fr_stem in self.banned_stems['fr']:
				return self.banned_words[self.banned_stems['fr'].index(fr_stem)]

		return None

	async def check_message(self, client: discord.Client, message: discord.Message) -> bool:
		"""
		Check if message contains any banned words and handle moderation if needed.

		Args:
			client: Discord client instance
			message: Message to check

		Returns:
			bool: True if message contained banned content and was handled
		"""
		if message.author.bot:
			return False

		found_word = self._contains_banned_word(message.content)
		if found_word:
			await self._handle_violation(client, message, found_word)
			return True
		return False

	async def _handle_violation(self, client: discord.Client, message: discord.Message, banned_word: str) -> None:
		try:
			await message.delete()

			webhooks = await message.channel.webhooks()
			if webhooks:
				webhook = webhooks[0]
			else:
				webhook = await message.channel.create_webhook(name="Censorship Webhook")

			censored_content = message.content
			# Use regex to find variations of the banned word
			for pattern in self.patterns:
				matches = pattern.finditer(censored_content)
				for match in matches:
					censored_word = ''.join(random.choice(string.punctuation) for _ in range(len(match.group())))
					censored_content = censored_content[:match.start()] + f'`{censored_word}`' + censored_content[match.end():]

			await webhook.send(
				content=censored_content,
				username=message.author.display_name,
				avatar_url=message.author.display_avatar.url
			)

			log_channel = client.get_channel(self.log_channel_id)
			if log_channel:
				embed = discord.Embed(
					title='Banned Word Detected',
					description='A message containing a banned word has been removed.',
					color=discord.Color.red()
				)
				embed.add_field(name='User', value=f'{message.author.mention}', inline=False)
				embed.add_field(name='Original Message', value=message.content, inline=False)
				embed.add_field(name='Detected Word', value=banned_word, inline=False)
				embed.set_footer(text=f'User ID: {message.author.id}')
				await log_channel.send(embed=embed)

		except Exception as e:
			logger.error(f"Error handling word filter violation: {str(e)}")