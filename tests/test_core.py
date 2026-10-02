import unittest

from parry.core import Parry


def fresh():
    return Parry(200, 1000, 30)


class BasicTest(unittest.TestCase):
    def test_not_active_before_press(self):
        self.assertFalse(fresh().active(0))

    def test_press_opens_window(self):
        parry = fresh()
        self.assertTrue(parry.press(0))
        self.assertTrue(parry.active(0))

    def test_attack_without_press_is_taken(self):
        taken, refund = fresh().incoming(100, 0)
        self.assertEqual((taken, refund), (100, 0))

    def test_refund_pct_is_stored(self):
        self.assertEqual(fresh().refund_pct, 30)

    def test_work_starts_at_zero(self):
        self.assertEqual(fresh().work_count(), 0)


class LedgerTest(unittest.TestCase):
    def test_sources_starts_empty(self):
        self.assertEqual(fresh().sources, {})

    def test_press_registers_source(self):
        parry = fresh()
        parry.press(0, source="gear")
        self.assertIn("gear", parry.sources)

    def test_events_are_recorded(self):
        parry = fresh()
        parry.incoming(100, 0, event_id="e1")
        self.assertTrue(parry.events)

    def test_work_grows_after_hits(self):
        parry = fresh()
        parry.incoming(100, 0, event_id="e1")
        parry.incoming(100, 1, event_id="e2")
        self.assertGreater(parry.work_count(), 0)


if __name__ == "__main__":
    unittest.main()
