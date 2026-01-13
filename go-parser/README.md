# coma-go (CodeWiki Go Parser)

`coma-go` is a lightweight, high-performance static analysis tool written in Go. It is designed to parse Go source files and extract structural information, including abstract syntax tree (AST) nodes (structs, interfaces, functions, methods) and call relationships.

This tool is primarily integrated into [CodeWiki](../README.md) as a backend analyzer for Go projects, enabling deep dependency analysis and documentation generation.

## Features

- **Fast Parsing**: Leverages Go's native `go/parser` and `go/ast` packages for robust and speedy analysis.
- **Component Extraction**: Identifies and extracts metadata for:
  - Structs and Interfaces (mapped to "class" components)
  - Functions and Methods
  - Source code segments (including documentation comments)
- **Call Graph Generation**: Extracts function call relationships within the analyzed file.
- **JSON Output**: Produces structured JSON output suitable for integration with other tools (e.g., Python parsers).

## Installation

### Prerequisites
- Go 1.22 or higher

### Build
To build the binary, run:

```bash
cd go-parser
go build -o coma-go .
```

This will create a `coma-go` executable in the current directory.

## Usage

`coma-go` is a command-line tool.

```bash
./coma-go -file <path_to_go_file> [-repo <path_to_repo_root>]
```

### Arguments

| Flag    | Required | Description                                                                   |
| ------- | -------- | ----------------------------------------------------------------------------- |
| `-file` | Yes      | Absolute or relative path to the Go file to analyze.                          |
| `-repo` | No       | Path to the repository root. Used to calculate relative paths for components. |

### Example

```bash
./coma-go -file ./analyzer/analyzer.go -repo .
```

## Output Format

The tool outputs a JSON object to `stdout` containing two main arrays: `nodes` and `call_relationships`.

### Example JSON Output

```json
{
  "nodes": [
    {
      "id": "analyzer.GoAnalyzer",
      "name": "GoAnalyzer",
      "component_type": "class",
      "file_path": "/abs/path/to/go-parser/analyzer/analyzer.go",
      "relative_path": "analyzer/analyzer.go",
      "source_code": "type GoAnalyzer struct { ... }",
      "start_line": 13,
      "end_line": 21,
      "has_docstring": false,
      "node_type": "struct",
      "component_id": "analyzer.GoAnalyzer"
    },
    {
      "id": "analyzer.NewGoAnalyzer",
      "name": "NewGoAnalyzer",
      "component_type": "function",
      "source_code": "func NewGoAnalyzer(...) { ... }",
      "start_line": 23,
      "end_line": 37,
      "parameters": ["filePath", "repoPath"]
    }
  ],
  "call_relationships": [
    {
      "caller": "analyzer.NewGoAnalyzer",
      "callee": "os.ReadFile",
      "call_line": 24,
      "is_resolved": true,
      "relationship_type": "calls"
    }
  ]
}
```

## Integration with CodeWiki

In the CodeWiki Python backend, `coma-go` is invoked via `subprocess`. The wrapper implementation can be found in `codewiki/src/be/dependency_analyzer/analyzers/go.py`.

It treats `coma-go` as a black-box parser:
1. Python detects a `.go` file.
2. Python executes `coma-go` with the file path.
3. `coma-go` analyzes the file and prints JSON to stdout.
4. Python captures stdout, deserializes the JSON, and integrates the nodes into the global dependency graph.

## Development

### Module Structure

- `main.go`: Entry point. Handles CLI flag parsing and JSON output marshaling.
- `analyzer/`: Core logic for AST traversal and extraction.
  - `analyzer.go`: `GoAnalyzer` struct and visitor methods (`visitTypeSpec`, `visitFuncDecl`).
- `models/`: Go struct definitions for the output JSON format (`Node`, `CallRelationship`).

### Running Tests

```bash
go test -v ./analyzer
```
