"""
Fabric Game Test Integration Tests for fabricpy.

Mirrors the Fabric GameTest framework described in:
https://docs.fabricmc.net/develop/automatic-testing

These tests verify that fabricpy generates valid game-test infrastructure:
- fabricApi { configureTests { ... } } in build.gradle
- createSourceSet with modId and eula
- Separate fabric.mod.json for gametest source set
- Server game tests implementing FabricGameTest / CustomTestMethodInvoker
- Client game tests implementing FabricClientGameTest
- @GameTest annotations with template and timeoutTicks
- Game test entrypoints in fabric.mod.json
- Block placement/assertion patterns (assertBlockPresent, succeed)
- Client game test world builder and screenshot capture
"""

import json
import os
import shutil
import tempfile

import pytest

from fabricpy import (
    Block,
    FoodItem,
    Item,
    ItemGroup,
    ModConfig,
    RecipeJson,
    ToolItem,
    item_group,
)

# ------------------------------------------------------------------ #
#  Fixtures                                                           #
# ------------------------------------------------------------------ #


@pytest.fixture
def tmp_project(tmp_path):
    """Temporary project directory."""
    project_dir = str(tmp_path / "gametest-mod")
    yield project_dir
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)


@pytest.fixture
def gametest_mod(tmp_project):
    """ModConfig configured with game tests enabled."""
    mod = ModConfig(
        mod_id="gtmod",
        name="GameTest Mod",
        version="1.0.0",
        description="Testing game test generation",
        authors=["pytest"],
        project_dir=tmp_project,
        enable_testing=True,
        generate_unit_tests=True,
        generate_game_tests=True,
    )

    # Items
    mod.registerItem(
        Item(
            id="gtmod:test_sword",
            name="Test Sword",
            max_stack_size=1,
            item_group=item_group.COMBAT,
        )
    )
    mod.registerItem(
        FoodItem(
            id="gtmod:test_apple",
            name="Test Apple",
            nutrition=4,
            saturation=2.4,
            item_group=item_group.FOOD_AND_DRINK,
        )
    )
    mod.registerItem(
        ToolItem(
            id="gtmod:test_pickaxe",
            name="Test Pickaxe",
            durability=250,
            mining_speed_multiplier=6.0,
            attack_damage=2.0,
        )
    )

    # Blocks
    mod.registerBlock(
        Block(
            id="gtmod:test_ore",
            name="Test Ore",
            item_group=item_group.NATURAL,
        )
    )
    mod.registerBlock(
        Block(
            id="gtmod:test_bricks",
            name="Test Bricks",
            item_group=item_group.BUILDING_BLOCKS,
        )
    )

    return mod


def _prepare_project(project_dir):
    """Create minimal project structure for game test generation."""
    os.makedirs(project_dir, exist_ok=True)
    with open(os.path.join(project_dir, "build.gradle"), "w") as f:
        f.write("dependencies {}\n")


# ================================================================== #
# Section 1 – Setting up Game Tests with Fabric Loom                 #
# Verifies build.gradle gets fabricApi { configureTests { ... } }     #
# ================================================================== #


class TestGameTestLoomSetup:
    """Verify build.gradle game test configuration when enabled."""

    def test_configure_tests_block_added(self, gametest_mod, tmp_project):
        """build.gradle should have fabricApi { configureTests { ... } }."""
        _prepare_project(tmp_project)
        gametest_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "configureTests" in content, (
            "build.gradle must include configureTests block per Fabric docs"
        )

    def test_configure_tests_has_create_source_set(self, gametest_mod, tmp_project):
        """configureTests should set createSourceSet = true."""
        _prepare_project(tmp_project)
        gametest_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "createSourceSet" in content

    def test_configure_tests_has_eula(self, gametest_mod, tmp_project):
        """configureTests should accept eula = true."""
        _prepare_project(tmp_project)
        gametest_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "eula" in content

    def test_no_game_test_config_when_disabled(self, tmp_project):
        """When generate_game_tests=False, configureTests should NOT be added."""
        mod = ModConfig(
            mod_id="nogt",
            name="No GT",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
            generate_game_tests=False,
        )
        _prepare_project(tmp_project)
        mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "configureTests" not in content, (
            "Should not add game test config when generate_game_tests=False"
        )


# ================================================================== #
# Section 2 – Game Test Directory Structure                          #
# Verifies src/gametest/ structure and fabric.mod.json                #
# ================================================================== #


