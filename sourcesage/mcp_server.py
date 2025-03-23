"""MCP server implementation for SourceSage."""

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from sourcesage.knowledge import (
    KnowledgeGraph,
)


class SourceSageMcpServer:
    """MCP server for code memory management."""

    def __init__(self, storage_path: str | None = None):
        """Initialize the MCP server.

        Args:
            storage_path: Optional path to store the knowledge graph
        """
        self.knowledge = KnowledgeGraph()
        self.storage_path = storage_path
        self.mcp = FastMCP("sourcesage")
        self._setup_tools()

        # Load existing knowledge if available
        if storage_path and os.path.exists(storage_path):
            loaded_knowledge = KnowledgeGraph.load_from_file(storage_path)
            if loaded_knowledge:
                self.knowledge = loaded_knowledge

    def _setup_tools(self):
        """Set up MCP tools."""

        # Entity registration tool
        @self.mcp.tool()
        def register_entity(
            name: str,
            entity_type: str,
            summary: str,
            signature: str | None = None,
            language: str | None = None,
            observations: list[str] | None = None,
            metadata: dict[str, Any] | None = None,
        ) -> str:
            """Register a code entity in the knowledge graph.

            Args:
                name: Name of the entity (e.g., class name, function name)
                entity_type: Type of entity (class, function, module, etc.)
                summary: Brief description of the entity
                signature: Entity signature (e.g., function signature)
                language: Programming language
                observations: List of observations about the entity
                metadata: Additional metadata as key-value pairs
            """
            entity_id = self.knowledge.add_entity(
                name=name,
                entity_type=entity_type,
                summary=summary,
                signature=signature,
                language=language,
                observations=observations,
                metadata=metadata,
            )

            # Save knowledge if storage path is set
            if self.storage_path:
                self.knowledge.save_to_file(self.storage_path)

            return f"Entity registered with ID: {entity_id}"

        # Relationship registration tool
        @self.mcp.tool()
        def register_relationship(
            from_entity: str,
            to_entity: str,
            relationship_type: str,
            metadata: dict[str, Any] | None = None,
        ) -> str:
            """Register a relationship between entities.

            Args:
                from_entity: Name of the source entity
                to_entity: Name of the target entity
                relationship_type: Type of relationship (calls, inherits, imports, etc.)
                metadata: Additional metadata as key-value pairs
            """
            # Find entities by name
            from_entities = self.knowledge.find_entity(from_entity)
            to_entities = self.knowledge.find_entity(to_entity)

            if not from_entities:
                return f"Error: Source entity '{from_entity}' not found"

            if not to_entities:
                return f"Error: Target entity '{to_entity}' not found"

            # If multiple entities with the same name, use the first one
            from_id = from_entities[0].entity_id
            to_id = to_entities[0].entity_id

            relation_id = self.knowledge.add_relation(
                from_id=from_id,
                to_id=to_id,
                relation_type=relationship_type,
                metadata=metadata,
            )

            if not relation_id:
                return "Error: Failed to create relationship"

            # Save knowledge if storage path is set
            if self.storage_path:
                self.knowledge.save_to_file(self.storage_path)

            return f"Relationship registered with ID: {relation_id}"

        # Pattern registration tool
        @self.mcp.tool()
        def register_pattern(
            name: str,
            description: str,
            language: str | None = None,
            example: str | None = None,
            metadata: dict[str, Any] | None = None,
        ) -> str:
            """Register a code pattern.

            Args:
                name: Name of the pattern
                description: Description of the pattern
                language: Programming language
                example: Example code demonstrating the pattern
                metadata: Additional metadata as key-value pairs
            """
            pattern_id = self.knowledge.add_pattern(
                name=name,
                description=description,
                language=language,
                example=example,
                metadata=metadata,
            )

            # Save knowledge if storage path is set
            if self.storage_path:
                self.knowledge.save_to_file(self.storage_path)

            return f"Pattern registered with ID: {pattern_id}"

        # Style convention registration tool
        @self.mcp.tool()
        def register_style_convention(
            name: str,
            description: str,
            language: str | None = None,
            examples: list[str] | None = None,
            metadata: dict[str, Any] | None = None,
        ) -> str:
            """Register a coding style convention.

            Args:
                name: Name of the convention
                description: Description of the convention
                language: Programming language
                examples: Example code snippets demonstrating the convention
                metadata: Additional metadata as key-value pairs
            """
            convention_id = self.knowledge.add_style_convention(
                name=name,
                description=description,
                language=language,
                examples=examples,
                metadata=metadata,
            )

            # Save knowledge if storage path is set
            if self.storage_path:
                self.knowledge.save_to_file(self.storage_path)

            return f"Style convention registered with ID: {convention_id}"

        # Entity observation tool
        @self.mcp.tool()
        def add_entity_observation(entity_name: str, observation: str) -> str:
            """Add an observation to an entity.

            Args:
                entity_name: Name of the entity
                observation: Observation to add
            """
            # Find entity by name
            entities = self.knowledge.find_entity(entity_name)

            if not entities:
                return f"Error: Entity '{entity_name}' not found"

            # If multiple entities with the same name, use the first one
            entity_id = entities[0].entity_id

            success = self.knowledge.add_observation(entity_id, observation)

            if not success:
                return f"Error: Failed to add observation to entity '{entity_name}'"

            # Save knowledge if storage path is set
            if self.storage_path:
                self.knowledge.save_to_file(self.storage_path)

            return f"Observation added to entity '{entity_name}'"

        # Entity query tool
        @self.mcp.tool()
        def query_entities(
            entity_type: str | None = None,
            language: str | None = None,
            name_pattern: str | None = None,
            limit: int = 10,
        ) -> str:
            """Query entities in the knowledge graph.

            Args:
                entity_type: Filter by entity type (class, function, module, etc.)
                language: Filter by programming language
                name_pattern: Filter by name pattern (regex)
                limit: Maximum number of results to return
            """
            entities = self.knowledge.query_entities(
                entity_type=entity_type,
                language=language,
                name_pattern=name_pattern,
                limit=limit,
            )

            if not entities:
                return "No entities found matching the query criteria"

            # Format results
            output = f"Found {len(entities)} entities:\n\n"

            for entity in entities:
                output += f"Name: {entity.name}\n"
                output += f"Type: {entity.entity_type}\n"

                if entity.language:
                    output += f"Language: {entity.language}\n"

                if entity.signature:
                    output += f"Signature: {entity.signature}\n"

                output += f"Summary: {entity.summary}\n"

                if entity.observations:
                    output += "Observations:\n"
                    for observation in entity.observations[
                        :3
                    ]:  # Limit to 3 observations
                        output += f"- {observation}\n"

                    if len(entity.observations) > 3:
                        output += f"... and {len(entity.observations) - 3} more observations\n"

                output += "\n"

            return output

        # Entity details tool
        @self.mcp.tool()
        def get_entity_details(entity_name: str) -> str:
            """Get detailed information about an entity.

            Args:
                entity_name: Name of the entity
            """
            # Find entity by name
            entities = self.knowledge.find_entity(entity_name)

            if not entities:
                return f"Error: Entity '{entity_name}' not found"

            # If multiple entities with the same name, provide a summary
            if len(entities) > 1:
                output = f"Found {len(entities)} entities named '{entity_name}':\n\n"

                for entity in entities:
                    output += f"Type: {entity.entity_type}\n"

                    if entity.language:
                        output += f"Language: {entity.language}\n"

                    if entity.signature:
                        output += f"Signature: {entity.signature}\n"

                    output += f"Summary: {entity.summary}\n\n"

                return output

            # Get the single matching entity
            entity = entities[0]
            entity_id = entity.entity_id

            # Get context
            context = self.knowledge.get_entity_context(entity_id, depth=1)

            # Format output
            output = f"Entity: {entity.name}\n"
            output += f"Type: {entity.entity_type}\n"

            if entity.language:
                output += f"Language: {entity.language}\n"

            if entity.signature:
                output += f"Signature: {entity.signature}\n"

            output += f"Summary: {entity.summary}\n\n"

            # Add observations
            if entity.observations:
                output += "Observations:\n"
                for observation in entity.observations:
                    output += f"- {observation}\n"
                output += "\n"

            # Add relationships
            relations = context.get("relations", [])
            if relations:
                output += "Relationships:\n"

                outgoing = [r for r in relations if r.from_id == entity_id]
                incoming = [r for r in relations if r.to_id == entity_id]

                if outgoing:
                    output += "Outgoing:\n"
                    for relation in outgoing:
                        to_entity = self.knowledge.get_entity(relation.to_id)
                        if to_entity:
                            output += f"- {relation.relation_type} -> {to_entity.name} ({to_entity.entity_type})\n"

                if incoming:
                    output += "Incoming:\n"
                    for relation in incoming:
                        from_entity = self.knowledge.get_entity(relation.from_id)
                        if from_entity:
                            output += f"- {from_entity.name} ({from_entity.entity_type}) {relation.relation_type} -> this\n"

                output += "\n"

            # Add metadata
            if entity.metadata:
                output += "Metadata:\n"
                for key, value in entity.metadata.items():
                    output += f"- {key}: {value}\n"

            return output

        # Pattern query tool
        @self.mcp.tool()
        def query_patterns(
            language: str | None = None, pattern_name: str | None = None
        ) -> str:
            """Query code patterns in the knowledge graph.

            Args:
                language: Filter by programming language
                pattern_name: Filter by pattern name
            """
            patterns = self.knowledge.find_patterns(
                name=pattern_name, language=language
            )

            if not patterns:
                return "No patterns found matching the query criteria"

            # Format results
            output = f"Found {len(patterns)} patterns:\n\n"

            for pattern in patterns:
                output += f"Name: {pattern.name}\n"

                if pattern.language:
                    output += f"Language: {pattern.language}\n"

                output += f"Description: {pattern.description}\n"

                if pattern.example:
                    output += "Example:\n"
                    output += "```\n"
                    output += pattern.example
                    output += "\n```\n"

                output += "\n"

            return output

        # Style convention query tool
        @self.mcp.tool()
        def query_style_conventions(
            language: str | None = None, convention_name: str | None = None
        ) -> str:
            """Query coding style conventions in the knowledge graph.

            Args:
                language: Filter by programming language
                convention_name: Filter by convention name
            """
            conventions = self.knowledge.find_style_conventions(
                name=convention_name, language=language
            )

            if not conventions:
                return "No style conventions found matching the query criteria"

            # Format results
            output = f"Found {len(conventions)} style conventions:\n\n"

            for convention in conventions:
                output += f"Name: {convention.name}\n"

                if convention.language:
                    output += f"Language: {convention.language}\n"

                output += f"Description: {convention.description}\n"

                if convention.examples:
                    output += "Examples:\n"
                    for i, example in enumerate(convention.examples):
                        output += f"Example {i + 1}:\n"
                        output += "```\n"
                        output += example
                        output += "\n```\n"

                output += "\n"

            return output

        # Knowledge statistics tool
        @self.mcp.tool()
        def get_knowledge_statistics() -> str:
            """Get statistics about the knowledge graph."""
            # Count entities by type
            entity_types = {}
            for entity in self.knowledge.entities.values():
                entity_types[entity.entity_type] = (
                    entity_types.get(entity.entity_type, 0) + 1
                )

            # Count entities by language
            languages = {}
            for entity in self.knowledge.entities.values():
                if entity.language:
                    languages[entity.language] = languages.get(entity.language, 0) + 1

            # Count relations by type
            relation_types = {}
            for relation in self.knowledge.relations.values():
                relation_types[relation.relation_type] = (
                    relation_types.get(relation.relation_type, 0) + 1
                )

            # Count patterns by language
            pattern_languages = {}
            for pattern in self.knowledge.patterns.values():
                if pattern.language:
                    pattern_languages[pattern.language] = (
                        pattern_languages.get(pattern.language, 0) + 1
                    )

            # Format output
            output = "Knowledge Graph Statistics:\n\n"

            output += f"Total Entities: {len(self.knowledge.entities)}\n"
            output += f"Total Relations: {len(self.knowledge.relations)}\n"
            output += f"Total Patterns: {len(self.knowledge.patterns)}\n"
            output += (
                f"Total Style Conventions: {len(self.knowledge.style_conventions)}\n\n"
            )

            if entity_types:
                output += "Entities by Type:\n"
                for entity_type, count in entity_types.items():
                    output += f"- {entity_type}: {count}\n"
                output += "\n"

            if languages:
                output += "Entities by Language:\n"
                for language, count in languages.items():
                    output += f"- {language}: {count}\n"
                output += "\n"

            if relation_types:
                output += "Relations by Type:\n"
                for relation_type, count in relation_types.items():
                    output += f"- {relation_type}: {count}\n"
                output += "\n"

            if pattern_languages:
                output += "Patterns by Language:\n"
                for language, count in pattern_languages.items():
                    output += f"- {language}: {count}\n"

            return output

        # Clear knowledge tool
        @self.mcp.tool()
        def clear_knowledge() -> str:
            """Clear all knowledge from the graph."""
            self.knowledge = KnowledgeGraph()

            # Save empty knowledge if storage path is set
            if self.storage_path:
                self.knowledge.save_to_file(self.storage_path)

            return "Knowledge graph cleared successfully"

        # Project understanding tools
        @self.mcp.tool()
        def load_project_understanding(project_path: str) -> str:
            """Load understanding of an entire project at once.

            This tool should be used by MCP clients to quickly get project understanding
            if available, instead of reading all the files individually. It loads all
            entities, relationships, patterns, and style conventions related to the project.

            Args:
                project_path: Path to the project root directory
            """
            # Normalize the project path
            project_path = os.path.normpath(os.path.abspath(project_path))

            # Check if we have any entities related to this project
            project_entities = []
            for entity in self.knowledge.entities.values():
                entity_project = entity.metadata.get("project_path")
                if (
                    entity_project
                    and os.path.normpath(os.path.abspath(entity_project))
                    == project_path
                ):
                    project_entities.append(entity)

            if not project_entities:
                return f"No understanding available for project at: {project_path}"

            # Count entities by type
            entity_types = {}
            for entity in project_entities:
                entity_types[entity.entity_type] = (
                    entity_types.get(entity.entity_type, 0) + 1
                )

            # Count relations
            project_entity_ids = {entity.entity_id for entity in project_entities}
            project_relations = []
            for relation in self.knowledge.relations.values():
                if (
                    relation.from_id in project_entity_ids
                    or relation.to_id in project_entity_ids
                ):
                    project_relations.append(relation)

            # Format output
            output = f"Project Understanding for: {project_path}\n\n"
            output += f"Total Entities: {len(project_entities)}\n"
            output += f"Total Relations: {len(project_relations)}\n\n"

            if entity_types:
                output += "Entities by Type:\n"
                for entity_type, count in entity_types.items():
                    output += f"- {entity_type}: {count}\n"
                output += "\n"

            # List key entities (e.g., modules, classes)
            key_entities = [
                e
                for e in project_entities
                if e.entity_type in ["module", "class", "interface"]
            ]
            if key_entities:
                output += "Key Components:\n"
                for entity in sorted(key_entities, key=lambda e: e.name)[
                    :10
                ]:  # Limit to 10
                    output += (
                        f"- {entity.name} ({entity.entity_type}): {entity.summary}\n"
                    )

                if len(key_entities) > 10:
                    output += f"... and {len(key_entities) - 10} more key components\n"
                output += "\n"

            # List all entities
            output += "All Entities:\n"
            for entity in sorted(project_entities, key=lambda e: e.name)[
                :30
            ]:  # Limit to 30 to avoid excessive output
                output += f"- {entity.name} ({entity.entity_type}): {entity.summary}\n"

            if len(project_entities) > 30:
                output += f"... and {len(project_entities) - 30} more entities\n"
            output += "\n"

            return output

        @self.mcp.tool()
        def dump_project_understanding(
            project_path: str, include_observations: bool = False
        ) -> str:
            """Dump understanding of an entire project at once.

            This tool provides a comprehensive dump of all knowledge related to a project,
            including all entities, relationships, patterns, and style conventions.

            Args:
                project_path: Path to the project root directory
                include_observations: Whether to include detailed observations
            """
            # Normalize the project path
            project_path = os.path.normpath(os.path.abspath(project_path))

            # Check if we have any entities related to this project
            project_entities = []
            for entity in self.knowledge.entities.values():
                entity_project = entity.metadata.get("project_path")
                if (
                    entity_project
                    and os.path.normpath(os.path.abspath(entity_project))
                    == project_path
                ):
                    project_entities.append(entity)

            if not project_entities:
                return f"No understanding available for project at: {project_path}"

            # Get all relations involving project entities
            project_entity_ids = {entity.entity_id for entity in project_entities}
            project_relations = []
            for relation in self.knowledge.relations.values():
                if (
                    relation.from_id in project_entity_ids
                    or relation.to_id in project_entity_ids
                ):
                    project_relations.append(relation)

            # Format output
            output = f"Project Understanding for: {project_path}\n\n"
            output += f"Total Entities: {len(project_entities)}\n"
            output += f"Total Relations: {len(project_relations)}\n\n"

            # Group entities by type
            entities_by_type = {}
            for entity in project_entities:
                if entity.entity_type not in entities_by_type:
                    entities_by_type[entity.entity_type] = []
                entities_by_type[entity.entity_type].append(entity)

            # Output entities by type
            for entity_type, entities in sorted(entities_by_type.items()):
                output += f"{entity_type.capitalize()} Entities ({len(entities)}):\n"

                for entity in sorted(entities, key=lambda e: e.name):
                    output += f"- {entity.name}\n"
                    output += f"  Summary: {entity.summary}\n"

                    if entity.signature:
                        output += f"  Signature: {entity.signature}\n"

                    if entity.language:
                        output += f"  Language: {entity.language}\n"

                    # Include observations if requested
                    if include_observations and entity.observations:
                        output += "  Observations:\n"
                        for observation in entity.observations:
                            output += f"    - {observation}\n"

                    # Include relations
                    entity_relations = [
                        r for r in project_relations if r.from_id == entity.entity_id
                    ]
                    if entity_relations:
                        output += "  Relations:\n"
                        for relation in entity_relations:
                            to_entity = self.knowledge.get_entity(relation.to_id)
                            if to_entity:
                                output += f"    - {relation.relation_type} -> {to_entity.name} ({to_entity.entity_type})\n"

                    output += "\n"

                output += "\n"

            # Include patterns and style conventions if any are associated with this project
            project_patterns = []
            for pattern in self.knowledge.patterns.values():
                if pattern.metadata.get("project_path") == project_path:
                    project_patterns.append(pattern)

            if project_patterns:
                output += f"Patterns ({len(project_patterns)}):\n"
                for pattern in project_patterns:
                    output += f"- {pattern.name}: {pattern.description}\n"
                output += "\n"

            project_conventions = []
            for convention in self.knowledge.style_conventions.values():
                if convention.metadata.get("project_path") == project_path:
                    project_conventions.append(convention)

            if project_conventions:
                output += f"Style Conventions ({len(project_conventions)}):\n"
                for convention in project_conventions:
                    output += f"- {convention.name}: {convention.description}\n"
                output += "\n"

            return output

    def run(self, transport: str = "stdio"):
        """Run the MCP server.

        Args:
            transport: Transport to use (stdio, http)
        """
        self.mcp.run(transport=transport)


def main():
    """Run the SourceSage MCP server."""
    # Use a standard location for storage
    # First check if XDG_DATA_HOME is set (Linux/Unix standard)
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        base_dir = xdg_data_home
    else:
        # Fall back to platform-specific standard locations
        home_dir = os.path.expanduser("~")
        if os.name == "nt":  # Windows
            base_dir = os.path.join(home_dir, "AppData", "Local")
        elif os.name == "posix":  # macOS/Linux
            if os.path.exists(os.path.join(home_dir, "Library")):  # macOS
                base_dir = os.path.join(home_dir, "Library", "Application Support")
            else:  # Linux/Unix
                base_dir = os.path.join(home_dir, ".local", "share")
        else:  # Fallback for other platforms
            base_dir = home_dir

    storage_dir = os.path.join(base_dir, "sourcesage")

    # Create storage directory if it doesn't exist
    os.makedirs(storage_dir, exist_ok=True)

    storage_path = os.path.join(storage_dir, "knowledge.json")

    print(f"Using knowledge graph storage at: {storage_path}")

    server = SourceSageMcpServer(storage_path=storage_path)
    server.run()


if __name__ == "__main__":
    main()
