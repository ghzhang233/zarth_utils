from unittest import TestCase
from zarth_utils.config import Config


class TestConfig(TestCase):
    def test_config(self):
        config = Config(default_config_dict={
            "a": "a",
            "b": {
                "c": "c",
                "d": "d",
                "e": {
                    "f": "f"
                }
            }
        })
        config.a = "A"
        config["b.c"] = "X"
        config.b.c = "Y"
        config.b["c"] = "C"
        config["b"]["d"] = "D"
        config["b"].e["f"] = "F"
        self.assertEqual(config.a, "A")
        self.assertEqual(config.b.c, "C")
        self.assertEqual(config.b.d, "D")
        self.assertEqual(config.b.e.f, "F")
        self.assertEqual(config["a"], "A")
        self.assertEqual(config["b"]["c"], "C")
        self.assertEqual(config["b"]["d"], "D")
        self.assertEqual(config["b"]["e"]["f"], "F")
        self.assertEqual(config.get("a"), "A")
        self.assertEqual(config.get("b.c"), "C")
        self.assertEqual(config.get("b.d"), "D")
        self.assertEqual(config.get("b.e.f"), "F")
        self.assertEqual(config["b"].e["f"], "F")
        self.assertEqual(config.b.e["f"], "F")
        self.assertEqual(config.b["e"].f, "F")
