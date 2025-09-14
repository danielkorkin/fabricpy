"""
Simple test to verify Fabric testing integration works.
"""

import unittest
import tempfile
import os

from fabricpy import ModConfig


class TestFabricTestingIntegration(unittest.TestCase):
    """Test basic Fabric testing integration."""

    def test_modconfig_with_testing_enabled(self):
        """Test creating ModConfig with testing enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mod = ModConfig(
                mod_id="test_mod",
                name="Test Mod",
                version="1.0.0",
                description="A test mod",
                authors=["test"],
                project_dir=os.path.join(temp_dir, "test-mod"),
                enable_testing=True,
                generate_unit_tests=True,
                generate_game_tests=True
            )
            
            # Verify testing flags are set
            self.assertTrue(mod.enable_testing)
            self.assertTrue(mod.generate_unit_tests)
            self.assertTrue(mod.generate_game_tests)

    def test_modconfig_with_testing_disabled(self):
        """Test creating ModConfig with testing disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mod = ModConfig(
                mod_id="test_mod_no_testing",
                name="Test Mod No Testing",
                version="1.0.0", 
                description="A test mod without testing",
                authors=["test"],
                project_dir=os.path.join(temp_dir, "test-mod-no-testing"),
                enable_testing=False
            )
            
            # Verify testing is disabled
            self.assertFalse(mod.enable_testing)

    def test_testing_methods_exist(self):
        """Test that testing methods exist on ModConfig."""
        mod = ModConfig(
            mod_id="test_mod",
            name="Test Mod",
            version="1.0.0",
            description="A test mod",
            authors=["test"]
        )
        
        # Verify testing methods exist
        self.assertTrue(hasattr(mod, 'setup_fabric_testing'))
        self.assertTrue(hasattr(mod, 'generate_fabric_unit_tests'))
        self.assertTrue(hasattr(mod, 'generate_fabric_game_tests'))


if __name__ == '__main__':
    unittest.main()