class TestGameTestDirectoryStructure:
    """Verify the gametest source set directory structure."""

    def test_gametest_java_dir_created(self, gametest_mod, tmp_project):
        """src/gametest/java/ directory should be created."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        gametest_dir = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            gametest_mod.mod_id,
        )
        assert os.path.isdir(gametest_dir)

    def test_gametest_resources_dir_created(self, gametest_mod, tmp_project):
        """src/gametest/resources/ directory should be created."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        resources_dir = os.path.join(tmp_project, "src", "gametest", "resources")
        assert os.path.isdir(resources_dir)

    def test_gametest_fabric_mod_json_created(self, gametest_mod, tmp_project):
        """fabric.mod.json should be created in src/gametest/resources/."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        mod_json_path = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "resources",
            "fabric.mod.json",
        )
        assert os.path.isfile(mod_json_path)

    def test_gametest_fabric_mod_json_schema(self, gametest_mod, tmp_project):
        """fabric.mod.json should have correct schema version and structure."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        mod_json_path = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "resources",
            "fabric.mod.json",
        )
        with open(mod_json_path) as f:
            data = json.load(f)

        assert data["schemaVersion"] == 1
        assert "id" in data
        assert "entrypoints" in data

    def test_gametest_fabric_mod_json_entrypoints(self, gametest_mod, tmp_project):
        """fabric.mod.json should have fabric-gametest and fabric-client-gametest
        entrypoints as per Fabric docs."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        mod_json_path = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "resources",
            "fabric.mod.json",
        )
        with open(mod_json_path) as f:
            data = json.load(f)

        entrypoints = data["entrypoints"]
        assert "fabric-gametest" in entrypoints, (
            "Must have fabric-gametest entrypoint for server tests"
        )
        assert "fabric-client-gametest" in entrypoints, (
            "Must have fabric-client-gametest entrypoint for client tests"
        )

    def test_gametest_mod_id_is_test_variant(self, gametest_mod, tmp_project):
        """Game test mod ID should be a test variant of the main mod ID."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        mod_json_path = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "resources",
            "fabric.mod.json",
        )
        with open(mod_json_path) as f:
            data = json.load(f)

        assert "test" in data["id"], "Game test mod ID should contain 'test'"


# ================================================================== #
# Section 3 – Server Game Tests                                      #
# Verifies generated server-side game test Java files                 #
# ================================================================== #


class TestServerGameTests:
    """Verify generated server game test files follow Fabric patterns."""

    def _get_server_test_content(self, mod, project_dir):
        """Generate and return server game test content."""
        _prepare_project(project_dir)
        mod.generate_fabric_game_tests(project_dir)

        gametest_dir = os.path.join(
            project_dir,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            mod.mod_id,
        )
        for fname in os.listdir(gametest_dir):
            if "Server" in fname and fname.endswith(".java"):
                with open(os.path.join(gametest_dir, fname)) as f:
                    return f.read()
        pytest.fail("No server game test file found")

    def test_server_test_file_generated(self, gametest_mod, tmp_project):
        """A server game test .java file should be generated."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        gametest_dir = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            gametest_mod.mod_id,
        )
        java_files = [f for f in os.listdir(gametest_dir) if "Server" in f]
        assert len(java_files) >= 1

    def test_server_test_has_gametest_annotation(self, gametest_mod, tmp_project):
        """Server test should use @GameTest annotation."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        assert "@GameTest" in content, "Server tests must use @GameTest annotation"

    def test_server_test_has_game_test_helper(self, gametest_mod, tmp_project):
        """Server test methods should accept GameTestHelper parameter."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        assert "GameTestHelper" in content

    def test_server_test_calls_succeed(self, gametest_mod, tmp_project):
        """Server tests should call context.complete() or context.succeed()."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        assert "complete()" in content or "succeed()" in content, (
            "Server tests must signal completion"
        )

    def test_server_test_has_empty_structure(self, gametest_mod, tmp_project):
        """Server tests should reference EMPTY_STRUCTURE template."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        assert "EMPTY_STRUCTURE" in content

    def test_server_test_has_timeout(self, gametest_mod, tmp_project):
        """@GameTest should specify timeoutTicks."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        assert "timeoutTicks" in content

    def test_server_test_tests_items(self, gametest_mod, tmp_project):
        """Server test should create ItemStack for registered items."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        assert "ItemStack" in content

    def test_server_test_tests_block_placement(self, gametest_mod, tmp_project):
        """Server test should test block placement with setBlockState."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        # Block tests should reference Blocks or setBlockState
        assert (
            "Blocks" in content or "setBlockState" in content or "BlockPos" in content
        )

    def test_server_test_references_registered_items(self, gametest_mod, tmp_project):
        """Server test should reference each registered item."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        for item in gametest_mod.registered_items:
            if item.id and ":" in item.id:
                _, path = item.id.split(":", 1)
                assert path in content, f"Server test should reference item {item.id}"

    def test_server_test_references_registered_blocks(self, gametest_mod, tmp_project):
        """Server test should reference each registered block."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        for block in gametest_mod.registered_blocks:
            if block.id and ":" in block.id:
                _, path = block.id.split(":", 1)
                assert path in content, f"Server test should reference block {block.id}"

    def test_server_test_checks_food_component(self, gametest_mod, tmp_project):
        """Server test should check food component for FoodItems."""
        content = self._get_server_test_content(gametest_mod, tmp_project)
        has_food = any(isinstance(i, FoodItem) for i in gametest_mod.registered_items)
        if has_food:
            assert "FOOD" in content or "food" in content.lower(), (
                "Should test food component for registered FoodItems"
            )


