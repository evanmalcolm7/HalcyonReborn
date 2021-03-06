from time import time
from tasks import Task
from files import get_file, save_file


# * things that are used to interact with the bot * #


def region_string_to_int(region_string):
    """Converts a string '(x, y)' to a tuple (x, y)"""
    splitforms = region_string.split(',')
    nospaces = [x.replace(' ', '') for x in splitforms]
    noparens = [x.replace('(', '') for x in nospaces]
    noparens2 = [x.replace(')', '') for x in noparens]
    asints = [int(x) for x in noparens2]
    return (asints[0], asints[1])


def entity_display_to_id(entity_display):
    """Converts an entity's display name to its internal ID"""
    # * entity display will be in the form "Owners's Entity | "
    # * we need it to be in the form OWNERentity
    # first, we strip it into two words
    try:
        owner, entity = entity_display.split()
    except ValueError:  # unless it's already one word
        return entity_display
    # for owner, we remove the 's and uppercase it
    owner = owner[:-2].upper()
    # for entity, we just lowercase it
    entity = entity.lower()
    # then for the return we just combine the two
    return owner + entity


class Payload:
    '''onCompleteArgs MUST BE A LIST'''

    def __init__(self, sourceLID, messages, isTaskMaker=False,
                 taskDuration=None, onCompleteFunc=None, onCompleteArgs=[]):
        self.sourceLID = sourceLID
        self.messages = messages
        self.isTaskMaker = isTaskMaker
        self.taskDuration = taskDuration
        self.onCompleteFunc = onCompleteFunc
        self.onCompleteArgs = onCompleteArgs

    def __str__(self):
        return 'This is a bot payload originating from %s' % self.sourceLID['EID']


def payload_manage(pload):
    # check if the payload makes a task
    if pload.isTaskMaker:
        # get the source object
        sourceLID = pload.sourceLID
        sourceFile = sourceLID['LocFile']
        sourceKey = sourceLID['LocKey']
        sourceEID = sourceLID['EID']
        storageDict = get_file(sourceFile)
        source = storageDict[sourceKey].content[sourceEID]
        if source.busy:
            # check if the entity is busy
            # ? set some sort of "activetask" attribute for entities ? #
            # ? we can use that to say what, exactly, they're busy doing ? #
            return f'```{source} is busy. Use ~cancel_task "entity_name" "entity_location" to cancel the task.```'
        # else, set the source to busy
        source.busy = True
        save_file(storageDict, sourceFile)
        # get numbers of minutes since epoch (MSE) right now
        current_MSE = int(time() // 60)
        # add the duration to figure out when to trigger
        trigger_time = current_MSE + (pload.taskDuration * 60)
        # create a Task, rest is handled in tasks.py
        Task(sourceLID, trigger_time, pload.onCompleteFunc, pload.onCompleteArgs)
    # * message management and output
    # We unpack the messages into a single string:
    bot_message = '```yaml\n'  # send it as a code block
    for sub_message in pload.messages:
        bot_message = bot_message + sub_message + '\n'
    # get rid of the final linebreak and complete codeblock
    return bot_message[:-1] + '```'

# a = Payload(None, ['hi'], isTaskMaker=True,
#             taskDuration=1,onCompleteFunc=print,
#             onCompleteArgs=['yay yay yay'])

# payload_manage(a)
