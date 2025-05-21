import aiosqlite, asyncio, os, discord, logging, platform, random, traceback
from discord.ext import commands, tasks
from dotenv import load_dotenv

from handlers.commands.connections import ConnectionsCommandHandler
from handlers.commands.strands import StrandsCommandHandler
from handlers.commands.wordle import WordleCommandHandler
from models import PuzzleName
from utils.bot_typing import MyBotType
from utils.bot_utilities import BotUtilities, DiscordReactions
from utils.help_handler import HelpMenuHandler

# parse environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN', 'XXXX')
DISCORD_ENV = os.getenv('DISCORD_ENV', 'prod')
APPLICATION_ID = int(os.getenv('CLIENT_ID', -1))
INVITE_LINK = os.getenv("INVITE_LINK")

class LoggingFormatter(logging.Formatter):
  # Colors
  black = "\x1b[30m"
  red = "\x1b[31m"
  green = "\x1b[32m"
  yellow = "\x1b[33m"
  blue = "\x1b[34m"
  gray = "\x1b[38m"
  # Styles
  reset = "\x1b[0m"
  bold = "\x1b[1m"

  COLORS = {
    logging.DEBUG: gray + bold,
    logging.INFO: blue + bold,
    logging.WARNING: yellow + bold,
    logging.ERROR: red,
    logging.CRITICAL: red + bold,
  }

  def format(self, record):
    log_color = self.COLORS[record.levelno]
    format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
    format = format.replace("(black)", self.black + self.bold)
    format = format.replace("(reset)", self.reset)
    format = format.replace("(levelcolor)", log_color)
    format = format.replace("(green)", self.green + self.bold)
    formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
    return formatter.format(record)

