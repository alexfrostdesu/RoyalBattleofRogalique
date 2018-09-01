class PrintMessage:
    def __init__(self, code, object=None, amount=-1, target=None):
        if object.__class__.__name__ == 'Character' or object.__class__.__bases__[0].__name__ == 'Character':
            self._character = object.get_class()
        elif object.__class__.__name__ == 'Item' or object.__class__.__bases__[0].__name__ == 'Item':
            self._item = object.get_name()
        if amount >= 0:
            self._amount = str(round(amount, 1))
        if target.__class__.__name__ == 'Character' or target.__class__.__bases__[0].__name__ == 'Character':
            self._target = target.get_class()
        with open('all_messages.txt') as msg_list:
            all_messages = dict(x.rstrip().split(':') for x in msg_list)
        print(eval(all_messages[code]))