from tristan.mixed_court import CourtCase, evaluate_court


def test_mixed_court_metrics():
    m = evaluate_court([
        CourtCase("p1", True, True, True),
        CourtCase("p2", True, False, None),
        CourtCase("n1", False, False, None),
        CourtCase("n2", False, True, False),
    ])
    assert (m.tp, m.tn, m.fp, m.fn) == (1, 1, 1, 1)
    assert m.precision == 0.5
    assert m.recall == 0.5
    assert m.fpr == 0.5
    assert m.fnr == 0.5
    assert m.mechanism_accuracy == 0.5


def test_court_no_negative_controls_has_unknown_fpr():
    m = evaluate_court([CourtCase("p", True, True, True)])
    assert m.fpr is None
