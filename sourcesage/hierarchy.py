"""Hierarchical compression for code memory storage."""

import ast
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HierarchyLevel(Enum):
    """Levels in the hierarchical compression system."""

    PROJECT = 0  # Project-wide information (structure, dependencies)
    MODULE = 1  # Module-level information (imports, exports)
    CLASS = 2  # Class-level information (methods, attributes)
    FUNCTION = 3  # Function-level information (signature, purpose)
    BLOCK = 4  # Code block information (loops, conditionals)
    LINE = 5  # Line-level details (specific implementations)


@dataclass
class CodeNode:
    """A node in the hierarchical code representation."""

    # Basic identification
    node_id: str
    name: str
    level: HierarchyLevel
    node_type: str  # "module", "class", "function", "method", etc.

    # Hierarchical relationships
    parent_id: str | None = None
    children_ids: set[str] = field(default_factory=set)

    # Content at this level (compressed representation)
    signature: str | None = None
    summary: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Full content (only stored at appropriate levels)
    content: str | None = None

    # Style information
    style_markers: dict[str, Any] = field(default_factory=dict)


class HierarchicalMemory:
    """Manages code memory using hierarchical compression."""

    def __init__(self):
        """Initialize the hierarchical memory system."""
        self.nodes: dict[str, CodeNode] = {}
        self.root_nodes: set[str] = set()
        self._next_id = 0

    def _generate_id(self) -> str:
        """Generate a unique ID for a node."""
        node_id = f"node_{self._next_id}"
        self._next_id += 1
        return node_id

    def add_node(
        self,
        name: str,
        level: HierarchyLevel,
        node_type: str,
        parent_id: str | None = None,
        **kwargs,
    ) -> str:
        """Add a node to the hierarchy.

        Args:
            name: The name of the node
            level: The hierarchy level
            node_type: The type of node
            parent_id: The ID of the parent node, if any
            **kwargs: Additional attributes for the node

        Returns:
            The ID of the new node
        """
        node_id = self._generate_id()

        # Create the node
        node = CodeNode(
            node_id=node_id,
            name=name,
            level=level,
            node_type=node_type,
            parent_id=parent_id,
            **kwargs,
        )

        # Add to the hierarchy
        self.nodes[node_id] = node

        # Update parent-child relationships
        if parent_id:
            if parent_id in self.nodes:
                self.nodes[parent_id].children_ids.add(node_id)
        else:
            # This is a root node
            self.root_nodes.add(node_id)

        return node_id

    def get_node(self, node_id: str) -> CodeNode | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_children(self, node_id: str) -> list[CodeNode]:
        """Get all children of a node."""
        node = self.get_node(node_id)
        if not node:
            return []

        return [
            self.nodes[child_id]
            for child_id in node.children_ids
            if child_id in self.nodes
        ]

    def get_parent(self, node_id: str) -> CodeNode | None:
        """Get the parent of a node."""
        node = self.get_node(node_id)
        if not node or not node.parent_id:
            return None

        return self.get_node(node.parent_id)

    def get_ancestors(self, node_id: str) -> list[CodeNode]:
        """Get all ancestors of a node, from parent to root."""
        ancestors = []
        current = self.get_node(node_id)

        while current and current.parent_id:
            parent = self.get_node(current.parent_id)
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break

        return ancestors

    def get_descendants(self, node_id: str) -> list[CodeNode]:
        """Get all descendants of a node."""
        descendants = []
        to_process = list(self.get_children(node_id))

        while to_process:
            current = to_process.pop(0)
            descendants.append(current)
            to_process.extend(self.get_children(current.node_id))

        return descendants

    def query(
        self,
        level: HierarchyLevel | None = None,
        node_type: str | None = None,
        name_pattern: str | None = None,
    ) -> list[CodeNode]:
        """Query nodes based on criteria.

        Args:
            level: Filter by hierarchy level
            node_type: Filter by node type
            name_pattern: Filter by name pattern (regex)

        Returns:
            List of matching nodes
        """
        results = []

        for node in self.nodes.values():
            # Apply filters
            if level is not None and node.level != level:
                continue

            if node_type is not None and node.node_type != node_type:
                continue

            if name_pattern is not None:
                if not re.search(name_pattern, node.name):
                    continue

            results.append(node)

        return results

    def summarize_node(self, node_id: str) -> dict[str, Any]:
        """Generate a summary of a node and its context."""
        node = self.get_node(node_id)
        if not node:
            return {}

        # Get context
        parent = self.get_parent(node_id)
        children = self.get_children(node_id)

        # Create summary
        summary = {
            "id": node.node_id,
            "name": node.name,
            "type": node.node_type,
            "level": node.level.name,
            "signature": node.signature,
            "summary": node.summary,
            "parent": parent.name if parent else None,
            "children": [child.name for child in children],
            "metadata": node.metadata,
        }

        return summary


