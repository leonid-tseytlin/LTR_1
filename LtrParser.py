import json
import logging

class SuParser():
    def __init__(self, key_list):
        self.key_list = key_list

    def parse(self, message):
#        logging.debug(message)
        msg_data = json.loads(message)
        logging.debug(msg_data)

        for key in self.key_list:
            if key in msg_data:
                return key, msg_data[key]

        return None