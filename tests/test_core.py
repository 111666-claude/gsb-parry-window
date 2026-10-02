import unittest

from parry.core import Parry


class BasicTest(unittest.TestCase):
    def test_not_active_before_press(self):
        self.assertFalse(Parry(200, 1000, 30).active(0))

    def test_press_opens_window(self):
        parry = Parry(200, 1000, 30)
        self.assertTrue(parry.press(0))
        self.assertTrue(parry.active(0))

    def test_attack_without_press_is_taken(self):
        taken, refund = Parry(200, 1000, 30).incoming(100, 0)
        self.assertEqual((taken, refund), (100, 0))

    def test_refund_pct_is_stored(self):
        self.assertEqual(Parry(200, 1000, 30).refund_pct, 30)

    def test_work_starts_at_zero(self):
        self.assertEqual(Parry(200, 1000, 30).work_count(), 0)


if __name__ == "__main__":
    unittest.main()
