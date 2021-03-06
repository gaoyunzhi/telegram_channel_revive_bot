import traceback as tb
import yaml
import time

DEFAULT_INTERVAL = 24
HOUR = 60 * 60

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
            time.time() - self.DB[chat_id].get('interval', DEFAULT_INTERVAL) * HOUR

    def setInterval(self, chat_id, hour):
        if chat_id not in self.DB:
            self.DB[chat_id] = {'pos': -1}   
        self.DB[chat_id]['interval'] = hour
        self.save()

    def setTime(self, chat_id):
        if chat_id not in self.DB:
            self.DB[chat_id] = {'pos': -1}    
        self.DB[chat_id]['last_update'] = time.time()
        self.save()

    def save(self):
        with open('db.yaml', 'w') as f:
            f.write(yaml.dump(self.DB, sort_keys=True, indent=2))