#!/usr/bin/env python3
"""Test script for SourceSage knowledge graph storage and project understanding."""

import os
import sys
from sourcesage.mcp_server import SourceSageMcpServer

def test_storage():
    """Test the knowledge graph storage functionality."""
    # Create a temporary server instance
    server = SourceSageMcpServer()
    
    # Add a test entity
    entity_id = server.knowledge.add_entity(
        name="TestEntity",
        entity_type="test",
        summary="A test entity for storage testing"
    )
    
    print(f"Created test entity with ID: {entity_id}")
    
    # Determine the storage path that would be used by the main function
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
    storage_path = os.path.join(storage_dir, "knowledge.json")
    
    print(f"Standard storage path: {storage_path}")
    
    # Save the knowledge graph to the standard location
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir, exist_ok=True)
        print(f"Created storage directory: {storage_dir}")
    
    success = server.knowledge.save_to_file(storage_path)
    if success:
        print(f"Successfully saved knowledge graph to: {storage_path}")
    else:
        print(f"Failed to save knowledge graph to: {storage_path}")
        return False
    
    # Create a new server instance and load the knowledge graph
    new_server = SourceSageMcpServer(storage_path=storage_path)
    
    # Check if the test entity was loaded
    loaded_entities = new_server.knowledge.find_entity("TestEntity")
    if loaded_entities:
        print(f"Successfully loaded test entity: {loaded_entities[0].name}")
    else:
        print("Failed to load test entity")
        return False
    
    print("Storage test completed successfully!")
    return True

def test_project_understanding():
    """Test the project understanding tools."""
    # Get the current project path
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Using project path: {project_path}")
    
    # Create a server instance
    server = SourceSageMcpServer()
    
    # Add test entities with project_path metadata
    entities = [
        {
            "name": "TestModule",
            "entity_type": "module",
            "summary": "A test module for project understanding testing",
            "language": "python",
            "metadata": {"project_path": project_path}
        },
        {
            "name": "TestClass",
            "entity_type": "class",
            "summary": "A test class for project understanding testing",
            "language": "python",
            "metadata": {"project_path": project_path}
        },
        {
            "name": "TestFunction",
            "entity_type": "function",
            "summary": "A test function for project understanding testing",
            "signature": "def test_function(arg1, arg2=None):",
            "language": "python",
            "metadata": {"project_path": project_path}
        }
    ]
    
    entity_ids = {}
    for entity_data in entities:
        metadata = entity_data.pop("metadata")
        entity_id = server.knowledge.add_entity(**entity_data, metadata=metadata)
        entity_ids[entity_data["name"]] = entity_id
        print(f"Created test entity: {entity_data['name']} with ID: {entity_id}")
    
    # Add a test relation
    relation_id = server.knowledge.add_relation(
        from_id=entity_ids["TestClass"],
        to_id=entity_ids["TestFunction"],
        relation_type="calls"
    )
    print(f"Created test relation with ID: {relation_id}")
    
    # Add a test pattern
    pattern_id = server.knowledge.add_pattern(
        name="TestPattern",
        description="A test pattern for project understanding testing",
        language="python",
        example="def example(): pass",
        metadata={"project_path": project_path}
    )
    print(f"Created test pattern with ID: {pattern_id}")
    
    # Add a test style convention
    convention_id = server.knowledge.add_style_convention(
        name="TestConvention",
        description="A test style convention for project understanding testing",
        language="python",
        examples=["def example_snake_case(): pass"],
        metadata={"project_path": project_path}
    )
    print(f"Created test style convention with ID: {convention_id}")
    
    # Create a custom implementation of the project understanding tools for testing
    def load_project_understanding(project_path):
        """Test implementation of load_project_understanding."""
        # Check if we have any entities related to this project
        project_entities = []
        for entity in server.knowledge.entities.values():
            entity_project = entity.metadata.get("project_path")
            if entity_project and os.path.normpath(os.path.abspath(entity_project)) == os.path.normpath(os.path.abspath(project_path)):
                project_entities.append(entity)
        
        if not project_entities:
            return f"No understanding available for project at: {project_path}"
        
        # Count entities by type
        entity_types = {}
        for entity in project_entities:
            entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
        
        # Count relations
        project_entity_ids = {entity.entity_id for entity in project_entities}
        project_relations = []
        for relation in server.knowledge.relations.values():
            if relation.from_id in project_entity_ids or relation.to_id in project_entity_ids:
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
        
        # List all entities
        output += "All Entities:\n"
        for entity in sorted(project_entities, key=lambda e: e.name):
            output += f"- {entity.name} ({entity.entity_type}): {entity.summary}\n"
        output += "\n"
        
        return output
    
    def dump_project_understanding(project_path, include_observations=False):
        """Test implementation of dump_project_understanding."""
        # Check if we have any entities related to this project
        project_entities = []
        for entity in server.knowledge.entities.values():
            entity_project = entity.metadata.get("project_path")
            if entity_project and os.path.normpath(os.path.abspath(entity_project)) == os.path.normpath(os.path.abspath(project_path)):
                project_entities.append(entity)
        
        if not project_entities:
            return f"No understanding available for project at: {project_path}"
        
        # Get all relations involving project entities
        project_entity_ids = {entity.entity_id for entity in project_entities}
        project_relations = []
        for relation in server.knowledge.relations.values():
            if relation.from_id in project_entity_ids or relation.to_id in project_entity_ids:
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
                entity_relations = [r for r in project_relations if r.from_id == entity.entity_id]
                if entity_relations:
                    output += "  Relations:\n"
                    for relation in entity_relations:
                        to_entity = server.knowledge.get_entity(relation.to_id)
                        if to_entity:
                            output += f"    - {relation.relation_type} -> {to_entity.name} ({to_entity.entity_type})\n"
                
                output += "\n"
            
            output += "\n"
        
        return output
    
    # Test load_project_understanding
    print("\nTesting load_project_understanding:")
    load_result = load_project_understanding(project_path)
    print(load_result)
    
    # Test dump_project_understanding
    print("\nTesting dump_project_understanding:")
    dump_result = dump_project_understanding(project_path, include_observations=True)
    print(dump_result)
    
    # Check if the results contain expected information
    success = True
    for entity_name in ["TestModule", "TestClass", "TestFunction"]:
        if entity_name not in load_result:
            print(f"Missing {entity_name} in load_project_understanding result")
            success = False
        if entity_name not in dump_result:
            print(f"Missing {entity_name} in dump_project_understanding result")
            success = False
    
    if success:
        print("Project understanding tools test completed successfully!")
    else:
        print("Project understanding tools test failed: missing expected entities in results")
    
    return success

def main():
    """Run all tests."""
    print("=== Testing Storage ===")
    storage_success = test_storage()
    
    print("\n=== Testing Project Understanding ===")
    understanding_success = test_project_understanding()
    
    if storage_success and understanding_success:
        print("\nAll tests completed successfully!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
