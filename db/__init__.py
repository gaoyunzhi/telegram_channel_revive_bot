import traceback as tb
import yaml
import time

# feature request: customize revive interval

DEFAULT_INTERVAL = 1440

class DB(object):
    def __init__(self):
        try:
            with open('db.yaml') as f:
                self.DB = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            print(e)
            tb.print_exc()
            self.DB = {}

    def rewindPos(self, chat_id):
        self.DB[chat_id]['pos'] -= 1
        self.save()

    def iteratePos(self, chat_id):
        self.DB[chat_id]['pos'] += 1
        self.save()
        return self.DB[chat_id]['pos']

    def chatIds(self):
        return self.DB.keys()

    def ready(self, chat_id):
        return self.DB[chat_id]['last_update'] < \
            time.time() - self.DB[chat_id].get('interval', DEFAULT_INTERVAL) * 60

    def hasChatId(self, chat_id):
        return chat_id in self.DB

    def setTime(self, chat_id):
        self.DB[chat_id]['last_update'] = time.time()
        self.save()

    def addChatId(self, chat_id):
        self.DB[chat_id] = {'pos': -1, 'last_update': time.time()}
        self.save()

    def save(self):
        with open('db.yaml', 'w') as f:
            f.write(yaml.dump(self.DB, sort_keys=True, indent=2))