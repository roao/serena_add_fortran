# Fortran Language Server Configuration Example

This directory demonstrates how to configure Serena to work with Fortran projects using fortls.

## Prerequisites

1. **Python 3.7+** with pip installed
2. **fortls** package: `pip install fortls`
3. **Serena** configured with Fortran support

## Project Configuration

Create a `.serena/project.yml` file in your Fortran project root:

```yaml
language: fortran
language_server_config:
  code_language: fortran
  trace_lsp_communication: false
  ignored_paths:
    - "build/**"
    - "*.mod"
    - "*.o"
    - "*.a"
```

## Optional: fortls Configuration

Create a `.fortls` configuration file in your project root for custom settings:

```json
{
  "hover_signature": true,
  "hover_language": "fortran",
  "use_signature_help": true,
  "lowercase_intrinsics": true,
  "debug_log": false,
  "variable_hover": true,
  "preserve_keyword_order": true,
  "max_line_length": -1,
  "format_indent": 4,
  "pp_include": [],
  "pp_define": ["DEBUG=1"],
  "pp_suffixes": [".F90", ".F95", ".F03", ".F08", ".F18", ".F"]
}
```

## Supported File Extensions

- Modern Fortran: `.f90`, `.f95`, `.f03`, `.f08`, `.f18`
- Preprocessor files: `.F90`, `.F95`, `.F03`, `.F08`, `.F`
- Legacy Fortran: `.f`, `.for`, `.f77`

## Usage with Claude Code

1. **Activate the project:**
   ```python
   from serena.tools.config_tools import activate_project
   activate_project("/path/to/fortran/project")
   ```

2. **Search for symbols:**
   ```python
   from serena.tools.symbol_tools import find_symbols
   symbols = find_symbols("subroutine calculate")
   ```

3. **Navigate to definitions:**
   ```python
   from serena.tools.symbol_tools import goto_definition
   definition = goto_definition("main.f90", 20, 15)
   ```

## Features Supported

- **Symbol Detection**: Modules, subroutines, functions, derived types
- **Cross-Module Navigation**: Go-to-definition across module boundaries
- **Hover Information**: Variable and procedure information
- **Completion**: Code completion for procedures and variables
- **Syntax Highlighting**: Full Fortran syntax support
- **Error Detection**: Compilation and syntax errors

## Troubleshooting

### fortls Installation Issues
```bash
pip install --upgrade fortls
```

### Python Path Issues
Ensure Python and pip are in your PATH:
```bash
python --version
pip --version
```

### LSP Communication Issues
Enable tracing in your project configuration:
```yaml
language_server_config:
  trace_lsp_communication: true
```

## Example Project Structure

```
my_fortran_project/
├── .serena/
│   └── project.yml
├── .fortls
├── src/
│   ├── main.f90
│   ├── utils.f90
│   └── math_operations.f90
├── tests/
│   └── test_main.f90
└── Makefile
```

## Performance Tips

1. **Exclude build directories** from LSP analysis
2. **Use .fortls configuration** for project-specific settings  
3. **Limit scope** for large codebases using ignored_paths
4. **Cache optimization** - Serena automatically caches LSP responses