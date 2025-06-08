import os
from typing import Tuple

import pandas as pd
import pytest


def calc(input_df: pd.DataFrame, scale: float = 2) -> pd.DataFrame:
    return input_df.copy() * scale


def get_test_file_path(filename: str) -> str:
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, filename)


@pytest.fixture
def excel_test_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    file_path = get_test_file_path("test_numbers.xlsx")

    input_df = pd.read_excel(file_path, sheet_name="inputs")
    expected_df = pd.read_excel(file_path, sheet_name="expected")

    return input_df, expected_df


def test_individual_cell_comparison(excel_test_data: Tuple[pd.DataFrame, pd.DataFrame]) -> None:
    # Arrange
    input_df, expected_df = excel_test_data
    tolerance: float = 1e-5

    # Act
    input_scaled = calc(input_df)

    # Assert
    assert (input_scaled.shape == expected_df.shape), "Input and expected data have different shapes"

    def compare_cells(idx: int, col: str) -> None:
        actual, expected = input_scaled.loc[idx, col], expected_df.loc[idx, col]

        assert type(actual) == type(expected), f"Type mismatch at row {idx}, column {col}: {type(actual)} != {type(expected)}"

        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            assert (abs(actual - expected) < tolerance), f"Mismatch at row {idx}, column {col}: {actual} != {expected}"
            return

        assert (actual == expected), f"Mismatch at row {idx}, column {col}: {actual} != {expected}"

    for col in input_scaled.columns:
        for idx in input_scaled.index:
            compare_cells(idx, col)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
