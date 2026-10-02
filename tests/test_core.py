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


class SourceIsolationTest(unittest.TestCase):
    def test_window_does_not_leak_across_sources(self):
        parry = fresh()
        parry.press(0, source="skill")
        taken, refund = parry.incoming(100, 100, source="gear")
        self.assertEqual((taken, refund), (100, 0))

    def test_cooldown_does_not_leak_across_sources(self):
        parry = fresh()
        parry.press(0, source="skill")
        parry.incoming(100, 50, source="skill")
        self.assertFalse(parry.press(60, source="skill"))
        self.assertTrue(parry.press(60, source="gear"))

    def test_consumption_does_not_leak_across_sources(self):
        parry = fresh()
        parry.press(0, source="skill")
        parry.press(0, source="gear")
        parry.incoming(100, 50, source="skill")
        taken, refund = parry.incoming(100, 60, source="gear")
        self.assertEqual((taken, refund), (0, 30))


class WindowStateTest(unittest.TestCase):
    def test_last_frame_of_window_is_active(self):
        parry = fresh()
        parry.press(0)
        self.assertTrue(parry.active(200))
        taken, _ = parry.incoming(100, 200)
        self.assertEqual(taken, 0)

    def test_frame_after_window_is_inactive(self):
        parry = fresh()
        parry.press(0)
        self.assertFalse(parry.active(201))

    def test_press_during_window_does_not_refresh(self):
        parry = fresh()
        self.assertTrue(parry.press(0))
        self.assertFalse(parry.press(100))
        taken, _ = parry.incoming(100, 250)
        self.assertEqual(taken, 100)

    def test_press_after_window_expired_opens_new_window(self):
        parry = fresh()
        parry.press(0)
        parry.incoming(100, 300)
        self.assertTrue(parry.press(300 + 1000))
        taken, _ = parry.incoming(100, 300 + 1000 + 200)
        self.assertEqual(taken, 0)


class SingleConsumptionTest(unittest.TestCase):
    def test_window_parries_only_once(self):
        parry = fresh()
        parry.press(0)
        first, _ = parry.incoming(100, 50)
        second, _ = parry.incoming(100, 100)
        self.assertEqual(first, 0)
        self.assertEqual(second, 100)

    def test_successful_parry_ends_window(self):
        parry = fresh()
        parry.press(0)
        parry.incoming(100, 50)
        self.assertFalse(parry.active(60))


class CooldownTest(unittest.TestCase):
    def test_press_blocked_during_cooldown(self):
        parry = fresh()
        parry.press(0)
        parry.incoming(100, 50)
        self.assertFalse(parry.press(60))

    def test_press_allowed_after_cooldown(self):
        parry = fresh()
        parry.press(0)
        parry.incoming(100, 50)
        self.assertTrue(parry.press(50 + 1000))

    def test_missed_window_enters_cooldown(self):
        parry = fresh()
        parry.press(0)
        taken, _ = parry.incoming(100, 500)
        self.assertEqual(taken, 100)
        self.assertFalse(parry.press(600))

    def test_no_window_no_cooldown(self):
        parry = fresh()
        parry.incoming(100, 0)
        self.assertTrue(parry.press(1))


class IdempotencyTest(unittest.TestCase):
    def test_same_event_id_settles_once(self):
        parry = fresh()
        parry.press(0)
        first = parry.incoming(100, 50, event_id="e1")
        second = parry.incoming(100, 50, event_id="e1")
        self.assertEqual(first, second)
        self.assertEqual(first, (0, 30))

    def test_replay_does_not_consume_window(self):
        parry = fresh()
        parry.press(0)
        parry.incoming(100, 50, event_id="e1")
        parry.incoming(100, 50, event_id="e1")
        taken, _ = parry.incoming(100, 60, event_id="e2")
        self.assertEqual(taken, 100)

    def test_repeated_sequence_is_deterministic(self):
        def run():
            parry = fresh()
            parry.press(0, source="a")
            parry.press(10, source="b")
            results = [
                parry.incoming(100, 50, source="a", event_id="e1"),
                parry.incoming(100, 60, source="b", event_id="e2"),
                parry.incoming(100, 70, source="a", event_id="e1"),
            ]
            return results

        self.assertEqual(run(), run())

    def test_taken_and_refund_never_negative(self):
        parry = fresh()
        parry.press(0)
        for index in range(100):
            taken, refund = parry.incoming(1, index, event_id="e-%d" % index)
            self.assertGreaterEqual(taken, 0)
            self.assertGreaterEqual(refund, 0)


class RefundTest(unittest.TestCase):
    def test_refund_uses_damage_times_pct_floored(self):
        parry = fresh()
        parry.press(0)
        _, refund = parry.incoming(250, 50)
        self.assertEqual(refund, 75)

    def test_refund_floors_after_multiplication(self):
        parry = Parry(200, 1000, 30)
        parry.press(0)
        _, refund = parry.incoming(10, 50)
        self.assertEqual(refund, 3)


class ScaleTest(unittest.TestCase):
    def test_work_is_constant_per_hit(self):
        parry = fresh()
        for index in range(3000):
            parry.incoming(100, index, event_id="e-%d" % index)
        self.assertLessEqual(parry.work_count(), 6000)

    def test_hundred_thousand_hits_single_pass(self):
        parry = fresh()
        for index in range(100000):
            parry.incoming(100, index, event_id="e-%d" % index)
        self.assertLessEqual(parry.work_count(), 200000)
