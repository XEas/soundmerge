"""Tests for the benchmark module."""

import pytest

from sound_merge.benchmark import random_coefficient, calculate_db_loss


def test_random_coefficient_range():
    """Test if random_coefficient returns a value between 0 and 1."""
    coeff = random_coefficient()
    assert 0 <= coeff <= 1


def test_calculate_db_loss_zero_percent():
    """Test if calculate_db_loss raises ValueError for 0 percent."""
    with pytest.raises(ValueError):
        calculate_db_loss(0)


def test_calculate_db_loss_valid_percent():
    """Test if calculate_db_loss returns correct value for valid percent."""
    assert calculate_db_loss(0.5) == pytest.approx(-3.0103, 0.0001)
