from aiogram import Bot
from config import cfg

bot = Bot(token=cfg.token.get_secret_value())