#!/usr/bin/python3

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
DATA = OrderedDict()


def get_args(text):
    return ' '.join(text.split()[1:])


def start(bot, update):
    user = update.message.from_user
    logger.info('User %s  started a conversation' % user.first_name)
    bot.sendMessage(update.message.chat_id,
                    text=
                    "Hi!"
                    "\nMy name is Bonkie."
                    "\nI can help you keep track of your fitness progress!"
                    "\nUse /starttraining to begin logging a training."
                    "\nYou can cancel the conversation at any time using /cancel.")


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    bot.sendMessage(update.message.chat_id,
                    text='Cancelled input')

    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def start_training(bot, update):
    user = update.message.from_user
    logger.info("User %s started a training session."
                "\nYou can cancel this at any time using /cancel." % user.first_name)
    DATA[update.message.chat_id] = OrderedDict()
    DATA[update.message.chat_id]['id'] = uuid.uuid4().__str__()
    DATA[update.message.chat_id]['name'] = user.first_name + ' ' + user.last_name
    DATA[update.message.chat_id]['date'] = ''
    DATA[update.message.chat_id]['location'] = ''
    DATA[update.message.chat_id]['order'] = []
    DATA[update.message.chat_id]['set'] = []
    DATA[update.message.chat_id]['superset'] = []
    bot.sendMessage(update.message.chat_id,
                    text="What date whould you like to use?"
                         "\nSend /today to use today's date, or enter a custom date (dd-mm-yyyy).")
    return DATE


def use_today(bot, update):
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    logger.info("Using today's date (%s)" % today)
    DATA[update.message.chat_id]['date'] = today
    bot.sendMessage(update.message.chat_id,
                    text="Using today's date (%s)"
                         "\n\nWould you like to save your training location? send your location or /skip." % today)
    return LOCATION


def use_date(bot, update):
    date = update.message.text
    logger.info("Set date to '%s'" % date)
    DATA[update.message.chat_id]['date'] = date
    bot.sendMessage(update.message.chat_id,
                    text="Using '%s' as date."
                         "\n\nWould you like to save your training location? send your location or /skip." % date)
    return LOCATION


def use_location(bot, update):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f"
                % (user.first_name, user_location.latitude, user_location.longitude))
    DATA[update.message.chat_id]['location'] = (user_location.latitude, user_location.longitude)
    bot.sendMessage(update.message.chat_id,
                    text='Training started!'
                         '\nUse /set to start a set, or /superset to start a superset.')
    return IN_TRAINING


