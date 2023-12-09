from aiogram.utils.keyboard import ReplyKeyboardBuilder

class CreationMenuKeyboard:
    def __get__(self, instance, owner):
        return ReplyKeyboardBuilder()