class CodeAnalyzer:
    """Analyzes code and builds a hierarchical representation."""

    def __init__(self, memory: HierarchicalMemory):
        """Initialize the analyzer.

        Args:
            memory: The hierarchical memory to populate
        """
        self.memory = memory

    def analyze_file(self, file_path: str) -> list[str]:
        """Analyze a single file and add it to the hierarchy.

        Args:
            file_path: Path to the file to analyze

        Returns:
            List of node IDs created
        """
        if not os.path.isfile(file_path):
            return []

        # Read the file
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Not a valid Python file
            return []

        # Create module node
        module_name = os.path.basename(file_path)
        module_id = self.memory.add_node(
            name=module_name,
            level=HierarchyLevel.MODULE,
            node_type="module",
            signature=f"module {module_name}",
            summary=f"Module defined in {file_path}",
            metadata={"path": file_path},
        )

        # Process imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))

        if imports:
            self.memory.nodes[module_id].metadata["imports"] = imports

        # Process classes and functions
        node_ids = [module_id]

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_id = self._process_class(node, module_id)
                if class_id:
                    node_ids.append(class_id)
            elif isinstance(node, ast.FunctionDef):
                func_id = self._process_function(node, module_id)
                if func_id:
                    node_ids.append(func_id)

        return node_ids

    def _process_class(self, node: ast.ClassDef, parent_id: str) -> str | None:
        """Process a class definition.

        Args:
            node: The AST node
            parent_id: The ID of the parent node

        Returns:
            The ID of the created node, or None if failed
        """
        # Extract class information
        class_name = node.name
        bases = [ast.unparse(base) for base in node.bases]
        docstring = ast.get_docstring(node)

        # Create signature
        signature = f"class {class_name}"
        if bases:
            signature += f"({', '.join(bases)})"

        # Create summary
        summary = docstring.split("\n")[0] if docstring else f"Class {class_name}"

        # Create the node
        class_id = self.memory.add_node(
            name=class_name,
            level=HierarchyLevel.CLASS,
            node_type="class",
            parent_id=parent_id,
            signature=signature,
            summary=summary,
            content=ast.unparse(node),
            metadata={"bases": bases, "docstring": docstring},
        )

        # Process methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._process_function(item, class_id, is_method=True)

        return class_id

    def _process_function(
        self, node: ast.FunctionDef, parent_id: str, is_method: bool = False
    ) -> str | None:
        """Process a function definition.

        Args:
            node: The AST node
            parent_id: The ID of the parent node
            is_method: Whether this is a method

        Returns:
            The ID of the created node, or None if failed
        """
        # Extract function information
        func_name = node.name
        docstring = ast.get_docstring(node)

        # Create signature
        args = []
        for arg in node.args.args:
            args.append(arg.arg)

        signature = f"def {func_name}({', '.join(args)})"

        # Create summary
        summary = docstring.split("\n")[0] if docstring else f"Function {func_name}"

        # Create the node
        node_type = "method" if is_method else "function"
        level = HierarchyLevel.FUNCTION

        func_id = self.memory.add_node(
            name=func_name,
            level=level,
            node_type=node_type,
            parent_id=parent_id,
            signature=signature,
            summary=summary,
            content=ast.unparse(node),
            metadata={"args": args, "docstring": docstring},
        )

        return func_id

    def analyze_directory(self, directory_path: str) -> list[str]:
        """Analyze all Python files in a directory.

        Args:
            directory_path: Path to the directory

        Returns:
            List of node IDs created
        """
        if not os.path.isdir(directory_path):
            return []

        # Create project node
        project_name = os.path.basename(directory_path)
        project_id = self.memory.add_node(
            name=project_name,
            level=HierarchyLevel.PROJECT,
            node_type="project",
            signature=f"project {project_name}",
            summary=f"Project at {directory_path}",
            metadata={"path": directory_path},
        )

        # Process all Python files
        node_ids = [project_id]

        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    file_node_ids = self.analyze_file(file_path)

                    # Link module to project
                    if file_node_ids:
                        module_id = file_node_ids[0]
                        self.memory.nodes[module_id].parent_id = project_id
                        self.memory.nodes[project_id].children_ids.add(module_id)

                    node_ids.extend(file_node_ids)

        return node_ids
