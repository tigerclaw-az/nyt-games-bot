import traceback, typing
from discord.ext import commands
from discord import app_commands

if typing.TYPE_CHECKING:
  from handlers.commands.connections import ConnectionsCommandHandler
  from handlers.commands.strands import StrandsCommandHandler
  from handlers.commands.wordle import WordleCommandHandler
  from utils.bot_typing import MyBotType
  from utils.bot_utilities import BotUtilities, NYTGame

class OwnerCog(commands.Cog, name="owner-cog"):
    # class variables
    bot: "MyBotType"
    utils: "BotUtilities"

    # games
    connections: "ConnectionsCommandHandler"
    strands: "StrandsCommandHandler"
    wordle: "WordleCommandHandler"

    def __init__(self, bot: "MyBotType") -> None:
      bot.logger.debug(f"Initializing {self.__class__.__name__} class.")

      self.bot = bot
      self.utils = self.bot.utils
      self.connections = self.bot.connections
      self.strands = self.bot.strands
      self.wordle = self.bot.wordle

    #####################
    #   COMMAND SETUP   #
    #####################

    @commands.is_owner()
    @commands.hybrid_command(
      name="remove",
      description="Removes one puzzle entry for a player"
    )
    @app_commands.describe(
      puzzle_type="The puzzle type to remove entry.",
      command="The command to remove entry."
    )
    async def remove_entry(self, ctx: commands.Context, puzzle_type: str, command: str = ''):
      match self.utils.get_game_type(puzzle_type):
        case NYTGame.CONNECTIONS:
          await self.connections.remove_entry(ctx, command)
        case NYTGame.STRANDS:
          await self.strands.remove_entry(ctx, command)
        case NYTGame.WORDLE:
          await self.wordle.remove_entry(ctx, command)

    @commands.is_owner()
    @commands.hybrid_command(
      name='update',
      description='Updates the database and channel with old puzzles'
    )
    async def update(self, ctx: commands.Context) -> None:
      await ctx.defer()
      count = 0
      async for message in ctx.channel.history(limit=5):
        if (len(message.reactions) == 0):
          await self.bot.on_message(message)
          count += 1
      await ctx.send(
        content=f"Update completed. {count} messages processed.",
        silent=True,
      )

    @commands.is_owner()
    @commands.hybrid_command(
      name='reset',
      description='Resets the database',
    )
    async def reset(self, ctx: commands.Context) -> None:
      await ctx.defer()
      try:
        await self.connections.db.reset_puzzle()
        await self.strands.db.reset_puzzle()
        await self.wordle.db.reset_puzzle()
        await ctx.send(
          content="Database reset completed.",
          delete_after=1,
          ephemeral=True,
          silent=True,
        )
      except Exception as e:
        self.bot.logger.error(f"Failed to reset database: {e}")
        await ctx.send(
          content="Database reset failed.",
          delete_after=2,
          ephemeral=True,
          silent=True,
        )
        traceback.print_exception(e)

async def setup(bot: "MyBotType") -> None:
  try:
    await bot.add_cog(OwnerCog(bot))
    bot.logger.debug(f"Loaded {OwnerCog.__name__} cog.")
  except Exception as e:
    bot.logger.error(f"Failed to load {OwnerCog.__name__} cog: {e}")
    traceback.print_exception(e)
