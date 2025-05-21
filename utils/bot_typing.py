import typing
from discord.ext import commands

if typing.TYPE_CHECKING:
  from logging import Logger
  from handlers.commands.connections import ConnectionsCommandHandler
  from handlers.commands.strands import StrandsCommandHandler
  from handlers.commands.wordle import WordleCommandHandler
  from utils.bot_utilities import BotUtilities
  from utils.help_handler import HelpMenuHandler

class BotUtilitiesProtocol(typing.Protocol):
  utils: "BotUtilities"
  help_menu: "HelpMenuHandler"
  connections: "ConnectionsCommandHandler"
  strands: "StrandsCommandHandler"
  wordle: "WordleCommandHandler"
  logger: "Logger"

class MyBotType(commands.Bot, BotUtilitiesProtocol):
  pass
