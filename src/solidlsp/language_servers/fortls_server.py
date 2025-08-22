"""
Provides Fortran specific instantiation of the LanguageServer class using fortls.
Contains various configurations and settings specific to Fortran.
"""

import logging
import os
import pathlib
import shutil
import subprocess
import sys
import threading

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings
from solidlsp.ls_types import SymbolKind


# Fortran-specific symbol kind mappings for better categorization
FORTRAN_SYMBOL_KIND_MAPPING = {
    # Fortran specific constructs mapped to appropriate LSP symbol kinds
    'interface': SymbolKind.Interface,
    'abstract_interface': SymbolKind.Interface,
    'generic_interface': SymbolKind.Interface,
    'namelist': SymbolKind.Variable,      # Namelists are treated as special variables
    'common': SymbolKind.Namespace,       # Common blocks as namespaces
    'block_data': SymbolKind.Module,      # Block data as modules
    'derived_type': SymbolKind.Struct,    # Derived types as structures
    'type_bound_procedure': SymbolKind.Method,  # Type-bound procedures as methods
    'generic_procedure': SymbolKind.Function,   # Generic procedures as functions
    'abstract_procedure': SymbolKind.Function,  # Abstract procedures as functions
}

# Fortran-specific search patterns for symbol recognition
FORTRAN_SYMBOL_PATTERNS = {
    'module': r'^\s*module\s+(\w+)',
    'program': r'^\s*program\s+(\w+)',
    'subroutine': r'^\s*(?:pure\s+|elemental\s+|impure\s+)?subroutine\s+(\w+)',
    'function': r'^\s*(?:pure\s+|elemental\s+|impure\s+)?(?:integer|real|complex|logical|character|type\(\w+\))?\s*function\s+(\w+)',
    'interface': r'^\s*(?:abstract\s+)?interface(?:\s+(\w+)|\s*$)',
    'type': r'^\s*type(?:\s*,\s*(?:public|private|abstract|extends\(\w+\)))?\s*::\s*(\w+)',
    'common': r'^\s*common\s*/(\w+)/',
    'namelist': r'^\s*namelist\s*/(\w+)/',
    'use_statement': r'^\s*use\s+(\w+)(?:\s*,\s*only\s*:\s*(.*?))?',
    'include': r'^\s*#?include\s+["\']([^"\']+)["\']',
}

# Fortran search templates for common use cases
FORTRAN_SEARCH_TEMPLATES = {
    'find_module_procedures': {
        'pattern': r'^\s*(?:contains|procedure)',
        'description': 'Find module procedures and type-bound procedures',
        'context_lines': 2
    },
    'find_use_statements': {
        'pattern': r'^\s*use\s+(\w+)',
        'description': 'Find module dependencies via use statements',
        'context_lines': 0
    },
    'find_interfaces': {
        'pattern': r'^\s*interface\s+(\w+)',
        'description': 'Find generic interfaces and abstract interfaces',
        'context_lines': 3
    },
    'find_derived_types': {
        'pattern': r'^\s*type(?:\s*,.*?)?\s*::\s*(\w+)',
        'description': 'Find derived type definitions',
        'context_lines': 1
    },
    'find_common_blocks': {
        'pattern': r'^\s*common\s*/(\w+)/',
        'description': 'Find common block definitions',
        'context_lines': 1
    },
    'find_preprocessor_directives': {
        'pattern': r'^\s*#\w+',
        'description': 'Find preprocessor directives like #include, #define',
        'context_lines': 0
    }
}


