import logging
import datetime
import itertools
from collections import OrderedDict

import uuid
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler,\
    ConversationHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKEN = '215428593:AAGl9krjx_0JxibgpyLzQfBYlgHI3PtAaxg'
SUPERSET_NAME, IN_TRAINING, DATE, LOCATION, SET_NAME, SAVE, IN_SET, IN_SUPERSET = range(8)
