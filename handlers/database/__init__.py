from datetime import date
from typing import Protocol

import aiosqlite
from models import PuzzleName
from utils.bot_utilities import BotUtilities

class BaseDatabaseHandler(Protocol):
  _utils: BotUtilities
  _arbitrary_date: date
  _arbitrary_date_puzzle: int

  def __init__(self, utils: BotUtilities, connection: aiosqlite.Connection) -> None:
    self._utils = utils
    self.connection = connection

    self._puzzle_name: PuzzleName.value = None

  ####################
  # ABSTRACT METHODS #
  ####################

  def add_entry(self, user_id: str, title: str, puzzle: str) -> bool:
    pass

  def get_entries_by_player(self, user_id: str, puzzle_list: list[int] = []) -> list[object]:
    pass

  ####################
  #   BASE METHODS   #
  ####################

  async def remove_entry(self, user_id: str, puzzle_id: int) -> bool:
    await self.connection.execute(f"delete from {self._puzzle_name} where user_id = {user_id} and puzzle_id = {puzzle_id}")
    await self.connection.commit()
    return self.connection.total_changes > 0

  async def add_user_if_not_exists(self, user_id: str) -> None:
    if not self.user_exists(user_id):
      user_name = self._utils.get_nickname(user_id)
      await self.connection.execute(f"insert into users (user_id, name) values ('{user_id}', '{user_name}')")
      self.connection.commit()
      if self.connection.total_changes == 0:
        raise Exception("Failed to add user to the database")

  async def user_exists(self, user_id: str) -> bool:
    async with self.connection.execute_fetchall(f"select * from users where user_id = {user_id}") as rows:
      if len(rows) == 0:
        return False
      return True

  async def entry_exists(self, user_id: str, puzzle_id: int) -> bool:
    async with self.connection.execute_fetchall(f"select * from {self._puzzle_name} where user_id = {user_id} and puzzle_id = {puzzle_id}") as rows:
      if len(rows) == 0:
        return False
      return True

  ####################
  #  PUZZLE METHODS  #
  ####################

  def get_puzzle_by_date(self, query_date: date) -> int:
    return self._arbitrary_date_puzzle + (query_date - self._arbitrary_date).days

  def get_puzzles_by_week(self, query_date: date) -> list[int]:
    if self._utils.is_sunday(query_date):
      sunday_puzzle_id = self.get_puzzle_by_date(query_date)
      return list(range(sunday_puzzle_id, sunday_puzzle_id + 7))

    return []

  async def get_all_puzzles(self) -> list[int]:
    async with self.connection.execute_fetchall(f"select distinct puzzle_id from {self._puzzle_name} where puzzle_name = {self.puzzle_name}") as rows:
      if len(rows) == 0:
        return []
      return [row[0] for row in rows]

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_all_players(self) -> list[str]:
    async with self.connection.execute_fetchall("select distinct user_id from users") as rows:
      if len(rows) == 0:
        return []
      return [row[0] for row in rows]

  async def get_puzzles_by_player(self, user_id) -> list[int]:
    async with self.connection.execute_fetchall(f"select distinct puzzle_id from {self._puzzle_name} where user_id = {user_id}") as rows:
      if len(rows) == 0:
        return []
      return [row[0] for row in rows]

  async def get_players_by_puzzle_id(self, puzzle_id: int) -> list[str]:
    async with self.connection.execute_fetchall(f"select distinct user_id from {self._puzzle_name} where puzzle_id = {puzzle_id}") as rows:
      if len(rows) == 0:
        return []
      return [row[0] for row in rows]
