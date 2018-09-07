import requests

class BotHandler:
    def __init__(self, token):
        self._token = token
        self._url = "https://api.telegram.org/bot{}/".format(self._token)
        self._offset = None

    def get_update_from(self):
        response = requests.get(self._url + "getUpdates", {'offset': self._offset, 'timeout': 100})
        update = response.json()['result']
        if update != []:
            self._offset = update[-1].get('update_id') + 1
            return update
        else:
            self.get_update_from()

    def get_last_message(self):
        messages = self.get_update_from()
        if messages != []:
            last_message = messages[-1].get('message')
            return last_message
        else:
            self.get_last_message()

    def get_offset(self):
        return self._offset

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

    def get_message_body(self):
        return self._message

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


