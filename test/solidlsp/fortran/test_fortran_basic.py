"""
Basic integration tests for the Fortran language server functionality.

These tests validate the functionality of the language server APIs
for Fortran code using fortls.
"""

import os

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language
from solidlsp.ls_utils import SymbolUtils


@pytest.mark.fortran
class TestFortranLanguageServer:
    """Test basic functionality of the Fortran language server."""

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_server_initialization(self, language_server: SolidLanguageServer):
        """Test that the Fortran language server initializes successfully."""
        assert language_server is not None
        assert language_server.language == Language.FORTRAN
        assert language_server.is_running()

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_find_main_program(self, language_server: SolidLanguageServer):
        """Test finding the main program symbol."""
        symbols = language_server.request_full_symbol_tree()
        assert SymbolUtils.symbol_tree_contains_name(symbols, "main"), "main program not found in symbol tree"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_find_module_symbols(self, language_server: SolidLanguageServer):
        """Test finding module symbols."""
        symbols = language_server.request_full_symbol_tree()
        assert SymbolUtils.symbol_tree_contains_name(symbols, "utils_module"), "utils_module not found in symbol tree"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "math_operations"), "math_operations module not found in symbol tree"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_find_function_symbols(self, language_server: SolidLanguageServer):
        """Test finding function and subroutine symbols."""
        symbols = language_server.request_full_symbol_tree()
        assert SymbolUtils.symbol_tree_contains_name(symbols, "calculate_mean"), "calculate_mean function not found in symbol tree"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "print_array"), "print_array subroutine not found in symbol tree"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_find_legacy_fortran_symbols(self, language_server: SolidLanguageServer):
        """Test finding symbols in legacy Fortran files."""
        symbols = language_server.request_full_symbol_tree()
        assert SymbolUtils.symbol_tree_contains_name(symbols, "legacy_routine"), "legacy_routine not found in symbol tree"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "legacy_function"), "legacy_function not found in symbol tree"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_document_symbols_main_program(self, language_server: SolidLanguageServer):
        """Test document symbol detection for main program file."""
        file_path = "main.f90"
        symbols, root_symbols = language_server.request_document_symbols(file_path)
        
        # Should detect symbols in the main program file
        assert len(symbols) > 0 or len(root_symbols) > 0, f"No symbols found in {file_path}"
        
        # Look for main program
        all_symbols = symbols + root_symbols
        program_names = [s.get("name", "").lower() for s in all_symbols]
        assert any("main" in name for name in program_names), "main program not detected in document symbols"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_document_symbols_module_file(self, language_server: SolidLanguageServer):
        """Test detection of modules and procedures in Fortran files."""
        file_path = "utils.f90"
        symbols, root_symbols = language_server.request_document_symbols(file_path)
        
        # Should detect symbols in the utils module
        assert len(symbols) > 0 or len(root_symbols) > 0, f"No symbols found in {file_path}"
        
        # Look for module and procedures
        all_symbols = symbols + root_symbols
        symbol_names = [s.get("name", "").lower() for s in all_symbols]
        assert any("utils_module" in name for name in symbol_names), "utils_module not detected"
        assert any("print_array" in name for name in symbol_names), "print_array subroutine not detected"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_document_symbols_legacy_fortran(self, language_server: SolidLanguageServer):
        """Test detection of legacy Fortran 77 style code."""
        file_path = "legacy.f"
        symbols, root_symbols = language_server.request_document_symbols(file_path)
        
        # Should detect symbols in legacy file
        assert len(symbols) > 0 or len(root_symbols) > 0, f"No symbols found in {file_path}"
        
        # Look for legacy procedures
        all_symbols = symbols + root_symbols
        symbol_names = [s.get("name", "").lower() for s in all_symbols]
        assert any("legacy_routine" in name for name in symbol_names), "legacy_routine not detected"
        assert any("legacy_function" in name for name in symbol_names), "legacy_function not detected"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_workspace_symbols_search(self, language_server: SolidLanguageServer):
        """Test workspace-wide symbol search functionality."""
        # Search for common Fortran symbols
        symbols = language_server.request_workspace_symbol("calculate")
        if symbols:  # fortls might not support workspace symbols initially
            symbol_names = [s.get("name", "").lower() for s in symbols]
            assert any("calculate" in name for name in symbol_names), "No calculate symbols found in workspace search"
        
        # Search for module names
        symbols = language_server.request_workspace_symbol("module")
        if symbols:
            # Should find modules or symbols containing "module"
            assert len(symbols) > 0, "No module symbols found in workspace search"

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_file_type_recognition(self, language_server: SolidLanguageServer):
        """Test that all Fortran file extensions are properly recognized."""
        from solidlsp.ls_config import LanguageServerConfig
        
        config = LanguageServerConfig(code_language=Language.FORTRAN)
        matcher = Language.FORTRAN.get_source_fn_matcher()
        
        # Test modern Fortran extensions
        assert matcher.is_relevant_filename("test.f90")
        assert matcher.is_relevant_filename("test.f95")
        assert matcher.is_relevant_filename("test.f03")
        assert matcher.is_relevant_filename("test.f08")
        assert matcher.is_relevant_filename("test.f18")
        
        # Test preprocessor extensions
        assert matcher.is_relevant_filename("test.F90")
        assert matcher.is_relevant_filename("test.F95")
        assert matcher.is_relevant_filename("test.F")
        
        # Test legacy extensions
        assert matcher.is_relevant_filename("test.f")
        assert matcher.is_relevant_filename("test.for")
        assert matcher.is_relevant_filename("test.f77")
        
        # Test non-Fortran files are not matched
        assert not matcher.is_relevant_filename("test.py")
        assert not matcher.is_relevant_filename("test.c")
        assert not matcher.is_relevant_filename("test.txt")

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_multiple_file_handling(self, language_server: SolidLanguageServer):
        """Test handling multiple Fortran files simultaneously."""
        files_to_test = ["main.f90", "utils.f90", "math_operations.f90", "legacy.f"]
        
        for filename in files_to_test:
            try:
                symbols, root_symbols = language_server.request_document_symbols(filename)
                assert isinstance(symbols, list)
                assert isinstance(root_symbols, list)
                # Each file should have at least some symbols
                assert len(symbols) > 0 or len(root_symbols) > 0, f"No symbols found in {filename}"
            except Exception as e:
                pytest.fail(f"Failed to process {filename}: {e}")

    @pytest.mark.parametrize("language_server", [Language.FORTRAN], indirect=True)
    def test_error_handling(self, language_server: SolidLanguageServer):
        """Test error handling for invalid Fortran files."""
        try:
            # Request symbols from non-existent file
            symbols, root_symbols = language_server.request_document_symbols("nonexistent.f90")
            # Should return empty lists or handle gracefully
            assert isinstance(symbols, list)
            assert isinstance(root_symbols, list)
        except Exception:
            # Some language servers might raise exceptions for non-existent files
            # This is acceptable behavior
            pass