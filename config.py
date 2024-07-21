import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, ChatMemberUpdated, CallbackQuery, LinkPreviewOptions
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.formatting import Text, ExpandableBlockQuote, Italic, Bold
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
import os
import json
import openai
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY") # optional
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# optional, for open-source model use with Deepinfra
SEARCH_MODEL=os.getenv("SEARCH_MODEL")
ANSWER_MODEL=os.getenv("ANSWER_MODEL")

with open("./underground_info/group_chat.json") as file:
    underground_data = json.load(file)
UNDERGROUND_CHAT_ID = underground_data.get("CHAT_ID")
UNDERGROUND_CHAT_INVITE = underground_data.get("CHAT_INVITE")
with open("./underground_info/admins.json") as file:
    ADMINS = json.load(file)

with open("./gspread_handler/url.txt") as file:
    SHEET_URL = file.read().strip()

with open("./prompts/non-found.txt") as file:
    NON_FOUND_PROMPT = file.read()
with open("./prompts/search.txt") as file:
    SEARCH_PROMPT = file.read()
with open("./prompts/summarize.txt") as file:
    SUMMARIZE_PROMPT = file.read()


scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('./gspread_handler/key.json', scopes=scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url(SHEET_URL)
worksheet = spreadsheet.sheet1


with open("./underground_info/mentions.json", "r") as file:
    MENTIONS = json.load(file)

deepinfra_client = openai.OpenAI(
        api_key=DEEPINFRA_API_KEY,
        base_url="https://api.deepinfra.com/v1/openai")

openai_client = openai.OpenAI()
openai.api_key = OPENAI_API_KEY

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()
dp.callback_query.middleware(CallbackAnswerMiddleware(pre=True))

text = State()