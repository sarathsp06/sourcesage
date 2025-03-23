"""Knowledge graph for efficient code memory storage."""

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Entity:
    """An entity in the knowledge graph."""

    # Basic identification
    entity_id: str
    name: str
    entity_type: str  # "class", "function", "module", etc.

    # Content representation
    summary: str
    signature: str | None = None

    # Metadata
    language: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    # Observations (facts about this entity)
    observations: list[str] = field(default_factory=list)


@dataclass
class Relation:
    """A relationship between entities in the knowledge graph."""

    # Basic identification
    relation_id: str
    relation_type: str  # "calls", "inherits", "imports", etc.

    # Connected entities
    from_id: str
    to_id: str

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: float = field(default_factory=time.time)


@dataclass
class Pattern:
    """A code pattern identified in the codebase."""

    # Basic identification
    pattern_id: str
    name: str
    description: str

    # Pattern details
    language: str | None = None
    example: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class StyleConvention:
    """A coding style convention identified in the codebase."""

    # Basic identification
    convention_id: str
    name: str
    description: str

    # Convention details
    language: str | None = None
    examples: list[str] = field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class KnowledgeGraph:
    """Manages a knowledge graph of code entities and relationships."""

    def __init__(self):
        """Initialize the knowledge graph."""
        self.entities: dict[str, Entity] = {}
        self.relations: dict[str, Relation] = {}
        self.patterns: dict[str, Pattern] = {}
        self.style_conventions: dict[str, StyleConvention] = {}
        self._next_id = 0

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID with the given prefix."""
        entity_id = f"{prefix}_{self._next_id}"
        self._next_id += 1
        return entity_id

    # Entity operations

    def add_entity(
        self,
        name: str,
        entity_type: str,
        summary: str,
        signature: str | None = None,
        language: str | None = None,
        metadata: dict[str, Any] | None = None,
        observations: list[str] | None = None,
    ) -> str:
        """Add an entity to the knowledge graph.

        Args:
            name: The name of the entity
            entity_type: The type of entity (class, function, module, etc.)
            summary: A brief summary of the entity
            signature: The entity's signature, if applicable
            language: The programming language
            metadata: Additional metadata
            observations: List of observations about the entity

        Returns:
            The ID of the new entity
        """
        entity_id = self._generate_id("entity")

        entity = Entity(
            entity_id=entity_id,
            name=name,
            entity_type=entity_type,
            summary=summary,
            signature=signature,
            language=language,
            metadata=metadata or {},
            observations=observations or [],
        )

        self.entities[entity_id] = entity
        return entity_id

    def update_entity(self, entity_id: str, **kwargs) -> bool:
        """Update an entity in the knowledge graph.

        Args:
            entity_id: The ID of the entity to update
            **kwargs: Attributes to update

        Returns:
            True if successful, False otherwise
        """
        if entity_id not in self.entities:
            return False

        entity = self.entities[entity_id]

        for key, value in kwargs.items():
            if hasattr(entity, key) and key != "entity_id":
                setattr(entity, key, value)

        entity.updated_at = time.time()
        return True

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get an entity by ID."""
        return self.entities.get(entity_id)

    def find_entity(self, name: str, entity_type: str | None = None) -> list[Entity]:
        """Find entities by name and optionally type.

        Args:
            name: The name to search for
            entity_type: Optional entity type to filter by

        Returns:
            List of matching entities
        """
        results = []

        for entity in self.entities.values():
            if entity.name == name:
                if entity_type is None or entity.entity_type == entity_type:
                    results.append(entity)

        return results

    def add_observation(self, entity_id: str, observation: str) -> bool:
        """Add an observation to an entity.

        Args:
            entity_id: The ID of the entity
            observation: The observation to add

        Returns:
            True if successful, False otherwise
        """
        if entity_id not in self.entities:
            return False

        entity = self.entities[entity_id]

        if observation not in entity.observations:
            entity.observations.append(observation)
            entity.updated_at = time.time()

        return True

    # Relation operations

    def add_relation(
        self,
        from_id: str,
        to_id: str,
        relation_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        """Add a relationship between entities.

        Args:
            from_id: The ID of the source entity
            to_id: The ID of the target entity
            relation_type: The type of relationship
            metadata: Additional metadata

        Returns:
            The ID of the new relation, or None if failed
        """
        if from_id not in self.entities or to_id not in self.entities:
            return None

        relation_id = self._generate_id("relation")

        relation = Relation(
            relation_id=relation_id,
            relation_type=relation_type,
            from_id=from_id,
            to_id=to_id,
            metadata=metadata or {},
        )

        self.relations[relation_id] = relation
        return relation_id

    def get_relations(
        self,
        entity_id: str,
        relation_type: str | None = None,
        direction: str = "both",
    ) -> list[Relation]:
        """Get relations for an entity.

        Args:
            entity_id: The ID of the entity
            relation_type: Optional relation type to filter by
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of matching relations
        """
        results = []

        for relation in self.relations.values():
            if direction in ["outgoing", "both"] and relation.from_id == entity_id:
                if relation_type is None or relation.relation_type == relation_type:
                    results.append(relation)

            if direction in ["incoming", "both"] and relation.to_id == entity_id:
                if relation_type is None or relation.relation_type == relation_type:
                    results.append(relation)

        return results

    def get_related_entities(
        self,
        entity_id: str,
        relation_type: str | None = None,
        direction: str = "both",
    ) -> list[Entity]:
        """Get entities related to the given entity.

        Args:
            entity_id: The ID of the entity
            relation_type: Optional relation type to filter by
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of related entities
        """
        relations = self.get_relations(entity_id, relation_type, direction)
        related_entities = []

        for relation in relations:
            if relation.from_id == entity_id:
                related_entity = self.get_entity(relation.to_id)
                if related_entity:
                    related_entities.append(related_entity)
            else:
                related_entity = self.get_entity(relation.from_id)
                if related_entity:
                    related_entities.append(related_entity)

        return related_entities

    # Pattern operations

    def add_pattern(
        self,
        name: str,
        description: str,
        language: str | None = None,
        example: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a code pattern to the knowledge graph.

        Args:
            name: The name of the pattern
            description: Description of the pattern
            language: The programming language
            example: An example of the pattern
            metadata: Additional metadata

        Returns:
            The ID of the new pattern
        """
        pattern_id = self._generate_id("pattern")

        pattern = Pattern(
            pattern_id=pattern_id,
            name=name,
            description=description,
            language=language,
            example=example,
            metadata=metadata or {},
        )

        self.patterns[pattern_id] = pattern
        return pattern_id

    def get_pattern(self, pattern_id: str) -> Pattern | None:
        """Get a pattern by ID."""
        return self.patterns.get(pattern_id)

    def find_patterns(
        self, name: str | None = None, language: str | None = None
    ) -> list[Pattern]:
        """Find patterns by name and/or language.

        Args:
            name: Optional pattern name to search for
            language: Optional language to filter by

        Returns:
            List of matching patterns
        """
        results = []

        for pattern in self.patterns.values():
            if (name is None or pattern.name == name) and (
                language is None or pattern.language == language
            ):
                results.append(pattern)

        return results

    # Style convention operations

    def add_style_convention(
        self,
        name: str,
        description: str,
        language: str | None = None,
        examples: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a style convention to the knowledge graph.

        Args:
            name: The name of the convention
            description: Description of the convention
            language: The programming language
            examples: Examples of the convention
            metadata: Additional metadata

        Returns:
            The ID of the new convention
        """
        convention_id = self._generate_id("convention")

        convention = StyleConvention(
            convention_id=convention_id,
            name=name,
            description=description,
            language=language,
            examples=examples or [],
            metadata=metadata or {},
        )

        self.style_conventions[convention_id] = convention
        return convention_id

    def get_style_convention(self, convention_id: str) -> StyleConvention | None:
        """Get a style convention by ID."""
        return self.style_conventions.get(convention_id)

    def find_style_conventions(
        self, name: str | None = None, language: str | None = None
    ) -> list[StyleConvention]:
        """Find style conventions by name and/or language.

        Args:
            name: Optional convention name to search for
            language: Optional language to filter by

        Returns:
            List of matching conventions
        """
        results = []

        for convention in self.style_conventions.values():
            if (name is None or convention.name == name) and (
                language is None or convention.language == language
            ):
                results.append(convention)

        return results

    # Query operations

    def query_entities(
        self,
        entity_type: str | None = None,
        language: str | None = None,
        name_pattern: str | None = None,
        limit: int = 100,
    ) -> list[Entity]:
        """Query entities based on criteria.

        Args:
            entity_type: Filter by entity type
            language: Filter by programming language
            name_pattern: Filter by name pattern (regex)
            limit: Maximum number of results

        Returns:
            List of matching entities
        """
        results = []

        for entity in self.entities.values():
            # Apply filters
            if entity_type is not None and entity.entity_type != entity_type:
                continue

            if language is not None and entity.language != language:
                continue

            if name_pattern is not None:
                if not re.search(name_pattern, entity.name):
                    continue

            results.append(entity)

            if len(results) >= limit:
                break

        return results

    def get_entity_context(self, entity_id: str, depth: int = 1) -> dict[str, Any]:
        """Get an entity and its context.

        Args:
            entity_id: The ID of the entity
            depth: How many levels of relationships to include

        Returns:
            Dictionary with entity and related entities
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return {}

        # Start with the entity itself
        context = {
            "entity": entity,
            "relations": self.get_relations(entity_id),
            "related_entities": {},
        }

        # Add related entities
        if depth > 0:
            related_entities = self.get_related_entities(entity_id)

            for related_entity in related_entities:
                if depth > 1:
                    # Recursively get context for related entities
                    context["related_entities"][related_entity.entity_id] = (
                        self.get_entity_context(related_entity.entity_id, depth - 1)
                    )
                else:
                    # Just include the entity
                    context["related_entities"][related_entity.entity_id] = {
                        "entity": related_entity,
                        "relations": [],
                    }

        return context

    # Serialization

    def to_dict(self) -> dict[str, Any]:
        """Convert the knowledge graph to a dictionary."""
        return {
            "entities": {
                k: self._dataclass_to_dict(v) for k, v in self.entities.items()
            },
            "relations": {
                k: self._dataclass_to_dict(v) for k, v in self.relations.items()
            },
            "patterns": {
                k: self._dataclass_to_dict(v) for k, v in self.patterns.items()
            },
            "style_conventions": {
                k: self._dataclass_to_dict(v) for k, v in self.style_conventions.items()
            },
            "_next_id": self._next_id,
        }

    @staticmethod
    def _dataclass_to_dict(obj: Any) -> dict[str, Any]:
        """Convert a dataclass instance to a dictionary."""
        if hasattr(obj, "__dataclass_fields__"):
            return {k: v for k, v in obj.__dict__.items()}
        return obj

    def to_json(self) -> str:
        """Convert the knowledge graph to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeGraph":
        """Create a knowledge graph from a dictionary."""
        graph = cls()

        # Restore next_id
        graph._next_id = data.get("_next_id", 0)

        # Restore entities
        for entity_id, entity_data in data.get("entities", {}).items():
            entity = Entity(**entity_data)
            graph.entities[entity_id] = entity

        # Restore relations
        for relation_id, relation_data in data.get("relations", {}).items():
            relation = Relation(**relation_data)
            graph.relations[relation_id] = relation

        # Restore patterns
        for pattern_id, pattern_data in data.get("patterns", {}).items():
            pattern = Pattern(**pattern_data)
            graph.patterns[pattern_id] = pattern

        # Restore style conventions
        for convention_id, convention_data in data.get("style_conventions", {}).items():
            convention = StyleConvention(**convention_data)
            graph.style_conventions[convention_id] = convention

        return graph

    @classmethod
    def from_json(cls, json_str: str) -> "KnowledgeGraph":
        """Create a knowledge graph from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save_to_file(self, file_path: str) -> bool:
        """Save the knowledge graph to a file.

        Args:
            file_path: Path to the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            return True
        except Exception as e:
            print(f"Error saving knowledge graph: {str(e)}")
            return False

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional["KnowledgeGraph"]:
        """Load a knowledge graph from a file.

        Args:
            file_path: Path to the file

        Returns:
            The loaded knowledge graph, or None if failed
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return cls.from_json(f.read())
        except FileNotFoundError:
            print(f"Knowledge graph file not found: {file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_path}")
            return None
        except Exception as e:
            print(f"Error loading knowledge graph: {str(e)}")
            return None
