import discord, traceback, typing
from discord import DiscordException, app_commands
from discord.ext import commands

from models import PuzzleName
from utils.bot_utilities import NYTGame
from utils.help_handler import HelpMenuHandler

if typing.TYPE_CHECKING:
  from handlers.commands.connections import ConnectionsCommandHandler
  from handlers.commands.strands import StrandsCommandHandler
  from handlers.commands.wordle import WordleCommandHandler
  from utils.bot_typing import MyBotType
  from utils.bot_utilities import BotUtilities

class MembersCog(commands.Cog, name="members-cog"):
  # class variables
  bot: "MyBotType"
  utils: "BotUtilities"
  help_menu: HelpMenuHandler

  # games
  connections: "ConnectionsCommandHandler"
  strands: "StrandsCommandHandler"
  wordle: "WordleCommandHandler"

  def __init__(self, bot: "MyBotType") -> None:
    bot.logger.debug(f"Initializing {self.__class__.__name__} class.")

    self.bot = bot
    self.utils = self.bot.utils
    self.help_menu = self.bot.help_menu
    self.build_help_menu()

    self.connections = self.bot.connections
    self.strands = self.bot.strands
    self.wordle = self.bot.wordle

    self.ctx_menu = app_commands.ContextMenu(
      name      = 'Add Puzzle Entry',
      callback  = self.add_puzzle_entry,
      type      = discord.AppCommandType.message
    )
    self.bot.tree.add_command(self.ctx_menu)

  async def cog_unload(self) -> None:
    self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

  async def add_puzzle_entry(self, interaction: discord.Interaction, message: discord.Message) -> None:
      self.bot.logger.debug(f"add_puzzle_entry() :: {interaction}\n{message}")

      if interaction is None or message is None:
        self.bot.logger.error(f"Interaction and Message cannot be `None`")
        await interaction.response.send_message(
          content=f"An error ocurred trying to add puzzle",
          ephemeral=True,
          delete_after=30,
        )
        raise RuntimeError(f"Interaction cannot be `None`")

      content = message.content
      user = typing.cast(discord.User, message.author)
      self.bot.logger.debug(f"{content}\n<{user}>")

      puzzle_type: str = ''
      try:
        if self.utils.is_connections_submission(content):
          await self.connections.add_score(message, user, content)
          puzzle_type = PuzzleName.CONNECTIONS.value
        elif self.utils.is_strands_submission(content):
          await self.strands.add_score(message, user, content)
          puzzle_type = PuzzleName.STRANDS.value
        elif self.utils.is_wordle_submission(content):
          await self.wordle.add_score(message, user, content)
          puzzle_type = PuzzleName.WORDLE.value
        else:
          await interaction.response.send_message(
            content=f"Unknown puzzle type, couldn't add puzzle.",
            ephemeral=True,
            delete_after=60,
          )
          return

        await interaction.response.send_message(
          content=f"{puzzle_type} puzzle added succesfully!",
          ephemeral=True,
          delete_after=5,
        )
      except Exception as e:
        await interaction.response.send_message(
          content=f"An error ocurred: {e}",
          ephemeral=True,
          delete_after=60,
        )


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
