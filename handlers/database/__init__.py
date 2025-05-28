import aiosqlite, discord, typing
from datetime import date

from numpy import True_

from utils.bot_utilities import BotUtilities

class BaseDatabaseHandler(typing.Protocol):
  connection: aiosqlite.Connection
  puzzle_name: str
  utils: BotUtilities

  _arbitrary_date: date
  _arbitrary_date_puzzle: int

  def __init__(self, utils: BotUtilities) -> None:
    self.connection: aiosqlite.Connection = utils.connection
    self.utils = utils

    self.puzzle_name = ''

  ####################
  # ABSTRACT METHODS #
  ####################

  async def add_entry(self, user: discord.User | discord.Member, title: str, puzzle: str, datetime: date) -> bool: # type: ignore
    pass

  async def get_entries_by_player[T](self, user_id: int, puzzle_list: list[int] = []) -> list[T]: # type: ignore
    pass

  ####################
  #   BASE METHODS   #
  ####################

  async def reset_puzzle(self) -> None:
    self.utils.bot.logger.debug(f"Resetting {self.puzzle_name} database.")
    await self.connection.execute(f"delete from {self.puzzle_name}")
    await self.connection.commit()

  async def remove_entry(self, user_id: int, puzzle_id: int) -> bool:
    await self.connection.execute(f"delete from {self.puzzle_name} where user_id = ? and puzzle_id = ?", (user_id, puzzle_id))
    await self.connection.commit()
    return self.connection.total_changes > 0

  async def add_user_if_not_exists(self, user: discord.User | discord.Member) -> None:
    if user is None:
      raise Exception(f"User cannot be None!")

    user_id = user.id
    user_name = user.name
    if not await self.user_exists(user_id):
      self.utils.bot.logger.debug(f"Adding user to database: {user}")

      await self.connection.execute(f"insert into users values (?, ?, ?)", (user_id, user_name, self.utils.get_todays_date(),))
      await self.connection.commit()
      if self.connection.total_changes <= 0:
        raise Exception("Failed to add user to the database")

  async def user_exists(self, user_id: int) -> bool:
    self.utils.bot.logger.debug(f"Checking if user exists: {user_id}")
    async with self.connection.execute(
      f"select * from users where user_id = (?)",
      (user_id,)
    ) as cursor:
      user: aiosqlite.Row | None = await cursor.fetchone()
      self.utils.bot.logger.debug(f"User exists? {user_id}: {cursor.rowcount} | {user}")
      return False if user is None else True

  async def entry_exists(self, user_id: int, puzzle_id: int) -> bool:
    self.utils.bot.logger.debug(f"Checking if entry exists: {user_id} | {puzzle_id}")
    async with self.connection.execute(
      f"select * from {self.puzzle_name} where user_id = ? and puzzle_id = ?",
      (user_id, puzzle_id,)
    ) as cursor:
      entry: aiosqlite.Row | None = await cursor.fetchone()
      self.utils.bot.logger.debug(f"Entry for user {user_id} and puzzle {puzzle_id}: {entry}")
      return False if entry is None else True

  ####################
  #  PUZZLE METHODS  #
  ####################

  def get_puzzle_by_date(self, query_date: date) -> int:
    return self._arbitrary_date_puzzle + (query_date - self._arbitrary_date).days

  def get_puzzles_by_week(self, query_date: date) -> list[int]:
    if self.utils.is_sunday(query_date):
      sunday_puzzle_id = self.get_puzzle_by_date(query_date)
      return list(range(sunday_puzzle_id, sunday_puzzle_id + 7))

    return []

  async def get_all_puzzles(self) -> list[int]:
    async with self.connection.execute_fetchall(f"select distinct puzzle_id from {self.puzzle_name}") as rows:
      return [row[0] for row in rows]

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_all_players(self) -> list[int]:
    async with self.connection.execute_fetchall("select distinct user_id from users") as rows:
      self.utils.bot.logger.debug(f"get_all_players():: {rows}")
      return [row[0] for row in rows]

  async def get_puzzles_by_player(self, user_id) -> list[int]:
    async with self.connection.execute_fetchall(
      f"select distinct puzzle_id from {self.puzzle_name} where user_id = ?",
      (user_id,)
    ) as rows:
      self.utils.bot.logger.debug(f"get_puzzles_by_player():: {rows}")
      return [row[0] for row in rows]

  async def get_players_by_puzzle_id(self, puzzle_id: int) -> list[int]:
    async with self.connection.execute_fetchall(
      f"select distinct user_id from {self.puzzle_name} where puzzle_id = ?",
      (puzzle_id,)
    ) as rows:
      self.utils.bot.logger.debug(f"get_players_by_puzzle_id():: {rows}")
      return [row[0] for row in rows]