# ================================================================== #
# Section 4 – Client Game Tests                                      #
# Verifies generated client-side game test Java files                 #
# ================================================================== #


class TestClientGameTests:
    """Verify generated client game test files follow Fabric patterns."""

    def _get_client_test_content(self, mod, project_dir):
        """Generate and return client game test content."""
        _prepare_project(project_dir)
        mod.generate_fabric_game_tests(project_dir)

        gametest_dir = os.path.join(
            project_dir,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            mod.mod_id,
        )
        for fname in os.listdir(gametest_dir):
            if "Client" in fname and fname.endswith(".java"):
                with open(os.path.join(gametest_dir, fname)) as f:
                    return f.read()
        pytest.fail("No client game test file found")

    def test_client_test_file_generated(self, gametest_mod, tmp_project):
        """A client game test .java file should be generated."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        gametest_dir = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            gametest_mod.mod_id,
        )
        client_files = [f for f in os.listdir(gametest_dir) if "Client" in f]
        assert len(client_files) >= 1

    def test_client_test_implements_fabric_client_gametest(
        self, gametest_mod, tmp_project
    ):
        """Client test should implement FabricClientGameTest."""
        content = self._get_client_test_content(gametest_mod, tmp_project)
        assert "FabricClientGameTest" in content

    def test_client_test_has_run_test_method(self, gametest_mod, tmp_project):
        """Client test should override runTest(ClientGameTestContext)."""
        content = self._get_client_test_content(gametest_mod, tmp_project)
        assert "runTest" in content
        assert "ClientGameTestContext" in content

    def test_client_test_uses_world_builder(self, gametest_mod, tmp_project):
        """Client test should use context.worldBuilder() as per Fabric docs."""
        content = self._get_client_test_content(gametest_mod, tmp_project)
        assert "worldBuilder" in content

    def test_client_test_takes_screenshot(self, gametest_mod, tmp_project):
        """Client test should capture a screenshot for verification."""
        content = self._get_client_test_content(gametest_mod, tmp_project)
        assert "takeScreenshot" in content or "screenshot" in content.lower()

    def test_client_test_uses_singleplayer_context(self, gametest_mod, tmp_project):
        """Client test should use TestSingleplayerContext."""
        content = self._get_client_test_content(gametest_mod, tmp_project)
        assert "TestSingleplayerContext" in content or "singleplayer" in content.lower()


# ================================================================== #
# Section 5 – _has_game_tests Detection                              #
# ================================================================== #


class TestGameTestDetection:
    """Test _has_game_tests method for detecting existing game tests."""

    def test_no_game_tests_empty_project(self, gametest_mod, tmp_project):
        """Should return False for a project with no gametest directory."""
        os.makedirs(tmp_project, exist_ok=True)
        assert gametest_mod._has_game_tests(tmp_project) is False

    def test_no_game_tests_empty_dir(self, gametest_mod, tmp_project):
        """Should return False for empty gametest directory."""
        gametest_dir = os.path.join(tmp_project, "src", "gametest", "java")
        os.makedirs(gametest_dir, exist_ok=True)
        assert gametest_mod._has_game_tests(tmp_project) is False

    def test_has_game_tests_with_java_file(self, gametest_mod, tmp_project):
        """Should return True when .java files exist in gametest dir."""
        gametest_dir = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "java",
            "com",
            "example",
        )
        os.makedirs(gametest_dir, exist_ok=True)
        with open(os.path.join(gametest_dir, "TestClass.java"), "w") as f:
            f.write("public class TestClass {}")

        assert gametest_mod._has_game_tests(tmp_project) is True

    def test_has_game_tests_non_java_ignored(self, gametest_mod, tmp_project):
        """Non-.java files should not count as game tests."""
        gametest_dir = os.path.join(tmp_project, "src", "gametest", "java")
        os.makedirs(gametest_dir, exist_ok=True)
        with open(os.path.join(gametest_dir, "readme.txt"), "w") as f:
            f.write("Not a test")

        assert gametest_mod._has_game_tests(tmp_project) is False


# ================================================================== #
# Section 6 – End-to-End: Full Game Test Generation Flow             #
# ================================================================== #


class TestEndToEndGameTestGeneration:
    """Test the complete game test generation workflow."""

    def test_full_generation_produces_all_files(self, gametest_mod, tmp_project):
        """Full game test generation should create all expected files."""
        _prepare_project(tmp_project)

        # Generate both unit and game tests
        gametest_mod.setup_fabric_testing(tmp_project)
        gametest_mod.generate_fabric_unit_tests(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        # Check unit test files
        unit_test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            gametest_mod.mod_id,
            "test",
        )
        assert os.path.isfile(os.path.join(unit_test_dir, "ItemRegistrationTest.java"))
        assert os.path.isfile(os.path.join(unit_test_dir, "RecipeValidationTest.java"))
        assert os.path.isfile(os.path.join(unit_test_dir, "ModIntegrationTest.java"))

        # Check game test files
        gametest_dir = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            gametest_mod.mod_id,
        )
        java_files = os.listdir(gametest_dir)
        assert any("Server" in f for f in java_files)
        assert any("Client" in f for f in java_files)

        # Check gametest fabric.mod.json
        assert os.path.isfile(
            os.path.join(
                tmp_project,
                "src",
                "gametest",
                "resources",
                "fabric.mod.json",
            )
        )

        # Check build.gradle
        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()
        assert "fabric-loader-junit" in content
        assert "configureTests" in content

    def test_entrypoints_match_generated_classes(self, gametest_mod, tmp_project):
        """Entrypoints in fabric.mod.json should match the generated class names."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        # Read entrypoints
        mod_json_path = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "resources",
            "fabric.mod.json",
        )
        with open(mod_json_path) as f:
            data = json.load(f)

        server_entrypoints = data["entrypoints"]["fabric-gametest"]
        client_entrypoints = data["entrypoints"]["fabric-client-gametest"]

        # Read generated file names
        gametest_dir = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            gametest_mod.mod_id,
        )
        java_files = os.listdir(gametest_dir)

        # Verify entrypoints reference actual generated classes
        for ep in server_entrypoints:
            class_name = ep.split(".")[-1]
            assert any(class_name in f for f in java_files), (
                f"Server entrypoint {ep} should match a generated file"
            )

        for ep in client_entrypoints:
            class_name = ep.split(".")[-1]
            assert any(class_name in f for f in java_files), (
                f"Client entrypoint {ep} should match a generated file"
            )

    def test_game_tests_enabled_adds_config_to_build_gradle(
        self, gametest_mod, tmp_project
    ):
        """When game tests are enabled, build.gradle should have fabricApi config."""
        _prepare_project(tmp_project)
        gametest_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "fabricApi" in content
        assert "configureTests" in content

    def test_multiple_blocks_generate_multiple_block_tests(
        self, gametest_mod, tmp_project
    ):
        """Each registered block should get its own test in server game tests."""
        _prepare_project(tmp_project)
        gametest_mod.generate_fabric_game_tests(tmp_project)

        gametest_dir = os.path.join(
            tmp_project,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            gametest_mod.mod_id,
        )
        for fname in os.listdir(gametest_dir):
            if "Server" in fname:
                with open(os.path.join(gametest_dir, fname)) as f:
                    content = f.read()
                for block in gametest_mod.registered_blocks:
                    if block.id and ":" in block.id:
                        _, path = block.id.split(":", 1)
                        assert path in content, f"Block {block.id} should be tested"


# ================================================================== #
# Section 7 – GitHub Actions Integration                             #
# Verifies build.gradle is CI-ready with test reports & artifacts     #
# ================================================================== #


class TestGitHubActionsIntegration:
    """Test that the generated testing setup is compatible with GitHub Actions."""

    def test_build_gradle_has_test_results_output(self, gametest_mod, tmp_project):
        """build.gradle test block should configure output useful for CI."""
        _prepare_project(tmp_project)
        gametest_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        # Test logging is configured for CI visibility
        assert "testLogging" in content or "showStackTraces" in content

    def test_build_gradle_sets_fabric_development(self, gametest_mod, tmp_project):
        """Tests should run with fabric.development=true system property."""
        _prepare_project(tmp_project)
        gametest_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "fabric.development" in content

    def test_build_gradle_max_heap_size(self, gametest_mod, tmp_project):
        """Test task should set adequate heap size for Minecraft bootstrap."""
        _prepare_project(tmp_project)
        gametest_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "maxHeapSize" in content or "Xmx" in content
