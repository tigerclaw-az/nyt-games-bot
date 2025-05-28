import discord, re
from turtle import pu
from datetime import date

from handlers.database import BaseDatabaseHandler
from models import PuzzleName
from models.wordle import WordlePuzzleEntry
from utils.bot_utilities import BotUtilities

class WordleDatabaseHandler(BaseDatabaseHandler):
  def __init__(self, utils: BotUtilities) -> None:
    utils.bot.logger.debug(f"Initializing {self.__class__.__name__} class.")

    # init
    super().__init__(utils)
    self.puzzle_name = PuzzleName.WORDLE.value.lower()

    # puzzles
    self._arbitrary_date = date(2022, 1, 10)
    self._arbitrary_date_puzzle = 205

  ####################
  #  PUZZLE METHODS  #
  ####################

  async def add_entry(self, user: discord.User | discord.Member, title: str, puzzle: str, datetime) -> bool:
    self.utils.bot.logger.debug(f"Wordle->add_entry()::<{user}>\n{title}\n{puzzle}")

    # Extract puzzle ID and score from the title
    puzzle_id_str: str = ''
    score_str: str = ''
    if 'X/6' in title:
      reg_match: re.Match[str] | None = re.search(r'\d{1,3}(,\d{3})*', title)
      if reg_match:
        puzzle_id_str = reg_match.group(0).replace(',', '')
        score_str = '7'
      else:
        return False
    else:
      reg_match = re.search(r'\d{1,3}(,\d{3})*', title)
      if reg_match:
        puzzle_id_str = reg_match.group(0).replace(',', '')
        reg_match = re.search(r'(\d)\/(\d)', title)
        if reg_match:
          score_str = reg_match.group(1)
        else:
          return False
      else:
        return False

    puzzle_id: int = int(puzzle_id_str)
    score: int = int(score_str)
    # puzzle = puzzle.replace("\n", ' ')
    total_green: int = puzzle.count('🟩')
    total_yellow: int = puzzle.count('🟨')
    total_other: int = puzzle.count('⬜') + puzzle.count('⬛')
    self.utils.bot.logger.debug(f"{puzzle_id}\n{puzzle}\n{total_green}:{total_yellow}:{total_other}\n->{score}")

    await self.add_user_if_not_exists(user)
    user_id: int = user.id

    if await self.entry_exists(user_id, puzzle_id):
      self.utils.bot.logger.debug(f"Entry already exists for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"update {self.puzzle_name} set score = ?, green = ?, yellow = ?, other = ? where user_id = ? and puzzle_id = ?",
        (score, total_green, total_yellow, total_other, user_id, puzzle_id,)
      )
    else:
      self.utils.bot.logger.debug(f"Adding entry for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"insert into {self.puzzle_name} values (?,?,?,?,?,?,?,?)",
        (puzzle_id, user_id, puzzle, score, total_green, total_yellow, total_other, datetime)
      )

    await self.connection.commit()
    self.utils.bot.logger.debug(f"total_changes: {self.connection.total_changes}")
    return self.connection.total_changes > 0

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_entries_by_player(self, user_id: int, puzzle_list: list[int] = []) -> list[WordlePuzzleEntry]:
    if not puzzle_list or len(puzzle_list) == 0:
      query = f"select puzzle_id, score, green, yellow, other from {self.puzzle_name} where user_id = {user_id} AND puzzle_name = {self.puzzle_name}"
    else:
      puzzle_list_str = ','.join([str(p_id) for p_id in puzzle_list])
      query = f"select puzzle_id, score, green, yellow, other from {self.puzzle_name} where user_id = {user_id} and puzzle_id in ({puzzle_list_str})"
    async with self.connection.execute_fetchall(query) as rows:
      entries: list[WordlePuzzleEntry] = []
      for row in rows:
        entries.append(WordlePuzzleEntry(row[0], user_id, row[1], row[2], row[3], row[4]))
      return entries
