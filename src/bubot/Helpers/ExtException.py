import json
from os import path
import sys
import traceback

# 3xxx - Ошибки в нашем коде
# 4xxx - Ошибки вызванные некорректными действиями пользователей
# 5xxx - Ошибки вызванные временной недоступностью функционала,повторный вызов с теми же параметрами может быть успешным
# 6xxx - Ошибки во внешних сервисах и библиотеках
# 8xxx - Запросы не реализованного, но потонциально интересного функционала
# 9xxx - Обертка над стандартными ошибками для испльзования в коде

codes = {
    "3000": {"en": "Unknown error"},
    "3100": {"en": "Handler not found"},
    "4000": {"en": "Unknown error"},
    "4011": {"en": "Unauthorized"},
    "4031": {"en": "Access denied", "ru": "Отказано в доступе"},
    "4039": {"en": "Account not specified", "ru": "Не указан аккаунт"},
    "4010": {"en": "Unable to save settings", "ru": "Невозможно сохранить настройки"},
    "4200": {"en": "Required details are missing", "ru": "Не заполнен обязательный реквизит"},
    "5000": {"en": "Unknown error"},
    "6000": {"en": "Unknown error"},
    "8000": {"en": "Unknown error"},
    "9010": {"en": "KeyError"},
    "9011": {"en": "InvalidId"}
}

http_codes = {
    "4011": 401,
    "4031": 403,
    "4039": 403
}


class ExtException(Exception):
    def __init__(self, *args, **kwargs):
        self.code = 3000
        self.skip_traceback = kwargs.get('skip_traceback', 0)
        self.message = ''
        self.detail = ''
        self.action = ''
        self.dump = {}
        self.stack = []
        self.new_msg = False
        parent = kwargs.get('parent')
        if parent and isinstance(parent, ExtException):  # прокидываем ошибку наверх
            self.add_parent_to_stack(parent)
            self.message = parent.message
            self.code = parent.code
            self.detail = parent.detail
            self.new_msg = bool(kwargs.get('message'))
        self.init_from_dict(kwargs)
        if parent and isinstance(parent, Exception) and not isinstance(parent, ExtException):
            self.code = 3000
            self.message = self.get_msg_by_code(self.code)
            self.detail = str(parent)
            self.add_sys_exc_to_stack()
        if args:
            if isinstance(args[0], str):
                self.new_msg = True
                self.message = args[0]
            elif isinstance(args[0], int):
                self.new_msg = True
                self.message = self.get_msg_by_code(args[0])
                self.code = args[0]
            else:
                raise Exception(f'Not supported mode - ExtException({type(args[0])})')
        if not self.stack:
            self.add_sys_exc_to_stack()
        pass

    def add_parent_to_stack(self, parent):
        if not isinstance(parent, ExtException):
            return None
        self.stack += parent.stack
        if not parent.action:
            return
        parent.dump['action'] = parent.action
        if not self.stack:
            data = self.get_sys_exc_info()
            if data:
                parent.dump['traceback'] = data['traceback']

        if parent.new_msg:
            parent.dump['message'] = parent.message
            if parent.detail:
                parent.dump['detail'] = parent.detail
        self.stack.append(parent.dump)

    def add_sys_exc_to_stack(self):
        data = self.get_sys_exc_info()
        if not data:
            return
        data['action'] = self.action
        self.stack.append(data)

    def get_sys_exc_info(self):
        exc_info = sys.exc_info()
        if exc_info[2] is None:
            return None
        last_call = traceback.extract_tb(exc_info[2], limit=self.skip_traceback + 1)
        last_call = last_call[self.skip_traceback]
        return {
            'message': exc_info[0].__name__,
            'detail': str(exc_info[1]),
            'traceback': f'{path.basename(last_call.filename)}, {last_call.name}, line {last_call.lineno}'
        }

    def init_from_dict(self, data):
        for field in ['code', 'message', 'detail', 'action', 'dump', 'stack']:
            if field in data:
                setattr(self, field, data[field])

    @property
    def title(self):
        if self.detail:
            return f'{self.code}: {self.message} - {self.detail}'
        return f'{self.code}: {self.message}'

    def __str__(self):
        res = f'ExtException {self.title}'
        if self.dump:
            res += f'\n  Dump: action={self.action}; '
            for elem in self.dump:
                res += f'{elem}={self.dump[elem]}; '
        if self.stack:
            res += '\n  Stack:'
            for stack in self.stack:
                _action = stack.get('action', '')
                if _action:
                    res += f'\n  - {_action}: '
                    for elem in stack:
                        if elem != 'action':
                            res += f'{elem}={stack[elem]}; '
        return res

    def dump(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self):
        return {
            'name': 'ExtException',
            'message': self.message,
            'detail': self.detail,
            'code': self.code,
            'action': self.action,
            'dump': self.dump,
            'stack': self.stack
        }

    @classmethod
    def get_msg_by_code(cls, code, **kwargs):
        _error = codes.get(str(code), {'en': 'Unknown error'})
        _lang = kwargs.get('lang', 'en')
        return _error[_lang]

    def get_http_code(self):
        return http_codes.get(str(self.code), 500)