# setup logging
logger = logging.getLogger("DiscordBot")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# build Discord client
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.guild_messages = True
intents.guild_reactions = True
client = discord.Client(intents=intents)

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
      # setup the bot
      super().__init__(
        command_prefix=commands.when_mentioned_or(os.getenv("PREFIX", '!')),
        intents=intents,
        application_id=APPLICATION_ID,
        help_command=None,
        case_insensitive=True,
        description="NYT Games Stats Bot",
      )
      """
      This creates custom bot variables so that we can access these variables in cogs more easily.

      For example, The logger is available using the following code:
      - self.logger # In this class
      - bot.logger # In this file
      - self.bot.logger # In cogs
      """
      self.logger = logger
      self.invite_link = INVITE_LINK
      self.guild_id = int(os.getenv('GUILD_ID', -1))
      self.utils = BotUtilities(client, self)
      self.help_menu = HelpMenuHandler()

    async def init_db(self) -> bool:
      try:
        async with aiosqlite.connect(
          f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
        ) as db:
          with open(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql",
            encoding = "utf-8"
          ) as file:
            await db.executescript(file.read())
          await db.commit()
          connection: aiosqlite.Connection = await aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db",

          )

        self.logger.info("Database loaded & successfully logged in.")

        # create games
        self.connections = ConnectionsCommandHandler(self.utils, connection)
        self.strands = StrandsCommandHandler(self.utils, connection)
        self.wordle = WordleCommandHandler(self.utils, connection)
        return True
      except Exception as e:
        self.logger.error(f"Failed to load database: {e}")
        return False

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        """
        Setup the game status task of the bot.
        """
        statuses = ["with you!", "with Krypton!", "with humans!"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        """
        Before starting the status changing task, we make sure the bot is ready
        """
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
      """
      This will just be executed when the bot starts the first time.
      """
      self.logger.info(f"discord.py API version: {discord.__version__}")
      self.logger.info(f"Python version: {platform.python_version()}")
      self.logger.info(
        f"Running on: {platform.system()} {platform.release()} ({os.name})"
      )
      self.logger.info("-------------------")
      if not await self.init_db():
        return

      for extension in ['cogs.members', 'cogs.owner']:
        try:
          await self.load_extension(extension)
          # cog = self.get_cog(extension.split('.')[-1]+'-cog')
          # print([c.name for c in cog.walk_commands()])
          # print([c.name for c in cog.walk_app_commands()])
        except Exception as e:
          raise RuntimeError(f"Failed to load extension '{extension}'.\n{e}")

      self.status_task.start()
      # Setup slash commands
      try:
        self.tree.copy_global_to(guild=discord.Object(id=self.guild_id))
        await self.tree.sync(guild=discord.Object(id=self.guild_id))
        self.logger.debug(f"Slash commands synced for guild ID {self.guild_id}.")
      except Exception as e:
        self.logger.error(f"Failed to sync slash commands for guild ID {self.guild_id}.\n{e}")

    async def on_ready(self):
      if self.user is not None:
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.debug(f'{self.user} has connected to Discord!')
      else:
        self.logger.warning("self.user is None in on_ready()")

    @client.event
    async def on_message(self, message: discord.Message) -> None:
      if self.user is None:
        return

      self.logger.debug("*** on_message() ***")
      user_id = str(message.author.id)
      app_user_id = str(self.user.id)
      self.logger.debug(f"Message from {message.author}: {message.content}")
      content_length: int = message.content.count("\n")
      self.logger.debug(f"user_id: {user_id} | content_length: {content_length} | is_bot: {user_id == app_user_id}")
      if user_id == app_user_id:
        self.logger.debug("Ignoring message from bot itself...")
        # ignore messages from the bot itself
        return

      try:
        if content_length >= 2:
          # parse non-puzzle lines from message
          first_line = message.content.splitlines()[0].strip()
          first_two_lines = '\n'.join(message.content.splitlines()[:2])
          self.logger.debug(f"first line: {first_line}")
          # add entry to either Wordle or Connections
          if PuzzleName.WORDLE.value in first_line and self.utils.is_wordle_submission(first_line):
            self.logger.debug("Wordle puzzle submitted.")
            content = '\n'.join(message.content.splitlines()[1:])
            if await self.wordle.add_entry(user_id, first_line, content):
              await message.add_reaction(DiscordReactions['checkmark'])
          elif PuzzleName.CONNECTIONS.value in first_line and self.utils.is_connections_submission(first_two_lines):
            self.logger.debug("Connections puzzle submitted.")
            content = '\n'.join(message.content.splitlines()[2:])
            if await self.connections.add_entry(user_id, first_two_lines, content):
              await message.add_reaction(DiscordReactions['checkmark'])
          elif PuzzleName.STRANDS.value in first_line and self.utils.is_strands_submission(first_two_lines):
            self.logger.debug("Strands puzzle submitted.")
            content = '\n'.join(message.content.splitlines()[2:])
            if await self.strands.add_entry(user_id, first_two_lines, content):
              await message.add_reaction(DiscordReactions['checkmark'])
        else:
          self.logger.info("Non puzzle message received.")
          # await self.process_commands(message)
          await message.add_reaction(DiscordReactions['crossmark'])

      except Exception as e:
        self.logger.error(f"Caught exception: {e}")
        traceback.print_exception(e)

    @client.event
    async def on_command_error(self, context: commands.Context, error) -> None:
        """
        The code in this event is executed every time a normal valid command catches an error.

        :param context: The context of the normal command that failed executing.
        :param error: The error that has been faced.
        """
        if isinstance(error, commands.CommandOnCooldown):
          minutes, seconds = divmod(error.retry_after, 60)
          hours, minutes = divmod(minutes, 60)
          hours = hours % 24
          embed = discord.Embed(
            description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B,
          )
          await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
          embed = discord.Embed(
            description="You are not the owner of the bot!", color=0xE02B2B
          )
          await context.send(embed=embed)
          if context.guild:
            self.logger.warning(
              f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
            )
          else:
            self.logger.warning(
              f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
            )
        elif isinstance(error, commands.MissingPermissions):
          embed = discord.Embed(
            description="You are missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to execute this command!",
            color=0xE02B2B,
          )
          await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
          embed = discord.Embed(
            description="I am missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to fully perform this command!",
            color=0xE02B2B,
          )
          await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
          embed = discord.Embed(
            title="Error!",
            # We need to capitalize because the command arguments have no capital letter in the code and they are the first word in the error message.
            description=str(error).capitalize(),
            color=0xE02B2B,
          )
          await context.send(embed=embed)
        else:
          raise error

async def main():
  bot = DiscordBot()
  try:
    # run the bot
    await bot.start(token=TOKEN, reconnect=True)
  except KeyboardInterrupt | asyncio.CancelledError:
    # handle keyboard interrupt
    await bot.close()
    await bot.connections.db.connection.close()
    quit()
  except Exception as e:
    # handle other exceptions
    bot.logger.error(f"An error occurred: {e}")
    traceback.print_exception(e)
    quit()

asyncio.run(main())
