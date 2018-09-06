import click
import random
import math


import os
import requests
import time

#os.environ["HTTPS_PROXY"] = 'https://125.141.200.45:80'

TOKEN = os.environ["TOKEN"]

class BotHandler:
    def __init__(self, token):
        self._token = token
        self._url = "https://api.telegram.org/bot{}/".format(self._token)
        self._offset = None

    def get_update_from(self):
        response = requests.get(self._url + "getUpdates", {'offset': self._offset, 'timeout': 100})
        update = response.json()['result']
        if update:
            self._offset = update[-1].get('update_id') + 1
        return update

    def get_last_message(self):
        messages = self.get_update_from()
        last_message = messages[-1]['message']
        return last_message

    def get_last_update_id(self):
        update = self.get_update_from()
        update_id = update[-1].get('update_id')
        return update_id

    def set_offset(self, offset):
        self._offset = offset

    def send_message(self, text, chat_id):
        response = requests.post(self._url + "sendMessage", {'text': text, 'chat_id': chat_id})
        return response


class Message:
    def __init__(self, message):
        self._message = message
        self._message_types = ['text', 'sticker', 'photo', 'document','video', 'audio', 'voice',
                               'video_note', 'contact', 'location', 'venue', 'game', 'invoice']
        self._message_type = self.get_type()

    def get_message_id(self):
        return self._message['message_id']

    def get_type(self):
        """Returns type of message."""
        for message_type in self._message_types:
            if message_type in self._message:
                return message_type

    def get_content(self):
        return self._message[self.get_type()]

    def get_chat_id(self):
        return self._message['chat']['id']


# dispatcher = BotHandler(TOKEN)
# msg = Message(dispatcher.get_last_message())
# text = msg.get_content()
# id = dispatcher.get_last_update_id()
# print(text)
# print(id)

def main():
    dispatcher = BotHandler(TOKEN)
    while True:
        msg = Message(dispatcher.get_last_message())
        if msg.get_type() != 'text':
            pass
        else:
            text = msg.get_content()
            # if text == 'stop':
            #     break
            chat_id = msg.get_chat_id()
            dispatcher.send_message(text, chat_id)
            time.sleep(0.5)



if __name__ == '__main__':
    main()

# print(last_message.get_type())
#
# text = last_message.get_message_content()
# print(text)
# chat_id = last_message.get_chat_id()

# send_message(text, chat_id)