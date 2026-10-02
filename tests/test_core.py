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


class WindowEdgeTest(unittest.TestCase):
    def test_last_frame_is_valid(self):
        parry = fresh()
        parry.press(0)
        self.assertTrue(parry.active(200))
        self.assertEqual(parry.incoming(100, 200), (0, 30))

    def test_frame_after_window_is_taken(self):
        parry = fresh()
        parry.press(0)
        self.assertFalse(parry.active(201))
        self.assertEqual(parry.incoming(100, 201), (100, 0))


class SingleConsumeTest(unittest.TestCase):
    def test_one_window_parries_once(self):
        parry = fresh()
        parry.press(0)
        self.assertEqual(parry.incoming(100, 50), (0, 30))
        self.assertEqual(parry.incoming(100, 100), (100, 0))

    def test_refund_uses_full_damage(self):
        parry = fresh()
        parry.press(0)
        self.assertEqual(parry.incoming(250, 50)[1], 75)

    def test_refund_and_taken_non_negative(self):
        parry = Parry(200, 1000, 30)
        for damage in (0, 1, 33, 100, 999):
            parry = Parry(200, 1000, 30)
            parry.press(0)
            taken, refund = parry.incoming(damage, 5)
            self.assertGreaterEqual(taken, 0)
            self.assertGreaterEqual(refund, 0)
            self.assertEqual(refund, damage * 30 // 100)


class CooldownTest(unittest.TestCase):
    def test_press_blocked_right_after_parry(self):
        parry = fresh()
        parry.press(0)
        parry.incoming(100, 50)
        self.assertFalse(parry.press(60))

    def test_press_blocked_during_cooldown_and_allowed_after(self):
        parry = fresh()
        parry.press(0)
        parry.incoming(100, 50)
        self.assertFalse(parry.press(1049))
        self.assertTrue(parry.press(1050))

    def test_missed_window_enters_cooldown(self):
        parry = fresh()
        parry.press(0)
        self.assertEqual(parry.incoming(100, 250), (100, 0))
        self.assertFalse(parry.press(300))


class RefreshTest(unittest.TestCase):
    def test_repeat_press_does_not_refresh_window(self):
        parry = fresh()
        self.assertTrue(parry.press(0))
        self.assertFalse(parry.press(100))
        self.assertFalse(parry.active(201))
        self.assertEqual(parry.incoming(100, 250), (100, 0))


class SourceIsolationTest(unittest.TestCase):
    def test_window_does_not_leak_between_sources(self):
        parry = fresh()
        parry.press(0, source="skill")
        self.assertEqual(parry.incoming(100, 100, source="gear"), (100, 0))
        self.assertEqual(parry.incoming(100, 100, source="skill"), (0, 30))

    def test_cooldown_is_per_source(self):
        parry = fresh()
        parry.press(0, source="skill")
        parry.incoming(100, 50, source="skill")
        self.assertFalse(parry.press(60, source="skill"))
        self.assertTrue(parry.press(60, source="gear"))

    def test_sources_are_independent_repeatedly(self):
        parry = fresh()
        parry.press(0, source="a")
        parry.press(0, source="b")
        self.assertEqual(parry.incoming(100, 50, source="a"), (0, 30))
        self.assertEqual(parry.incoming(100, 50, source="b"), (0, 30))
        self.assertFalse(parry.press(60, source="a"))
        self.assertFalse(parry.press(60, source="b"))


class IdempotencyTest(unittest.TestCase):
    def test_same_event_settles_once(self):
        parry = fresh()
        parry.press(0)
        first = parry.incoming(100, 50, event_id="e1")
        second = parry.incoming(100, 999, event_id="e1")
        self.assertEqual(first, second)
        self.assertEqual(second, (0, 30))

    def test_duplicate_without_window_returns_first_result(self):
        parry = fresh()
        first = parry.incoming(100, 0, event_id="e1")
        parry.press(5)
        second = parry.incoming(100, 999, event_id="e1")
        self.assertEqual(first, second)
        self.assertEqual(second, (100, 0))


class DeterminismTest(unittest.TestCase):
    def test_same_sequence_gives_same_results(self):
        def run():
            parry = fresh()
            results = []
            results.append(parry.press(0, source="s1"))
            results.append(parry.incoming(100, 50, source="s1", event_id="a"))
            results.append(parry.press(60, source="s1"))
            results.append(parry.incoming(250, 70, source="s1", event_id="b"))
            results.append(parry.press(0, source="s2"))
            results.append(parry.incoming(80, 250, source="s2", event_id="c"))
            return results
        self.assertEqual(run(), run())


class ScaleTest(unittest.TestCase):
    def test_100k_hits_amortized_constant_work(self):
        parry = fresh()
        for index in range(100000):
            parry.incoming(100, index, event_id="e-%d" % index)
        self.assertLessEqual(parry.work_count(), 100000 + 5)
