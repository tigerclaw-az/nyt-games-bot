import discord, typing
from datetime import date
from discord.ext import commands

if typing.TYPE_CHECKING:
  from handlers.database import BaseDatabaseHandler
  from utils.bot_utilities import BotUtilities

class BaseCommandHandler(typing.Protocol):
  MAX_DATAFRAME_ROWS: int = 10

  db: "BaseDatabaseHandler"
  utils: "BotUtilities"

  def __init__(self, utils: "BotUtilities", db: "BaseDatabaseHandler") -> None:
    self.utils = utils
    self.db = db

  ######################
  #   MEMBER METHODS   #
  ######################

  async def add_entry(self, user: discord.User | discord.Member, title: str, puzzle: str, datetime = None) -> bool:
    if not datetime:
      datetime = self.utils.get_todays_date()
    return await self.db.add_entry(user, title, puzzle, datetime)

  async def get_ranks(self, ctx: commands.Context, *args: str) -> None:
    pass

  async def get_missing(self, ctx: commands.Context, *args: str) -> None:
    pass

  async def get_entries(self, ctx: commands.Context, *args: str) -> None:
    pass

  async def get_entry(self, ctx: commands.Context, *args: str) -> None:
    pass

  async def get_stats(self, ctx: commands.Context, *args: str) -> None:
    pass

  ######################
  #   OWNER METHODS    #
  ######################

  async def remove_entry(self, ctx: commands.Context, *args: str) -> None:
    pass

  async def add_score(self, message: discord.Message | None, user: discord.User, *args: str) -> None:
    pass
