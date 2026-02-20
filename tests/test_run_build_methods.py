"""
Tests for the .run() and .build() methods of ModConfig.

These tests verify that the run() and build() methods work correctly
and properly configure gradle.properties with the required properties.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from fabricpy.item import Item
from fabricpy.modconfig import ModConfig


class TestRunBuildMethods(unittest.TestCase):
    """Test the run() and build() methods of ModConfig."""

    def setUp(self):
        """Set up temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "test_project")
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_run_method_success(self):
        """Test run() method executes successfully."""
        with (
            patch("fabricpy.modconfig.subprocess.check_call") as mock_subprocess,
            patch("fabricpy.modconfig.os.chdir") as mock_chdir,
            patch("fabricpy.modconfig.os.getcwd", return_value="/original/dir"),
        ):
            mod_config = ModConfig(
                mod_id="test-run-mod",
                name="Test Run Mod",
                version="1.0.0",
                description="Test mod for run method",
                authors=["Test Author"],
                project_dir=self.project_dir,
            )

            # Create project directory and gradle.properties
            os.makedirs(self.project_dir)
            gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
            with open(gradle_props_path, "w") as f:
                f.write("# Test gradle.properties\n")

            # Call run method
            mod_config.run()

            # Verify gradle.properties was updated
            with open(gradle_props_path, "r") as f:
                content = f.read()

            self.assertIn("archives_base_name=test-run-mod", content)
            self.assertIn("mod_id=test-run-mod", content)

            # Verify directory changes and subprocess call
            mock_chdir.assert_any_call(self.project_dir)
            mock_chdir.assert_any_call("/original/dir")
            mock_subprocess.assert_called_once_with(["./gradlew", "runClient"])

    def test_run_method_project_not_exists(self):
        """Test run() method raises FileNotFoundError when project doesn't exist."""
        mod_config = ModConfig(
            mod_id="test-run-mod",
            name="Test Run Mod",
            version="1.0.0",
            description="Test mod",
            authors=["Test Author"],
            project_dir=self.project_dir,
        )

        # Don't create project directory
        with self.assertRaises(FileNotFoundError) as context:
            mod_config.run()

        self.assertIn("does not exist", str(context.exception))
        self.assertIn("Run compile() first", str(context.exception))

    def test_run_method_gradle_failure(self):
        """Test run() method handles Gradle failures gracefully."""
        with (
            patch("fabricpy.modconfig.subprocess.check_call") as mock_subprocess,
            patch("fabricpy.modconfig.os.chdir") as mock_chdir,
            patch("fabricpy.modconfig.os.getcwd", return_value="/original/dir"),
        ):
            mock_subprocess.side_effect = subprocess.CalledProcessError(
                1, ["./gradlew", "runClient"]
            )

            mod_config = ModConfig(
                mod_id="test-gradle-fail",
                name="Test Gradle Fail",
                version="1.0.0",
                description="Test mod",
                authors=["Test Author"],
                project_dir=self.project_dir,
            )

            # Create project directory and gradle.properties
            os.makedirs(self.project_dir)
            gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
            with open(gradle_props_path, "w") as f:
                f.write("# Test gradle.properties\n")

            # Should raise CalledProcessError
            with self.assertRaises(subprocess.CalledProcessError):
                mod_config.run()

            # Should still restore original directory
            mock_chdir.assert_any_call("/original/dir")

    def test_build_method_success(self):
        """Test build() method executes successfully."""
        with patch("fabricpy.modconfig.subprocess.check_call") as mock_subprocess:
            mod_config = ModConfig(
                mod_id="test-build-mod",
                name="Test Build Mod",
                version="1.0.0",
                description="Test mod for build method",
                authors=["Test Author"],
                project_dir=self.project_dir,
            )

            # Create project directory and gradle.properties
            os.makedirs(self.project_dir)
            gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
            with open(gradle_props_path, "w") as f:
                f.write("# Test gradle.properties\n")

            # Call build method
            mod_config.build()

            # Verify gradle.properties was updated
            with open(gradle_props_path, "r") as f:
                content = f.read()

            self.assertIn("archives_base_name=test-build-mod", content)
            self.assertIn("mod_id=test-build-mod", content)

            # Verify subprocess call
            mock_subprocess.assert_called_once_with(
                ["./gradlew", "build"], cwd=self.project_dir
            )

    def test_build_method_project_not_exists(self):
        """Test build() method raises RuntimeError when project doesn't exist."""
        mod_config = ModConfig(
            mod_id="test-build-mod",
            name="Test Build Mod",
            version="1.0.0",
            description="Test mod",
            authors=["Test Author"],
            project_dir=self.project_dir,
        )

        # Don't create project directory
        with self.assertRaises(RuntimeError) as context:
            mod_config.build()

        self.assertIn("Project directory not found", str(context.exception))
        self.assertIn("call compile() first", str(context.exception))

    def test_build_method_gradle_failure(self):
        """Test build() method handles Gradle failures gracefully."""
        with patch("fabricpy.modconfig.subprocess.check_call") as mock_subprocess:
            mock_subprocess.side_effect = subprocess.CalledProcessError(
                1, ["./gradlew", "build"]
            )

            mod_config = ModConfig(
                mod_id="test-gradle-fail",
                name="Test Gradle Fail",
                version="1.0.0",
                description="Test mod",
                authors=["Test Author"],
                project_dir=self.project_dir,
            )

            # Create project directory
            os.makedirs(self.project_dir)
            gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
            with open(gradle_props_path, "w") as f:
                f.write("# Test gradle.properties\n")

            # Should raise CalledProcessError
            with self.assertRaises(subprocess.CalledProcessError):
                mod_config.build()

    def test_gradle_properties_properly_configured(self):
        """Test that gradle.properties is properly configured with required properties."""
        mod_config = ModConfig(
            mod_id="test-gradle-props",
            name="Test Gradle Props",
            version="1.0.0",
            description="Test mod",
            authors=["Test Author"],
            project_dir=self.project_dir,
        )

        # Create project directory and basic gradle.properties
        os.makedirs(self.project_dir)
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        with open(gradle_props_path, "w") as f:
            f.write("# Basic gradle.properties\nsome_other_property=value\n")

        # Call _ensure_gradle_properties directly
        mod_config._ensure_gradle_properties(self.project_dir)

        # Verify all required properties are present
        with open(gradle_props_path, "r") as f:
            content = f.read()

        # Since the method now overwrites the file, check for the complete template
        self.assertIn("archives_base_name=test-gradle-props", content)
        self.assertIn("mod_id=test-gradle-props", content)
        self.assertIn("org.gradle.jvmargs=-Xmx1G", content)
        self.assertIn("loom_version=1.15-SNAPSHOT", content)
        self.assertIn("org.gradle.parallel=true", content)
        self.assertIn("mod_version=1.0.0", content)
        self.assertIn("maven_group=com.example", content)
        self.assertIn("minecraft_version=1.21.11", content)
        self.assertIn("loader_version=0.18.4", content)
        self.assertIn("fabric_version=0.141.3+1.21.11", content)
        # Note: some_other_property should NOT be preserved since file is overwritten

    def test_run_and_build_with_complex_mod_id(self):
        """Test run() and build() methods with complex mod IDs containing special characters."""
        complex_mod_id = "test-mod_with.special-chars"

        with patch("fabricpy.modconfig.subprocess.check_call") as mock_subprocess:
            mod_config = ModConfig(
                mod_id=complex_mod_id,
                name="Complex Mod ID Test",
                version="1.0.0",
                description="Test mod with complex ID",
                authors=["Test Author"],
                project_dir=self.project_dir,
            )

            # Create project directory and gradle.properties
            os.makedirs(self.project_dir)
            gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
            with open(gradle_props_path, "w") as f:
                f.write("# Test gradle.properties\n")

            # Test build method
            mod_config.build()

            # Verify gradle.properties handles special characters
            with open(gradle_props_path, "r") as f:
                content = f.read()

            self.assertIn(f"archives_base_name={complex_mod_id}", content)
            self.assertIn(f"mod_id={complex_mod_id}", content)

            # Verify subprocess call
            mock_subprocess.assert_called_once_with(
                ["./gradlew", "build"], cwd=self.project_dir
            )

    def test_run_and_build_integration_workflow(self):
        """Test a complete integration workflow: compile -> build -> run."""
        with (
            patch("fabricpy.modconfig.subprocess.check_call") as mock_subprocess,
            patch("fabricpy.modconfig.os.chdir"),
            patch("fabricpy.modconfig.os.getcwd", return_value="/original/dir"),
        ):
            mod_config = ModConfig(
                mod_id="integration-test",
                name="Integration Test Mod",
                version="1.0.0",
                description="Test integration workflow",
                authors=["Test Author"],
                project_dir=self.project_dir,
            )

            # Add some components
            test_item = Item(id="integration-test:test_item", name="Test Item")
            mod_config.registerItem(test_item)

            # Create project directory and gradle.properties (simulating compile)
            os.makedirs(self.project_dir)
            gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
            with open(gradle_props_path, "w") as f:
                f.write("# Generated gradle.properties\n")

            # Test build
            mod_config.build()

            # Verify gradle.properties was configured for build
            with open(gradle_props_path, "r") as f:
                content = f.read()
            self.assertIn("archives_base_name=integration-test", content)
            self.assertIn("mod_id=integration-test", content)

            # Verify build was called
            mock_subprocess.assert_called_with(
                ["./gradlew", "build"], cwd=self.project_dir
            )

            # Reset mock for run test
            mock_subprocess.reset_mock()

            # Test run
            mod_config.run()

            # Verify run was called
            mock_subprocess.assert_called_with(["./gradlew", "runClient"])

    def test_gradle_properties_no_duplication(self):
        """Test that gradle.properties gets recreated with correct format."""
        mod_config = ModConfig(
            mod_id="no-duplication-test",
            name="No Duplication Test",
            version="1.0.0",
            description="Test no duplication",
            authors=["Test Author"],
            project_dir=self.project_dir,
        )

        # Create project directory and gradle.properties with existing properties
        os.makedirs(self.project_dir)
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        original_content = """# Existing gradle.properties
archives_base_name=old-value
mod_id=old-value
org.gradle.jvmargs=-Xmx3G
org.gradle.parallel=false
some_custom_property=keep_me
"""
        with open(gradle_props_path, "w") as f:
            f.write(original_content)

        # Call _ensure_gradle_properties multiple times
        mod_config._ensure_gradle_properties(self.project_dir)
        mod_config._ensure_gradle_properties(self.project_dir)
        mod_config._ensure_gradle_properties(self.project_dir)

        # Verify file was overwritten with correct template format
        with open(gradle_props_path, "r") as f:
            final_content = f.read()

        # Should have exactly one of each property with correct values
        self.assertEqual(final_content.count("archives_base_name="), 1)
        self.assertEqual(final_content.count("mod_id="), 1)
        self.assertEqual(final_content.count("org.gradle.jvmargs="), 1)
        self.assertEqual(final_content.count("org.gradle.parallel="), 1)

        # Should have the new values, not the old ones
        self.assertIn("archives_base_name=no-duplication-test", final_content)
        self.assertIn("mod_id=no-duplication-test", final_content)
        self.assertIn("org.gradle.jvmargs=-Xmx1G", final_content)
        self.assertIn("org.gradle.parallel=true", final_content)

        # Should NOT preserve existing custom properties since file is overwritten
        self.assertNotIn("some_custom_property=keep_me", final_content)


if __name__ == "__main__":
    unittest.main()