def skip_location(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a location." % user.first_name)
    DATA[update.message.chat_id]['location'] = None
    bot.sendMessage(update.message.chat_id,
                    text="Training started!"
                         "\nUse /set to start a set, or /superset to start a superset."
                         "\nYou can end the training using /endtraining.")
    return IN_TRAINING


def start_set(bot, update):
    user = update.message.from_user
    message = update.message.text
    exercise = get_args(message)
    if exercise:
        logger.info("user %s started a set '%s'. " % (user.first_name, exercise))
        DATA[update.message.chat_id]['set'].append(exercise)
        DATA[update.message.chat_id]['order'].append(exercise)
        bot.sendMessage(update.message.chat_id,
                        text="Set '%s' started!"
                             "\nPlease provide the number of reps and the load of the exercise as follows:"
                             "\n (reps x load)"
                             "\nYou can use /undo to remove the last entry "
                             "or use /endset to end the set." % exercise)
        return IN_SET
    else:
        logger.info("user %s started a set without name. " % user.first_name)
        bot.sendMessage(update.message.chat_id,
                        text="please provide the name of the exercise:")
        return SET_NAME


def set_name(bot, update):
    exercise = update.message.text
    logger.info("Exercise name set to '%s'" % exercise)
    DATA[update.message.chat_id]['set'].append(exercise)
    DATA[update.message.chat_id]['order'].append(exercise)
    bot.sendMessage(update.message.chat_id,
                    text="Set '%s' started!"
                         "\nplease provide the number of reps and the load of the exercise as follows:"
                         "\n (reps x load)"
                         "\nYou can use /undo to remove the last entry "
                         "or use /endset to end the set." % exercise)
    return IN_SET


def handle_set(bot, update):
    user = update.message.from_user
    message = update.message.text
    reps, weight = [i.strip() for i in message.split('x')]
    logger.info("User %s sent '%s'" % (user.first_name, message))
    DATA[update.message.chat_id]['set'].append((reps, weight))
    bot.sendMessage(update.message.chat_id,
                    text="reps: %s"
                         "\nload: %s" % (reps, weight))
    return IN_SET


def end_set(bot, update):
    user = update.message.from_user
    logger.info("User %s ended set" % user.first_name)
    bot.sendMessage(update.message.chat_id,
                    text='ended set!')
    return IN_TRAINING


def start_superset(bot, update):
    user = update.message.from_user
    message = update.message.text
    args = get_args(message)
    if args:
        exercises = ', '.join(['{}. {}'.format(i+1, j.strip()) for i, j in enumerate(args.split(','))])
        logger.info("user %s started a superset '%s'. " % user.first_name, exercises)
        DATA[update.message.chat_id]['superset'].append(exercises)
        DATA[update.message.chat_id]['order'].append(exercises)
        bot.sendMessage(update.message.chat_id,
                        text="Superet '%s' started!"
                             "\nPlease provide the number of reps and the load of the exercise as follows:"
                             "\n (reps x load) "
                             "\nYou can use /undo to remove the last entry "
                             "or use /endset to end the set." % exercises)
        return IN_SUPERSET
    else:
        logger.info("user %s started a superset without name. " % user.first_name)
        bot.sendMessage(update.message.chat_id,
                        text="please provide the names of the exercises, seperated using a comma.")
        return SUPERSET_NAME


def superset_name(bot, update):
    message = update.message.text
    exercises = ', '.join(['{}. {}'.format(i + 1, j.strip()) for i, j in enumerate(message.split(','))])
    logger.info("Exercise names set to '%s'" % exercises)
    DATA[update.message.chat_id]['superset'].append(exercises)
    DATA[update.message.chat_id]['order'].append(exercises)
    bot.sendMessage(update.message.chat_id,
                    text="Superet '%s' started!"
                         "\nPlease provide the number of reps and the load of the exercise as follows:"
                         "\n (reps x load)"
                         "\nYou can use /undo to remove the last entry "
                         "or use /endset to end the current set." % exercises)
    return IN_SUPERSET


def handle_superset(bot, update):
    user = update.message.from_user
    message = update.message.text
    reps, weight = [i.strip() for i in message.split('x')]
    logger.info("User %s sent '%s'" % (user.first_name, message))
    DATA[update.message.chat_id]['superset'].append((reps, weight))
    bot.sendMessage(update.message.chat_id,
                    text="reps: %s"
                         "\nload: %s" % (reps, weight))
    return IN_SUPERSET


def end_superset(bot, update):
    user = update.message.from_user
    logger.info("User %s ended superset" % user.first_name)
    bot.sendMessage(update.message.chat_id,
                    text='ended superset!')
    return IN_TRAINING


def set_undo(bot, update):
    user = update.message.from_user
    logger.info("User %s undid last entry'" % user.first_name)
    DATA[update.message.chat_id]['set'] = DATA[update.message.chat_id]['set'][:-1]
    bot.sendMessage(update.message.chat_id,
                    text="Removed last entry")
    return IN_SET


def superset_undo(bot, update):
    user = update.message.from_user
    logger.info("User %s undid last entry'" % user.first_name)
    DATA[update.message.chat_id]['superset'] = DATA[update.message.chat_id]['superset'][:-1]
    bot.sendMessage(update.message.chat_id,
                    text="Removed last entry")
    return IN_SUPERSET


def end_training(bot, update):
    reply_keyboard = [['yes', 'no']]
    user = update.message.from_user
    logger.info("User %s ended training" % user.first_name)
    bot.sendMessage(update.message.chat_id,
                    text='ended training!'
                    '\nDo you wish to save this training? ( Yes | No )',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SAVE


def save_exercise(bot, update):
    user = update.message.from_user
    message = update.message.text
    logger.info("User %s sent '%s'" % (user.first_name, message))

    bot.sendMessage(update.message.chat_id,
                    text=format_data(DATA[update.message.chat_id]))
    return ConversationHandler.END


def format_data(dct):

    exercises = format_multiple_sets(dct['set'], dct['superset'])
    txt = ''
    for ex in dct['order']:
        current = [i for i in exercises if i[0] == ex][0]
        if ',' in current[0]:
            txt += format_superset(current) + '\n'
        else:
            txt += format_set(current) + '\n'
    txtmessage = 'TRAINING\n{}\n\n{}'.format(dct['date'],txt)
    return txtmessage


def format_set(lst):
    name = lst[0]
    repload = '\n'.join(['{} x {}'.format(*s) for s in lst[1:]])
    txt = '{}\n{}'.format(name, repload)
    return txt


def format_superset(lst):
    def split_seq(iterable, size):
        it = iter(iterable)
        item = list(itertools.islice(it, size))
        while item:
            yield item
            item = list(itertools.islice(it, size))

    names = lst[0].split(',')
    nExercises = len(names)
    splitted = list(split_seq(lst[1:], nExercises))
    txt = ''
    for i in range(nExercises):
        txt += '{}\n'.format(names[i].strip()) + '\n'.join(['{} x {}'.format(*s[i]) for s in splitted]) + '\n'
    return txt


def format_multiple_sets(set_lst, superset_lst):

    lst = set_lst + superset_lst
    output = OrderedDict()
    key = ''
    for i in lst:
        if type(i) is str:
            key = i
            output[key] = list()
        else:
            output[key].append(i)
    output2 = [[i] + j for i, j in output.items()]
    return output2


class exercise:

    def __init__(self, name, units='kilogram'):
        self.id = str(uuid.uuid4())
        self.name = name
        self.units = units
        self.reps = []
        self.load = []

    def __repr__(self):
        stress = ', '.join(['{} x {}'.format(r, l) for r, l in zip(self.reps, self.load)])
        return '<{} ({})>'.format(self.name, stress)

    def add_set(self, reps, load):
        self.reps.append(reps)
        self.load.append(load)

    def add_multiple_sets(self, sets, reps, load):
        for i in range(sets):
            self.add_set(reps, load)

    def undo_set(self):
        self.reps.__delitem__(-1)
        self.load.__delitem__(-1)

    def export(self):
        output = []
        for r, l in zip(self.reps, self.load):
            row = OrderedDict()
            row['id'] = self.id
            row['name'] = self.name
            row['reps'] = r
            row['load'] = l
            row['units'] = self.units3
            output.append(row)

        return output

class superset:

    def __init__(self, names, delimiter=',', units='kilogram'):
        self.id = str(uuid.uuid4())
        self.order = [n.strip() for n in names.split(delimiter)]
        self.exercises = [exercise(n) for n in self.order]
        self.count = 0

    def add_set(self, reps, load):
        self.exercises[self.count].add_set(reps, load)
        self.count += 1

    def undo_set(self):
        self.count -= 1  # ToDo: build in assertion that doesnt go negative
        self.exercises[self.count].undo_set()


class training:

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.date = None
        self.location = None

        self.exercises = []
        self.supersets = []
        self.order = []

    def set_date(self, date):
        self.date = date

    def set_location(self, lat, lon):
        self.location = (lat, lon)

    def export(self):
        output = []
        return output




if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    training_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('starttraining', start_training)],

        states={
            DATE: [CommandHandler('today', use_today),
                   RegexHandler('\d\d-\d\d-\d\d\d\d', use_date)],

            LOCATION: [MessageHandler([Filters.location], use_location),
                       CommandHandler('skip', skip_location)],

            IN_TRAINING: [CommandHandler('set', start_set),
                          CommandHandler('superset',start_superset),
                          CommandHandler('endtraining', end_training)],

            SET_NAME: [RegexHandler("(.*?)", set_name)],

            SUPERSET_NAME: [RegexHandler("(.*?)", superset_name)],

            IN_SET: [RegexHandler("(.*\d) *x *(.*\d)", handle_set),
                     CommandHandler('endset', end_set),
                     CommandHandler('undo', set_undo)],

            IN_SUPERSET: [RegexHandler("(.*\d) *x *(.*\d)", handle_superset),
                          CommandHandler('endset', end_superset),
                          CommandHandler('undo', superset_undo)],

            SAVE: [RegexHandler("yes|no", save_exercise)]
                },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(training_conv_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_error_handler(error)

    logger.info('starting BonkieBot')
    updater.start_polling()