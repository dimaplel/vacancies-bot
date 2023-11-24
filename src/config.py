import json

from enum import StrEnum

class ConfigField(StrEnum):
    BOT_TOKEN = "bot.token",
    SQL_TOKEN = "sql.main_token"

class Config:
    def __init__(self, filepath: str) -> None:
        with open(filepath) as f:
            self.file = json.load(f)
    
    def get_field(self, field: ConfigField):
        keys = field.value.split('.')  # Split the field string into nested keys
        value = self.file
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return ""
        return value