class FortlsServer(SolidLanguageServer):
    """
    Provides Fortran specific instantiation of the LanguageServer class using fortls.
    Contains various configurations and settings specific to Fortran.
    """

    def __init__(
        self, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str, solidlsp_settings: SolidLSPSettings
    ):
        """
        Creates a FortlsServer instance. This class is not meant to be instantiated directly.
        Use LanguageServer.create() instead.
        """
        fortls_executable_path = self._ensure_fortls_installed()
        logger.log(f"Using fortls at: {fortls_executable_path}", logging.INFO)
        
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=fortls_executable_path, cwd=repository_root_path),
            "fortran",
            solidlsp_settings,
        )

        # Event to signal when initial workspace analysis is complete
        self.analysis_complete = threading.Event()
        self.server_ready = threading.Event()

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # For Fortran projects, ignore common build and temporary directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "build", "dist", "CMakeFiles", "*.mod", "*.o", "*.a"
        ]

    @staticmethod
    def _get_fortls_version():
        """Get installed fortls version or None if not found."""
        try:
            result = subprocess.run(["fortls", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            return None
        return None

    @staticmethod
    def _ensure_fortls_installed():
        """Ensure fortls is available, install via pip if needed."""
        # First check if fortls is already available in PATH
        if shutil.which("fortls"):
            return "fortls"
        
        # Check if fortls is available as a Python module
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import fortls; print('fortls available')"],
                check=True,
                capture_output=True,
                text=True
            )
            return "fortls"
        except subprocess.CalledProcessError:
            pass
        
        # Try to install fortls via pip
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "fortls>=3.0.0"],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to install fortls via pip: {e}\n"
                f"Please install fortls manually: pip install fortls"
            )
        
        # Verify installation worked
        if not shutil.which("fortls"):
            # Try via python -m fortls
            try:
                subprocess.run(
                    [sys.executable, "-c", "import fortls"],
                    check=True,
                    capture_output=True
                )
                return f"{sys.executable} -m fortls"
            except subprocess.CalledProcessError:
                raise RuntimeError(
                    "fortls installation succeeded but binary not found in PATH.\n"
                    "Please ensure your Python scripts directory is in PATH."
                )
        
        return "fortls"

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the Fortran Language Server.
        """
        root_uri = pathlib.Path(repository_absolute_path).as_uri()
        initialize_params = {
            "processId": os.getpid(),
            "rootPath": repository_absolute_path,
            "rootUri": root_uri,
            "capabilities": {
                "textDocument": {
                    "synchronization": {"didSave": True, "dynamicRegistration": True},
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "hierarchicalDocumentSymbolSupport": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                    "hover": {"dynamicRegistration": True, "contentFormat": ["markdown", "plaintext"]},
                    "completion": {"dynamicRegistration": True},
                },
                "workspace": {
                    "workspaceFolders": True,
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "symbol": {"dynamicRegistration": True},
                },
            },
            "workspaceFolders": [
                {
                    "uri": root_uri,
                    "name": os.path.basename(repository_absolute_path),
                }
            ],
        }
        return initialize_params

    def _start_server(self):
        """
        Starts the Fortran Language Server, waits for the server to be ready and yields the LanguageServer instance.
        """

        def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)
            # Check for fortls ready signals
            message_text = msg.get("message", "")
            if "parsing complete" in message_text.lower() or "ready" in message_text.lower():
                self.logger.log("Fortran language server analysis signals detected", logging.INFO)
                self.server_ready.set()
                self.completions_available.set()
                self.analysis_complete.set()

        def do_nothing(params):
            return

        # Set up notification handlers
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_notification("window/showMessage", window_log_message)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        self.logger.log("Starting Fortran server process", logging.INFO)
        self.server.start()
        initialize_params = self._get_initialize_params(self.repository_root_path)

        self.logger.log(
            "Sending initialize request from LSP client to LSP server and awaiting response",
            logging.INFO,
        )
        init_response = self.server.send.initialize(initialize_params)
        self.logger.log(f"Received initialize response from fortls server", logging.DEBUG)

        # Verify server capabilities
        capabilities = init_response.get("capabilities", {})
        
        if "textDocumentSync" in capabilities:
            self.logger.log("fortls supports text document synchronization", logging.INFO)
        
        if "documentSymbolProvider" in capabilities:
            self.logger.log("fortls supports document symbols", logging.INFO)
        else:
            self.logger.log("Warning: fortls does not report document symbol support", logging.WARNING)

        self.server.notify.initialized({})

        # Wait for server readiness with timeout (similar to gopls)
        self.logger.log("Waiting for Fortran language server to be ready...", logging.INFO)
        if not self.server_ready.wait(timeout=3.0):
            # Fallback: assume server is ready after timeout (like gopls)
            self.logger.log("Timeout waiting for fortls server ready signal, proceeding anyway", logging.WARNING)
            self.server_ready.set()
            self.completions_available.set()
            self.analysis_complete.set()
        else:
            self.logger.log("fortls server initialization complete", logging.INFO)