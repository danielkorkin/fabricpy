#!/usr/bin/env python3
"""
Test script to demonstrate the new gradle.properties format.
"""

import tempfile
import os
from fabricpy.modconfig import ModConfig

def test_gradle_properties_format():
    """Test that gradle.properties is created with the exact format specified."""
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = os.path.join(temp_dir, "test_mod")
        
        # Create a ModConfig instance
        mod_config = ModConfig(
            mod_id="modid",
            name="Test Mod",
            version="1.0.0",
            description="Test mod",
            authors=["Test Author"],
            project_dir=project_dir
        )
        
        # Create project directory
        os.makedirs(project_dir)
        
        # Create a dummy gradle.properties file
        gradle_props_path = os.path.join(project_dir, "gradle.properties")
        with open(gradle_props_path, 'w') as f:
            f.write("# Old content\nold_property=value\n")
        
        # Call _ensure_gradle_properties to create the standard format
        mod_config._ensure_gradle_properties(project_dir)
        
        # Read the resulting file
        with open(gradle_props_path, 'r') as f:
            content = f.read()
        
        print("Generated gradle.properties content:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        # Verify it matches the expected format
        expected_lines = [
            "# Done to increase the memory available to gradle.",
            "org.gradle.jvmargs=-Xmx1G",
            "org.gradle.parallel=true",
            "",
            "# Fabric Properties",
            "# check these on https://fabricmc.net/develop",
            "minecraft_version=1.21.5",
            "yarn_mappings=1.21.5+build.1",
            "loader_version=0.16.10",
            "",
            "# Mod Properties",
            "mod_version=1.0.0",
            "maven_group=com.example",
            "archives_base_name=modid",
            "mod_id=modid",
            "",
            "# Dependencies",
            "fabric_version=0.119.5+1.21.5",
            ""
        ]
        
        actual_lines = content.split('\n')
        
        print("Verification:")
        for i, expected_line in enumerate(expected_lines):
            if i < len(actual_lines):
                actual_line = actual_lines[i]
                if actual_line == expected_line:
                    print(f"✅ Line {i+1}: '{expected_line}'")
                else:
                    print(f"❌ Line {i+1}: Expected '{expected_line}', got '{actual_line}'")
            else:
                print(f"❌ Line {i+1}: Missing line '{expected_line}'")
        
        print(f"\nTotal lines: {len(actual_lines)} (expected: {len(expected_lines)})")

if __name__ == "__main__":
    test_gradle_properties_format()
