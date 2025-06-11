#!/usr/bin/env python3
"""
Test to verify the new conditional game testing behavior.
"""

import tempfile
import os
from fabricpy.modconfig import ModConfig
from fabricpy.item import Item

def test_default_no_game_tests():
    """Test that by default, game testing config is NOT added."""
    print("Testing default behavior (no game tests)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = os.path.join(temp_dir, "test_default")
        
        # Create ModConfig with default settings (generate_game_tests=False)
        mod_config = ModConfig(
            mod_id="test-default",
            name="Test Default",
            version="1.0.0", 
            description="Test default behavior",
            authors=["Test Author"],
            project_dir=project_dir,
            enable_testing=True  # Enable testing but not game tests
        )
        
        # Add an item and compile
        test_item = Item(id="test-default:item", name="Test Item")
        mod_config.registerItem(test_item)
        mod_config.compile()
        
        # Check build.gradle
        build_gradle_path = os.path.join(project_dir, "build.gradle")
        with open(build_gradle_path, 'r') as f:
            content = f.read()
        
        # Should have basic testing dependencies
        assert "fabric-loader-junit" in content, "Should have basic testing dependencies"
        assert "test {" in content, "Should have test configuration"
        assert "useJUnitPlatform" in content, "Should use JUnit platform"
        
        # Should NOT have game testing config
        assert "fabricApi {" not in content, "Should NOT have game testing config by default"
        assert "configureTests" not in content, "Should NOT have configureTests by default"
        
        print("✅ Default behavior correct: basic testing yes, game testing no")

def test_explicit_game_tests_enabled():
    """Test that explicitly enabling game tests works."""
    print("Testing explicit game tests enabled...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = os.path.join(temp_dir, "test_explicit")
        
        # Create ModConfig with game tests explicitly enabled
        mod_config = ModConfig(
            mod_id="test-explicit",
            name="Test Explicit",
            version="1.0.0",
            description="Test explicit game tests",
            authors=["Test Author"],
            project_dir=project_dir,
            enable_testing=True,
            generate_game_tests=True  # Explicitly enable
        )
        
        # Add an item and compile
        test_item = Item(id="test-explicit:item", name="Test Item")
        mod_config.registerItem(test_item)
        mod_config.compile()
        
        # Check build.gradle
        build_gradle_path = os.path.join(project_dir, "build.gradle")
        with open(build_gradle_path, 'r') as f:
            content = f.read()
        
        # Should have basic testing dependencies
        assert "fabric-loader-junit" in content, "Should have basic testing dependencies"
        assert "test {" in content, "Should have test configuration"
        
        # Should ALSO have game testing config
        assert "fabricApi {" in content, "SHOULD have game testing config when explicitly enabled"
        assert "configureTests" in content, "SHOULD have configureTests when explicitly enabled"
        
        print("✅ Explicit enable behavior correct: both basic and game testing added")

def test_existing_game_tests_detected():
    """Test that existing game tests are detected."""
    print("Testing existing game tests detection...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = os.path.join(temp_dir, "test_existing")
        
        # Create ModConfig with default settings
        mod_config = ModConfig(
            mod_id="test-existing",
            name="Test Existing",
            version="1.0.0",
            description="Test existing game tests detection",
            authors=["Test Author"],
            project_dir=project_dir,
            enable_testing=True
            # generate_game_tests=False by default
        )
        
        # Create project directory and existing game test files
        os.makedirs(project_dir)
        gametest_dir = os.path.join(project_dir, "src", "gametest", "java", "com", "example")
        os.makedirs(gametest_dir, exist_ok=True)
        with open(os.path.join(gametest_dir, "ExistingTest.java"), 'w') as f:
            f.write("// Existing game test")
        
        # Create build.gradle manually first
        build_gradle_path = os.path.join(project_dir, "build.gradle")
        with open(build_gradle_path, 'w') as f:
            f.write("// Basic build.gradle\nplugins { id 'fabric-loom' }")
        
        # Call _enhance_build_gradle_for_testing directly
        mod_config._enhance_build_gradle_for_testing(project_dir)
        
        # Check build.gradle
        with open(build_gradle_path, 'r') as f:
            content = f.read()
        
        # Should have basic testing dependencies
        assert "fabric-loader-junit" in content, "Should have basic testing dependencies"
        assert "test {" in content, "Should have test configuration"
        
        # Should ALSO have game testing config because existing tests were detected
        assert "fabricApi {" in content, "SHOULD have game testing config when existing tests detected"
        assert "configureTests" in content, "SHOULD have configureTests when existing tests detected"
        
        print("✅ Existing tests detection correct: game testing config added")

if __name__ == "__main__":
    print("🧪 Testing conditional game testing behavior...\n")
    
    test_default_no_game_tests()
    test_explicit_game_tests_enabled()
    test_existing_game_tests_detected()
    
    print("\n🎉 All conditional game testing tests passed!")
    print("\n📋 Verified behaviors:")
    print("   ✅ Default: basic testing only (no game tests)")
    print("   ✅ Explicit enable: both basic and game testing")
    print("   ✅ Existing tests: automatically enables game testing")
    print("   ✅ Build issues prevented by disabling game tests by default")
