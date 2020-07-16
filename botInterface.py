
# * things that are used to interact with the bot * #

class Payload:

    def __init__(self, source, messages, isTaskMaker = False, 
                taskDuration = None, onCompleteFunc = None, onCompleteArgs = None):
        self.source = source
        self.messages = messages
        self.isTaskMaker = isTaskMaker
        self.taskDuration = taskDuration
        self.onCompleteFunc = onCompleteFunc
        self.onCompleteArgs = onCompleteArgs

    def __str__(self):
        return 'This is a bot payload originating from %s' % self.source

def payload_manage(pload):
    # We unpack the messages into a single string:
    bot_message = ''
    for sub_message in pload.messages:
        bot_message = bot_message + sub_message + '\n' 
    return bot_message[:-1] # gets rid of the final linebreak