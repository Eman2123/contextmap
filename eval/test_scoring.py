from eval.scoring import is_correct


def test_exact_code_is_correct():
    assert is_correct("ZL-3B9", "ZL-3B9")


def test_code_inside_sentence_is_correct():
    assert is_correct("The access code is ZL-3B9.", "ZL-3B9")


def test_near_miss_is_wrong():
    assert not is_correct("ZL-3B0", "ZL-3B9")


def test_refusal_is_wrong():
    assert not is_correct("The document does not mention a code.", "ZL-3B9")


def test_case_is_ignored():
    assert is_correct("zl-3b9", "ZL-3B9")
