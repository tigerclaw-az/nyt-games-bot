import traceback, typing
from discord import app_commands
from discord.ext import commands

from utils.bot_utilities import NYTGame

if typing.TYPE_CHECKING:
  from handlers.commands.connections import ConnectionsCommandHandler
  from handlers.commands.strands import StrandsCommandHandler
  from handlers.commands.wordle import WordleCommandHandler
  from utils.bot_typing import MyBotType
  from utils.bot_utilities import BotUtilities
  from utils.help_handler import HelpMenuHandler

class MembersCog(commands.Cog, name="members-cog"):
  # class variables
  bot: "MyBotType"
  utils: "BotUtilities"
  help_menu: "HelpMenuHandler"

  # games
  connections: "ConnectionsCommandHandler"
  strands: "StrandsCommandHandler"
  wordle: "WordleCommandHandler"

  def __init__(self, bot: "MyBotType") -> None:
    self.bot = bot
    self.utils = self.bot.utils
    self.help_menu = self.bot.help_menu
    self.build_help_menu()

    self.connections = self.bot.connections
    self.strands = self.bot.strands
    self.wordle = self.bot.wordle

  #####################
  #   COMMAND SETUP   #
  #####################

  @commands.hybrid_command(name="help", description="Show help for the bot.")
  async def help_command(self, ctx: commands.Context, command: str = '') -> None:
    # """Slash command for help."""
    if command == '':
      await ctx.send(self.help_menu.get_all())
    else:
      await ctx.send(self.help_menu.get_message(command))

  @commands.hybrid_command(
    name='ranks',
    description='Show ranks of players in the server'
  )
  @app_commands.describe(
    puzzle_type="The puzzle type to get ranks for."
  )
  async def get_ranks(self, ctx: commands.Context, puzzle_type: str = '') -> None:
    try:
      match self.utils.get_game_type(puzzle_type):
        case NYTGame.CONNECTIONS:
          await self.connections.get_ranks(ctx)
        case NYTGame.STRANDS:
          await self.strands.get_ranks(ctx)
        case NYTGame.WORDLE:
          await self.wordle.get_ranks(ctx)
    except Exception as e:
      self.bot.logger.error(f"Caught exception: {e}")
      traceback.print_exception(e)

  @commands.hybrid_command(
    name='missing',
    description='Show all players missing an entry for a puzzle'
  )
  @app_commands.describe(puzzle_type="The puzzle type to check for missing entries.")
  async def get_missing(self, ctx: commands.Context, puzzle_type: str) -> None:
    try:
      match self.utils.get_game_type(puzzle_type):
        case NYTGame.CONNECTIONS:
          await self.connections.get_missing(ctx)
        case NYTGame.STRANDS:
          await self.strands.get_missing(ctx)
        case NYTGame.WORDLE:
          await self.wordle.get_missing(ctx)
    except Exception as e:
      self.bot.logger.error(f"Caught exception: {e}")
      traceback.print_exception(e)

  @commands.hybrid_command(
    name='entries',
    description='Show all recorded entries for a player'
  )
  async def get_entries(self, ctx: commands.Context) -> None:
    try:
      await self.connections.get_entries(ctx)
      await self.strands.get_entries(ctx)
      await self.wordle.get_entries(ctx)
    except Exception as e:
      self.bot.logger.error(f"Caught exception: {e}")
      traceback.print_exception(e)

  @commands.hybrid_command(
    name="view",
    description="Show player's entry for a given puzzle number"
  )
  @app_commands.describe(
    puzzle_type="The puzzle type to view.",
    puzzle_number="The puzzle number to view."
  )
  async def get_entry(self, ctx: commands.Context, puzzle_type: str, puzzle_number: str) -> None:
    try:
      match self.utils.get_game_type(puzzle_type):
        case NYTGame.CONNECTIONS:
          await self.connections.get_entry(ctx, puzzle_number)
        case NYTGame.STRANDS:
          await self.strands.get_entry(ctx, puzzle_number)
        case NYTGame.WORDLE:
          await self.wordle.get_entry(ctx, puzzle_number)
    except Exception as e:
      self.bot.logger.error(f"Caught exception: {e}")
      traceback.print_exception(e)

  @commands.hybrid_command(name="stats", description="Show basic stats for a player")
  @app_commands.describe(
    puzzle_type="The puzzle type to get stats for."
  )
  async def get_stats(self, ctx: commands.Context, puzzle_type: str) -> None:
    try:
      match self.utils.get_game_type(puzzle_type):
        case NYTGame.CONNECTIONS:
          await self.connections.get_stats(ctx)
        case NYTGame.STRANDS:
          await self.strands.get_stats(ctx)
        case NYTGame.WORDLE:
          await self.wordle.get_stats(ctx)
    except Exception as e:
      self.bot.logger.error(f"Caught exception: {e}")
      traceback.print_exception(e)

  ######################
  #   HELPER METHODS   #
  ######################

  def build_help_menu(self) -> None:
    self.help_menu.add('ranks', \
        explanation = "View the leaderboard over time or for a specific puzzle.", \
        usage = "`?ranks (today|weekly|10-day|all-time)`\n`?ranks <MM/DD/YYYY>`\n`?ranks <puzzle #>`", \
        notes = "- `?ranks` will default to `?ranks weekly`.\n- When using MM/DD/YYYY format, the date must be a Sunday.")
    self.help_menu.add('missing', \
        explanation = "View and mention all players who have not yet submitted a puzzle.", \
        usage = "`?missing [<puzzle #>]`", \
        notes = "`?missing` will default to today's puzzle.")
    self.help_menu.add('entries', \
        explanation = "View a list of all submitted entries for a player.", \
        usage = "`?entries [<player>]`")
    self.help_menu.add('stats', \
        explanation = "View more details stats on one or players.", \
        usage = "`?stats <player1> [<player2> ...]`", \
        notes = "`?stats` will default to just query for the calling user.")
    self.help_menu.add('view', \
        explanation = "View specific details of one or more entries.", \
        usage = "`?view [<player>] <puzzle #1> [<puzzle #2> ...]`")
    self.help_menu.add('add', \
        explanation = "Manually add an entry to the database.", \
        usage = "`?add [<player>] <entry>`", \
        owner_only=True)
    self.help_menu.add('remove', \
        explanation = "Remove an entry from the database.", \
        usage = "`?remove [<player>] <puzzle #>`", \
        owner_only=True)

async def setup(bot: "MyBotType") -> None:
  try:
    await bot.add_cog(MembersCog(bot))
    bot.logger.debug(f"Loaded {MembersCog.__name__} cog.")
  except Exception as e:
    bot.logger.error(f"Failed to load {MembersCog.__name__} cog: {e}")
    traceback.print_exception(e)
