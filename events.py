class DialogMessage:
    def __init__(self, code, object=None, amount=-1, target=None):
        if object.__class__.__name__ == 'Character' or object.__class__.__bases__[0].__name__ in ('Character', 'Monster'):
            self._character = object.get_class()
        elif object.__class__.__name__ == 'Item' or object.__class__.__bases__[0].__name__ == 'Item':
            self._item = object.get_name()
        if amount >= 0:
            self._amount = str(round(amount, 1))
        if target.__class__.__name__ == 'Character' or target.__class__.__bases__[0].__name__ in ('Character', 'Monster'):
            self._target = target.get_class()
        with open('all_messages.txt') as msg_list:
            all_messages = dict(x.rstrip().split(':') for x in msg_list)
        self._message = eval(all_messages[code])

    def get_message(self):
        return self._message

    def print_message(self):
        print(self._message)