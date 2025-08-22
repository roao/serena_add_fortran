# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Essential Commands (use these exact commands):**
- `uv run poe format` - Format code (BLACK + RUFF) - ONLY allowed formatting command
- `uv run poe type-check` - Run mypy type checking - ONLY allowed type checking command  
- `uv run poe test` - Run tests with default markers (excludes java/rust by default)
- `uv run poe test -m "python or go"` - Run specific language tests
- `uv run poe lint` - Check code style without fixing

**Test Markers:**
Available pytest markers for selective testing:
- `python`, `go`, `java`, `rust`, `typescript`, `php`, `csharp`, `elixir`, `terraform`, `clojure`, `swift`, `bash`, `ruby`, `fortran`
- `snapshot` - for symbolic editing operation tests

**Project Management:**
- `uv run serena-mcp-server` - Start MCP server from project root
- `uv run index-project` - Index project for faster tool performance

**Always run format, type-check, and test before completing any task.**

## Architecture Overview

Serena is a dual-layer coding agent toolkit:

### Core Components

**1. SerenaAgent (`src/serena/agent.py`)**
- Central orchestrator managing projects, tools, and user interactions
- Coordinates language servers, memory persistence, and MCP server interface
- Manages tool registry and context/mode configurations

**2. SolidLanguageServer (`src/solidlsp/ls.py`)**  
- Unified wrapper around Language Server Protocol (LSP) implementations
- Provides language-agnostic interface for symbol operations
- Handles caching, error recovery, and multiple language server lifecycle

**3. Tool System (`src/serena/tools/`)**
- **file_tools.py** - File system operations, search, regex replacements
- **symbol_tools.py** - Language-aware symbol finding, navigation, editing
- **memory_tools.py** - Project knowledge persistence and retrieval
- **config_tools.py** - Project activation, mode switching
- **workflow_tools.py** - Onboarding and meta-operations

**4. Configuration System (`src/serena/config/`)**
- **Contexts** - Define tool sets for different environments (desktop-app, agent, ide-assistant)
- **Modes** - Operational patterns (planning, editing, interactive, one-shot)
- **Projects** - Per-project settings and language server configs

### Language Support Architecture

Each supported language has:
1. **Language Server Implementation** in `src/solidlsp/language_servers/`
2. **Runtime Dependencies** - Automatic language server downloads when needed
3. **Test Repository** in `test/resources/repos/<language>/`
4. **Test Suite** in `test/solidlsp/<language>/`

### Memory & Knowledge System

- **Markdown-based storage** in `.serena/memories/` directories
- **Project-specific knowledge** persistence across sessions
- **Contextual retrieval** based on relevance
- **Onboarding support** for new projects

## Fortran Support Enhancement

Serena's Fortran support represents a comprehensive language integration designed specifically for scientific computing codebases. The implementation addresses unique challenges in analyzing large-scale Fortran projects through intelligent optimization and user experience enhancements.

### Core Implementation

**Language Server Integration**
- **fortls-based LSP** - Uses Python-based Fortran Language Server for semantic analysis
- **Automatic dependency management** - Installs fortls (>=3.0.0) via pip when needed  
- **Fortran-specific symbol mapping** - Maps Fortran constructs to LSP symbol types:
  - Modules → Module, Interfaces → Interface, Derived types → Struct
  - Common blocks → Namespace, Namelists → Variable
  - Type-bound procedures → Method, Generic procedures → Function

**File Pattern Support**
Comprehensive Fortran file extension matching:
```
*.f90, *.f95, *.f03, *.f08, *.f18, *.F90, *.F95, *.F03, *.F08, *.F, *.f, *.for, *.f77
```

### Intelligent User Experience Features

**Smart Result Management (`tools_base.py`)**
- **Context-aware length limiting** - Provides specific suggestions when results exceed limits
- **Intelligent chunking recommendations** - Suggests parameter adjustments for optimal results
- **Error recovery guidance** - Helps users refine queries instead of generic error messages

**Tool Recommendation System (`smart_recommender.py`)**
- **Query pattern recognition** - Classifies user intent (symbol search, text search, navigation)
- **Project-aware suggestions** - Considers project size and language-specific patterns
- **Fortran-specific templates** - Pre-configured search patterns for common Fortran constructs:
  ```python
  # Examples
  "find_module_procedures": r"^\s*(?:contains|procedure)"
  "find_use_statements": r"^\s*use\s+(\w+)"  
  "find_derived_types": r"^\s*type(?:\s*,.*?)?\s*::\s*(\w+)"
  ```

**RecommendTool Integration (`config_tools.py`)**
- Provides contextual tool recommendations based on query analysis
- Reduces learning curve for complex tool parameter combinations
- Offers Fortran-specific optimization tips

### Fortran-Specific Optimizations

**Scientific Computing Focus**
- **Module dependency analysis** - Track `use` statements and module relationships
- **Preprocessor directive support** - Handle `#include`, `#define` for legacy code
- **Interface recognition** - Support for abstract interfaces and generic procedures
- **Common block handling** - Legacy Fortran data sharing construct support

**Search Pattern Templates**
Pre-built patterns for common Fortran analysis tasks:
- Module procedures and type-bound procedures
- Generic and abstract interfaces  
- Derived type definitions with parameterization
- Common block definitions and usage
- Preprocessor directives in mixed-language projects

### Design Philosophy

**Minimal Intrusion** - Follows existing LSP integration patterns without breaking compatibility
**Progressive Enhancement** - Layers intelligent features on top of solid LSP foundation
**User Experience First** - Addresses real-world pain points discovered through GENE project analysis
**Scientific Computing Awareness** - Understands the unique characteristics of computational science codebases

## Development Patterns

### Adding New Languages
1. Create language server class in `src/solidlsp/language_servers/`
2. Add to Language enum in `src/solidlsp/ls_config.py` 
3. Update factory method in `src/solidlsp/ls.py`
4. Create test repository in `test/resources/repos/<language>/`
5. Write test suite in `test/solidlsp/<language>/`
6. Add pytest marker to `pyproject.toml`

### Adding New Tools
1. Inherit from `Tool` base class in `src/serena/tools/tools_base.py`
2. Implement required methods and parameter validation
3. Register in appropriate tool registry
4. Add to context/mode configurations

### Testing Strategy
- Language-specific tests use pytest markers
- Symbolic editing operations have snapshot tests
- Integration tests in `test_serena_agent.py`
- Test repositories provide realistic symbol structures

## Configuration Hierarchy

Configuration is loaded from (in order of precedence):
1. Command-line arguments to `serena-mcp-server`
2. Project-specific `.serena/project.yml`
3. User config `~/.serena/serena_config.yml`
4. Active modes and contexts

## Key Implementation Notes

- **Symbol-based editing** - Uses LSP for precise code manipulation
- **Caching strategy** - Reduces language server overhead
- **Error recovery** - Automatic language server restart on crashes
- **Multi-language support** - 17+ languages with LSP integration (including Fortran)
- **MCP protocol** - Exposes tools to AI agents via Model Context Protocol
- **Async operation** - Non-blocking language server interactions
- **Intelligent error handling** - Context-aware suggestions for large result sets and query optimization
- **Scientific computing optimization** - Fortran-specific enhancements for computational science workflows

## Working with the Codebase

- Project uses Python 3.11 with `uv` for dependency management
- Strict typing with mypy, formatted with black + ruff
- Language servers run as separate processes with LSP communication
- Memory system enables persistent project knowledge
- Context/mode system allows workflow customization