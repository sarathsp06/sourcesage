# SourceSage: Efficient Code Memory for LLMs

SourceSage is an MCP (Model Context Protocol) server that efficiently memorizes key aspects of a codebase—logic, style, and standards—while allowing dynamic updates and fast retrieval. It's designed to be language-agnostic, leveraging the LLM's understanding of code across multiple languages.

## Features

- **Language Agnostic**: Works with any programming language the LLM understands
- **Knowledge Graph Storage**: Efficiently stores code entities, relationships, patterns, and style conventions
- **LLM-Driven Analysis**: Relies on the LLM to analyze code and provide insights
- **Token-Efficient Storage**: Optimizes for minimal token usage while maximizing memory capacity
- **Incremental Updates**: Updates knowledge when code changes without redundant storage
- **Fast Retrieval**: Enables quick and accurate retrieval of relevant information

## How It Works

SourceSage uses a novel approach where:

1. The LLM analyzes code files (in any language)
2. The LLM uses MCP tools to register entities, relationships, patterns, and style conventions
3. SourceSage stores this knowledge in a token-efficient graph structure
4. The LLM can later query this knowledge when needed

This approach leverages the LLM's inherent language understanding while focusing the MCP server on efficient memory management.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sourcesage.git
cd sourcesage

# Install the package
pip install -e .
```

## Usage

### Running the MCP Server

```bash
# Run the server
sourcesage

# Or run directly from the repository
python -m sourcesage.mcp_server
```

### Connecting to Claude for Desktop

1. Open Claude for Desktop
2. Go to Settings > Developer > Edit Config
3. Add the following to your `claude_desktop_config.json`:

If you've installed the package:
```json
{
  "mcpServers": {
    "sourcesage": {
      "command": "sourcesage",
      "args": []
    }
  }
}
```

If you're running from a local directory without installing:
```json
{
  "sourcesage": {
      "command": "uv", 
      "args": [
        "--directory",
        "/path/to/sourcesage",
        "run",
        "main.py"
      ]
    },
}
```

4. Restart Claude for Desktop

### Available Tools

SourceSage provides the following MCP tools:

1. **register_entity**: Register a code entity in the knowledge graph
   ```
   Input:
     - name: Name of the entity (e.g., class name, function name)
     - entity_type: Type of entity (class, function, module, etc.)
     - summary: Brief description of the entity
     - signature: Entity signature (optional)
     - language: Programming language (optional)
     - observations: List of observations about the entity (optional)
     - metadata: Additional metadata (optional)
   Output: Confirmation message with entity ID
   ```

2. **register_relationship**: Register a relationship between entities
   ```
   Input:
     - from_entity: Name of the source entity
     - to_entity: Name of the target entity
     - relationship_type: Type of relationship (calls, inherits, imports, etc.)
     - metadata: Additional metadata (optional)
   Output: Confirmation message with relationship ID
   ```

3. **register_pattern**: Register a code pattern
   ```
   Input:
     - name: Name of the pattern
     - description: Description of the pattern
     - language: Programming language (optional)
     - example: Example code demonstrating the pattern (optional)
     - metadata: Additional metadata (optional)
   Output: Confirmation message with pattern ID
   ```

4. **register_style_convention**: Register a coding style convention
   ```
   Input:
     - name: Name of the convention
     - description: Description of the convention
     - language: Programming language (optional)
     - examples: Example code snippets demonstrating the convention (optional)
     - metadata: Additional metadata (optional)
   Output: Confirmation message with convention ID
   ```

5. **add_entity_observation**: Add an observation to an entity
   ```
   Input:
     - entity_name: Name of the entity
     - observation: Observation to add
   Output: Confirmation message
   ```

6. **query_entities**: Query entities in the knowledge graph
   ```
   Input:
     - entity_type: Filter by entity type (optional)
     - language: Filter by programming language (optional)
     - name_pattern: Filter by name pattern (regex, optional)
     - limit: Maximum number of results to return (optional)
   Output: List of matching entities
   ```

7. **get_entity_details**: Get detailed information about an entity
   ```
   Input:
     - entity_name: Name of the entity
   Output: Detailed information about the entity
   ```

8. **query_patterns**: Query code patterns in the knowledge graph
   ```
   Input:
     - language: Filter by programming language (optional)
     - pattern_name: Filter by pattern name (optional)
   Output: List of matching patterns
   ```

9. **query_style_conventions**: Query coding style conventions
   ```
   Input:
     - language: Filter by programming language (optional)
     - convention_name: Filter by convention name (optional)
   Output: List of matching style conventions
   ```

10. **get_knowledge_statistics**: Get statistics about the knowledge graph
    ```
    Input: None
    Output: Statistics about the knowledge graph
    ```

11. **clear_knowledge**: Clear all knowledge from the graph
    ```
    Input: None
    Output: Confirmation message
    ```

## Example Workflow with Claude

1. **Analyze Code**: Ask Claude to analyze your code files
   ```
   "Please analyze this Python file and register the key entities and relationships."
   ```

2. **Register Entities**: Claude will use the register_entity tool to store code entities
   ```
   "I'll register the main class in this file."
   ```

3. **Register Relationships**: Claude will use the register_relationship tool to store relationships
   ```
   "I'll register the inheritance relationship between these classes."
   ```

4. **Query Knowledge**: Later, ask Claude about your codebase
   ```
   "What classes are defined in my codebase?"
   "Show me the details of the User class."
   "What's the relationship between the User and Profile classes?"
   ```

5. **Get Coding Patterns**: Ask Claude about coding patterns
   ```
   "What design patterns are used in my codebase?"
   "Show me examples of the Factory pattern in my code."
   ```

## How It's Different

Unlike traditional code analysis tools, SourceSage:

1. **Leverages LLM Understanding**: Uses the LLM's ability to understand code semantics across languages
2. **Stores Semantic Knowledge**: Focuses on meaning and relationships, not just syntax
3. **Is Language Agnostic**: Works with any programming language the LLM understands
4. **Optimizes for Token Efficiency**: Stores knowledge in a way that minimizes token usage
5. **Evolves with LLM Capabilities**: As LLMs improve, so does code understanding

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
