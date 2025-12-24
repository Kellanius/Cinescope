import pytest


@pytest.mark.parametrize("param_a,param_b", [
    ("a1", "b1"),
    ("a2", "b2")
])
class TestMultipleParams:

    def test_params_combination(self, param_a, param_b):
        print(f"1 тест: {param_a} и {param_b}")

    def test_another_method(self, param_a, param_b):
        combined = f"{param_a}-{param_b}"
        print(f"2 тест: {combined}")
        assert len(combined) > 2


import pytest

@pytest.mark.smoke
def test_addition():
    assert 1 + 1 == 2

@pytest.mark.regression
def test_subtraction():
    assert 5 - 3 == 2

@pytest.mark.api
def test_multiplication():
    assert 2 * 3 == 6

@pytest.mark.slow
def test_division():
    assert 10 / 2 == 5
