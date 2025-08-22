"""
Fortran-specific test utilities and fixtures.
"""

import pytest
from pathlib import Path

from solidlsp.ls_config import Language


@pytest.fixture
def fortran_test_files():
    """Fixture providing list of Fortran test files."""
    return [
        "main.f90",
        "utils.f90", 
        "math_operations.f90",
        "data_processor.f90",
        "legacy.f"
    ]


@pytest.fixture
def expected_fortran_symbols():
    """Fixture providing expected symbols for each test file."""
    return {
        "main.f90": ["main"],
        "utils.f90": ["utils_module", "print_array", "read_config"],
        "math_operations.f90": ["math_operations", "calculate_mean", "calculate_variance", "vector_type"],
        "data_processor.f90": ["data_processor", "process_data", "data_filter", "analysis_type"],
        "legacy.f": ["legacy_routine", "legacy_function"]
    }


def check_symbol_presence(symbols, expected_names):
    """Helper function to check if expected symbols are present."""
    symbol_names = [s.get("name", "").lower() for s in symbols]
    
    found_symbols = []
    for expected in expected_names:
        if any(expected.lower() in name for name in symbol_names):
            found_symbols.append(expected)
    
    return found_symbols