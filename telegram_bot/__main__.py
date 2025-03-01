import asyncio
import logging
import sys

from telegram_bot.config.config import dp, bot, ColoredFormatter
from telegram_bot.handlers.start import router as start_router


async def main() -> None:
    dp.include_router(start_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger().handlers[0].setFormatter(ColoredFormatter())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")
