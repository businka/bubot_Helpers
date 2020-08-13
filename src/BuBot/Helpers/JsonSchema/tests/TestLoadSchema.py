import unittest
from BuBot.Helpers.JsonSchema.JsonSchema4 import JsonSchema4


class TestLoadSchema(unittest.TestCase):

    def test_load_schema(self):
        schema = JsonSchema4()
