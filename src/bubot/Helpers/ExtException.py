import json
from os import path
import sys
import traceback

codes = {
    3000: "Unknown error",
    4000: "",
    4001: "Bad login or password",
    4010: "Невозможно сохранить настройки",
    5000: "",
    6000: "",
    8000: "",
}

http_codes = {
    4001: 401
}


class ExtException(Exception):
    def __init__(self, *args, **kwargs):
        self.code = 3000
        self.skip_traceback = kwargs.get('skip_traceback', 0)
        self.msg = ''
        self.detail = ''
        self.action = ''
        self.dump = {}
        self.stack = []
        self.new_msg = False
        parent = kwargs.get('parent')
        if parent and isinstance(parent, ExtException):  # прокидываем ошибку наверх
            self.add_parent_to_stack(parent)
            self.msg = parent.msg
            self.code = parent.code
            self.detail = parent.detail
            self.new_msg = bool(kwargs.get('msg'))
        self.init_from_dict(kwargs)
        if parent and isinstance(parent, Exception) and not isinstance(parent, ExtException):
            self.code = 3000
            self.msg = self.get_msg_by_code(self.code)
            self.detail = str(parent)
            self.add_sys_exc_to_stack()
        if args:
            if isinstance(args[0], str):
                self.new_msg = True
                self.msg = args[0]
            elif isinstance(args[0], int):
                self.new_msg = True
                self.msg = self.get_msg_by_code(args[0])
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
            parent.dump['msg'] = parent.msg
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
        try:
            exc_info = sys.exc_info()
            last_call = traceback.extract_tb(exc_info[2], limit=self.skip_traceback + 1)
            last_call = last_call[self.skip_traceback]
        except Exception:
            return None  # исключения не было
        # if exc_info[0] == cls:
        #     return None
        return {
            'msg': exc_info[0].__name__,
            'detail': str(exc_info[1]),
            'traceback': f'{path.basename(last_call.filename)}, {last_call.name}, line {last_call.lineno}'
        }

    def init_from_dict(self, data):
        for field in ['code', 'msg', 'detail', 'action', 'dump', 'stack']:
            if field in data:
                setattr(self, field, data[field])

    @property
    def message(self):
        if self.detail:
            return f'{self.code}: {self.msg} - {self.detail}'
        return f'{self.code}: {self.msg}'

    def __str__(self):
        res = f'ExtException {self.message}'
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
            'msg': self.msg,
            'detail': self.detail,
            'code': self.code,
            'action': self.action,
            'stack': self.stack
        }

    @classmethod
    def get_msg_by_code(cls, code):
        return codes.get(code, "Unknown error")

    def get_http_code(self):
        return http_codes.get(self.code, 500)
