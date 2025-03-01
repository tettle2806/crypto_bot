from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os
from pathlib import Path
import logging

BASE_DIR = Path(__file__).parent.parent

load_dotenv()

DB_URL = os.getenv("DB_URL")


class DbSettings(BaseSettings):
    url: str = DB_URL
    echo: bool = True


class Setting(BaseSettings):

    db_url: str = DB_URL
    db_echo: bool = False
    # db_echo: bool = True


settings = Setting()


TOKEN = os.getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m",
    }

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(message)s\033[0m"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
