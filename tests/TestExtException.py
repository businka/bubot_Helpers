import unittest
from bubot.Helpers.ExtException import ExtException


class TestExtException(unittest.TestCase):
    def test_raise_from_other(self):
        a = []
        err3 = None
        try:
            try:
                try:
                    b = a[2]
                except Exception:
                    err1 = ExtException('msg1', action='action1')
                    raise err1
            except ExtException as err:
                err2 = ExtException('msg2', action='action2', parent=err)
                raise err2
        except ExtException as err:
            err3 = ExtException(action='action3', parent=err)
        self.assertEqual(3, len(err3.stack))
        self.assertEqual('IndexError', err3.stack[0]['msg'])
        self.assertEqual('msg2', err3.msg)
        print(err3)
        pass

    def test_raise(self):
        err3 = None
        try:
            try:
                err1 = ExtException('msg1', action='action1')
                raise err1
            except ExtException as err:
                err2 = ExtException('msg2', action='action2', parent=err)
                raise err2
        except ExtException as err:
            err3 = ExtException(action='action3', parent=err)
        self.assertEqual(2, len(err3.stack))
        self.assertEqual('msg1', err3.stack[0]['msg'])
        self.assertEqual('msg2', err3.msg)
        print(err3)