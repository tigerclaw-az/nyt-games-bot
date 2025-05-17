import traceback
from discord.ext import commands
from discord import app_commands

from handlers.commands.connections import ConnectionsCommandHandler
from handlers.commands.strands import StrandsCommandHandler
from handlers.commands.wordle import WordleCommandHandler
from utils.bot_utilities import BotUtilities, NYTGame

class OwnerCog(commands.Cog, name="owner-cog"):
    # class variables
    bot: commands.Bot
    utils: BotUtilities

    # games
    connections: ConnectionsCommandHandler
    strands: StrandsCommandHandler
    wordle: WordleCommandHandler

    def __init__(self, bot: commands.Bot):
      self.bot = bot
      self.utils = self.bot.utils
      self.connections = self.bot.connections
      self.strands = self.bot.strands
      self.wordle = self.bot.wordle

    #####################
    #   COMMAND SETUP   #
    #####################
    # def is_owner():
    #   async def predicate(interaction: discord.Interaction) -> bool:
    #       return await interaction.client.is_owner(interaction.user)
    #   return app_commands.check(predicate)

    @commands.is_owner()
    @commands.hybrid_command(
      name="remove",
      description="Removes one puzzle entry for a player"
    )
    @app_commands.describe(
      puzzle_type="The puzzle type to remove entry.",
      command="The command to remove entry."
    )
    async def remove_entry(self, ctx: commands.Context, puzzle_type: str, command: str = None):
      match self.utils.get_game_type(puzzle_type):
        case NYTGame.CONNECTIONS:
          await self.connections.remove_entry(ctx, command)
        case NYTGame.STRANDS:
          await self.strands.remove_entry(ctx, command)
        case NYTGame.WORDLE:
          await self.wordle.remove_entry(ctx, command)

    @commands.is_owner()
    @commands.hybrid_command(
      name='add',
      description='Manually adds a puzzle entry for a player'
    )
    @app_commands.describe(
      puzzle_type="The puzzle type to add entry.",
      command="The command to add entry."
    )
    async def add_score(self, ctx: commands.Context, puzzle_type: str, command: str = None):
      match self.utils.get_game_type(puzzle_type):
        case NYTGame.CONNECTIONS:
          await self.connections.add_score(ctx, command)
        case NYTGame.STRANDS:
          await self.strands.add_score(ctx, command)
        case NYTGame.WORDLE:
          await self.wordle.add_score(ctx, command)

async def setup(bot: commands.Bot):
  try:
    await bot.add_cog(OwnerCog(bot))
    bot.logger.debug(f"Loaded {OwnerCog.__name__} cog.")
  except Exception as e:
    bot.logger.error(f"Failed to load {OwnerCog.__name__} cog: {e}")
    traceback.print_exception(e)
