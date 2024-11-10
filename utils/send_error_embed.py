from datetime import datetime
import discord

async def SendErrorEmbed(ctx, message, error):
	embed = discord.Embed(
		title='Bot Error',
		description=f"An error occurred:\n\n ```{error}```",
		color=discord.Color.red()
	)
	embed.add_field(name='User', value=message.author.mention, inline=False)
	embed.add_field(name='Message Content', value=message.content, inline=False)
	embed.add_field(name='Channel', value=message.channel.mention, inline=False)
	embed.set_author(name='Bot Exception', icon_url=message.author.display_avatar.url if message.author.display_avatar else None)
	embed.set_footer(text=f'User ID: {message.author.id}')
	embed.timestamp = datetime.utcnow()

	await ctx.send(embed=embed)
