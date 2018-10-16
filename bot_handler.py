import requests, asyncio, aiohttp

class BotHandler:
    def __init__(self, token):
        self._token = token
        self._url = "https://api.telegram.org/bot{}/".format(self._token)
        self._offset = None

#   Offset getter and setter #

    def get_offset(self):
        """
        Returns offset
        """
        return self._offset

    def set_offset(self, offset):
        """
        Sets offset to a new value
        """
        self._offset = offset

#   Important part #

    def get_update(self):
        """
        Returns update via getUpdates request
        Sets offset + 1
        Timeout 20
        """
        while True:
            response = requests.get(self._url + "getUpdates", {'offset': self._offset, 'timeout': 20})
            print('Updating')  # testing reasons
            update = response.json()['result']
            if update == []:
                pass
            else:
                self._offset = update[-1]['update_id'] + 1
                return update

    def send_message(self, text, chat_id, user_id):
        """
        Sends message via sendMessage request
        text = any string (Markdown is on)
        chat and user id - send to who
        """
        response = requests.post(self._url + "sendMessage", {'text': text, 'chat_id': chat_id, 'from': user_id, 'parse_mode': 'Markdown'})
        return response

    def send_messages(self, messages):
        for message in messages:
            self.send_message(message.text, message.chat_id, message.player_id)

    async def send_message_async(self, text, chat_id, user_id):
        async with aiohttp.ClientSession() as session:
            await session.post(self._url + "sendMessage", json={'text': text, 'chat_id': chat_id, 'from': user_id, 'parse_mode': 'Markdown'})

    async def prepare_message_send(self, messages):
        lst2 = (self.send_message_async(message.text, message.chat_id,
                                   message.player_id) for message in messages)
        await asyncio.gather(*lst2)

    def send_messages_async(self, messages):
        asyncio.run(self.prepare_message_send(messages))


class Message:
    def __init__(self, message):
        self._message = message
        self._message_types = ['text', 'sticker', 'photo', 'document', 'video', 'audio', 'voice',
                               'video_note', 'contact', 'location', 'venue', 'game', 'invoice']

    def get_message_body(self):
        """
        Returns message body
        """
        return self._message

    def get_message_id(self):
        """
        Returns message id
        """
        return self._message['message_id']

    def get_type(self):
        """
        Returns message type
        """
        for message_type in self._message_types:
            if message_type in self._message:
                return message_type

    def get_content(self):
        """
        Returns message content
        """
        return self._message[self.get_type()]

    def get_chat_id(self):
        """
        Returns message chat id
        """
        return self._message['chat']['id']

    def get_user_id(self):
        """
        Returns message user id
        """
        return self._message['from']


