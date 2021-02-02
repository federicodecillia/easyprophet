"""Tests for `easyprophet` package."""
import pytest
from easyprophet import easyprophet
from easyprophet import hello_world


def test_raises_exception_on_non_string_arguments():
    with pytest.raises(TypeError):
        hello_world.capital_case(9)


def test_create_grid():
    input_grid = {
        "model": ["m1", "m2"],
        "initial": ["cv_initial", "cv2"],
        "period": ["cv_period", "cv_period2"],
        "horizon": ["cv_horizon", "cv_horizon2"],
    }
    param_grid = list(easyprophet.create_grid(input_grid))
    assert len(param_grid) == 16
