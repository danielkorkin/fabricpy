"""
Fabric Unit Testing Integration Tests for fabricpy.

Mirrors the Fabric Loader JUnit testing pattern described in:
https://docs.fabricmc.net/develop/automatic-testing

These tests verify that fabricpy generates valid Java unit tests following
the Fabric testing conventions:
- SharedConstants.tryDetectVersion() / Bootstrap.bootStrap() setup
- JUnit 5 @Test / @BeforeAll annotations
- Registry-dependent class initialization
- build.gradle test dependency configuration
- GitHub Actions CI integration artifacts

Each test class mirrors a section from the Fabric documentation.
"""

import json
import os
import shutil
import tempfile
import textwrap

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
    message,
)

# ------------------------------------------------------------------ #
#  Fixtures                                                           #
# ------------------------------------------------------------------ #


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory and clean up after."""
    project_dir = str(tmp_path / "test-mod")
    yield project_dir
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)


@pytest.fixture
def basic_mod(tmp_project):
    """A minimal ModConfig with one item registered."""
    mod = ModConfig(
        mod_id="testmod",
        name="Test Mod",
        version="1.0.0",
        description="Unit testing mod",
        authors=["pytest"],
        project_dir=tmp_project,
        enable_testing=True,
        generate_unit_tests=True,
        generate_game_tests=False,
    )
    item = Item(id="testmod:basic_item", name="Basic Item")
    mod.registerItem(item)
    return mod


@pytest.fixture
def full_mod(tmp_project):
    """A ModConfig with items, food, tools, blocks, and recipes."""
    mod = ModConfig(
        mod_id="fullmod",
        name="Full Mod",
        version="2.0.0",
        description="Full integration testing mod",
        authors=["pytest", "fabricpy"],
        project_dir=tmp_project,
        enable_testing=True,
        generate_unit_tests=True,
        generate_game_tests=True,
    )

    # Basic item with recipe
    sword = Item(
        id="fullmod:ruby_sword",
        name="Ruby Sword",
        max_stack_size=1,
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["#", "#", "/"],
                "key": {"#": "minecraft:emerald", "/": "minecraft:stick"},
                "result": {"id": "fullmod:ruby_sword", "count": 1},
            }
        ),
        item_group=item_group.COMBAT,
    )
    mod.registerItem(sword)

    # Food item
    berry = FoodItem(
        id="fullmod:magic_berry",
        name="Magic Berry",
        nutrition=6,
        saturation=0.8,
        always_edible=True,
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shapeless",
                "ingredients": ["minecraft:sweet_berries", "minecraft:glowstone_dust"],
                "result": {"id": "fullmod:magic_berry", "count": 2},
            }
        ),
        item_group=item_group.FOOD_AND_DRINK,
    )
    mod.registerItem(berry)

    # Tool item
    pickaxe = ToolItem(
        id="fullmod:ruby_pickaxe",
        name="Ruby Pickaxe",
        durability=500,
        mining_speed_multiplier=8.0,
        attack_damage=3.0,
        mining_level=2,
        enchantability=22,
        repair_ingredient="minecraft:emerald",
        item_group=item_group.TOOLS,
    )
    mod.registerItem(pickaxe)

    # Block
    block = Block(
        id="fullmod:ruby_block",
        name="Ruby Block",
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["###", "###", "###"],
                "key": {"#": "minecraft:emerald"},
                "result": {"id": "fullmod:ruby_block", "count": 1},
            }
        ),
        item_group=item_group.BUILDING_BLOCKS,
    )
    mod.registerBlock(block)

    return mod


# ================================================================== #
# Section 1 – Setting up Fabric Loader JUnit                         #
# Verifies build.gradle gets the correct testImplementation entries   #
# and useJUnitPlatform() call.                                        #
# ================================================================== #


class TestFabricLoaderJUnitSetup:
    """Test that build.gradle is enhanced with Fabric testing deps."""

    def test_build_gradle_adds_junit_dependency(self, basic_mod, tmp_project):
        """build.gradle should contain fabric-loader-junit dependency."""
        # Create a minimal project structure with build.gradle
        os.makedirs(tmp_project, exist_ok=True)
        build_gradle = os.path.join(tmp_project, "build.gradle")
        with open(build_gradle, "w") as f:
            f.write("plugins { id 'fabric-loom' }\ndependencies {}\n")

        basic_mod.setup_fabric_testing(tmp_project)

        with open(build_gradle) as f:
            content = f.read()

        assert "fabric-loader-junit" in content, (
            "build.gradle must include fabric-loader-junit (per Fabric docs)"
        )

    def test_build_gradle_uses_junit_platform(self, basic_mod, tmp_project):
        """build.gradle should declare useJUnitPlatform()."""
        os.makedirs(tmp_project, exist_ok=True)
        build_gradle = os.path.join(tmp_project, "build.gradle")
        with open(build_gradle, "w") as f:
            f.write("plugins { id 'fabric-loom' }\n")

        basic_mod.setup_fabric_testing(tmp_project)

        with open(build_gradle) as f:
            content = f.read()

        assert "useJUnitPlatform()" in content, (
            "build.gradle must call useJUnitPlatform() as per Fabric docs"
        )

    def test_build_gradle_adds_junit_jupiter(self, basic_mod, tmp_project):
        """build.gradle should include JUnit Jupiter dependency."""
        os.makedirs(tmp_project, exist_ok=True)
        with open(os.path.join(tmp_project, "build.gradle"), "w") as f:
            f.write("dependencies {}\n")

        basic_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "junit-jupiter" in content, "build.gradle should include JUnit Jupiter"

    def test_build_gradle_idempotent(self, basic_mod, tmp_project):
        """Calling setup_fabric_testing twice should not duplicate entries."""
        os.makedirs(tmp_project, exist_ok=True)
        with open(os.path.join(tmp_project, "build.gradle"), "w") as f:
            f.write("dependencies {}\n")

        basic_mod.setup_fabric_testing(tmp_project)
        basic_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert content.count("fabric-loader-junit") == 1, (
            "Fabric testing deps should only be added once"
        )

    def test_build_gradle_test_logging(self, basic_mod, tmp_project):
        """build.gradle should configure test logging for passed/skipped/failed."""
        os.makedirs(tmp_project, exist_ok=True)
        with open(os.path.join(tmp_project, "build.gradle"), "w") as f:
            f.write("dependencies {}\n")

        basic_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        for event in ("passed", "skipped", "failed"):
            assert event in content, f"Test logging should include '{event}' events"


# ================================================================== #
# Section 2 – Writing Unit Tests                                     #
# Verifies generated Java test files follow JUnit patterns from docs  #
# ================================================================== #


class TestWritingUnitTests:
    """Test that generated Java unit tests follow Fabric JUnit conventions."""

    def _generate_tests(self, mod, project_dir):
        """Helper to create project structure and generate tests."""
        os.makedirs(project_dir, exist_ok=True)
        test_dir = os.path.join(
            project_dir,
            "src",
            "test",
            "java",
            "com",
            "example",
            mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        mod.generate_fabric_unit_tests(project_dir)
        return test_dir

    def test_item_registration_test_generated(self, basic_mod, tmp_project):
        """ItemRegistrationTest.java should be generated."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        assert os.path.isfile(os.path.join(test_dir, "ItemRegistrationTest.java"))

    def test_recipe_validation_test_generated(self, basic_mod, tmp_project):
        """RecipeValidationTest.java should be generated."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        assert os.path.isfile(os.path.join(test_dir, "RecipeValidationTest.java"))

    def test_mod_integration_test_generated(self, basic_mod, tmp_project):
        """ModIntegrationTest.java should be generated."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        assert os.path.isfile(os.path.join(test_dir, "ModIntegrationTest.java"))

    def test_generated_test_has_before_all_bootstrap(self, basic_mod, tmp_project):
        """Generated tests should call SharedConstants.tryDetectVersion()
        and Bootstrap.bootStrap() in @BeforeAll, as per Fabric docs for
        registry-dependent tests."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        assert "@BeforeAll" in content, "Must have @BeforeAll annotation"
        assert "SharedConstants.tryDetectVersion()" in content, (
            "Must bootstrap SharedConstants per Fabric docs"
        )
        assert "Bootstrap.bootStrap()" in content, (
            "Must bootstrap registries per Fabric docs"
        )

    def test_generated_test_has_junit_test_annotation(self, basic_mod, tmp_project):
        """Each test method should use @Test annotation from JUnit Jupiter."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        assert "import org.junit.jupiter.api.Test;" in content
        assert "@Test" in content

    def test_generated_test_uses_assertions(self, basic_mod, tmp_project):
        """Generated tests should use JUnit Assertions class."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        assert "Assertions" in content, "Tests should use JUnit Assertions"

    def test_generated_test_has_display_name(self, basic_mod, tmp_project):
        """Generated tests should use @DisplayName for readable test output."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        assert "@DisplayName" in content

    def test_generated_test_package_follows_convention(self, basic_mod, tmp_project):
        """Test package should follow the test naming convention:
        com.example.<mod_id>.test (as recommended in Fabric docs)."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        assert f"package com.example.{basic_mod.mod_id}.test;" in content

    def test_generated_test_mirrors_source_structure(self, basic_mod, tmp_project):
        """Test directory should be at src/test/java/ (Fabric convention)."""
        self._generate_tests(basic_mod, tmp_project)
        expected = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            basic_mod.mod_id,
            "test",
        )
        assert os.path.isdir(expected)

    def test_vanilla_diamond_test_generated(self, basic_mod, tmp_project):
        """Generated tests should include a vanilla item test
        (like the testDiamondItemStack example in Fabric docs)."""
        test_dir = self._generate_tests(basic_mod, tmp_project)
        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        # The test should verify vanilla Items are accessible (registry working)
        assert "Items.DIAMOND" in content or "testVanillaItemsAccessible" in content, (
            "Should test vanilla registry access like Fabric docs' diamond example"
        )


# ================================================================== #
# Section 3 – Setting Up Registries                                  #
# Verifies that generated tests handle registry bootstrapping         #
# ================================================================== #


class TestSettingUpRegistries:
    """Verify registry bootstrapping is correctly inserted in generated tests."""

    def test_all_test_files_have_bootstrap(self, full_mod, tmp_project):
        """Every generated test class should bootstrap registries."""
        os.makedirs(tmp_project, exist_ok=True)
        test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            full_mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        full_mod.generate_fabric_unit_tests(tmp_project)

        for fname in os.listdir(test_dir):
            if fname.endswith(".java"):
                with open(os.path.join(test_dir, fname)) as f:
                    content = f.read()
                assert "SharedConstants.tryDetectVersion()" in content, (
                    f"{fname} must call SharedConstants.tryDetectVersion()"
                )
                assert "Bootstrap.bootStrap()" in content, (
                    f"{fname} must call Bootstrap.bootStrap()"
                )

    def test_bootstrap_before_registry_access(self, full_mod, tmp_project):
        """Bootstrap calls must appear in @BeforeAll, before any registry usage in methods."""
        os.makedirs(tmp_project, exist_ok=True)
        test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            full_mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        full_mod.generate_fabric_unit_tests(tmp_project)

        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        bootstrap_pos = content.find("Bootstrap.bootStrap()")
        # Find BuiltInRegistries usage in method bodies (after @BeforeAll block),
        # not in import statements at the top
        method_body_start = content.find("@BeforeAll")
        if method_body_start >= 0:
            registry_pos = content.find("BuiltInRegistries.ITEM", method_body_start)
        else:
            registry_pos = -1

        # If both exist, bootstrap should come first
        if bootstrap_pos >= 0 and registry_pos >= 0:
            assert bootstrap_pos < registry_pos, (
                "Bootstrap must be called before any registry access in methods"
            )

    def test_item_registry_check_for_each_registered_item(self, full_mod, tmp_project):
        """Integration test should verify each registered item is in the registry."""
        os.makedirs(tmp_project, exist_ok=True)
        test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            full_mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        full_mod.generate_fabric_unit_tests(tmp_project)

        path = os.path.join(test_dir, "ModIntegrationTest.java")
        with open(path) as f:
            content = f.read()

        for item in full_mod.registered_items:
            if item.id and ":" in item.id:
                namespace, path_part = item.id.split(":", 1)
                assert path_part in content, (
                    f"Integration test should reference {item.id}"
                )

    def test_food_properties_tested(self, full_mod, tmp_project):
        """Generated tests should verify food properties (nutrition, saturation)."""
        os.makedirs(tmp_project, exist_ok=True)
        test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            full_mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        full_mod.generate_fabric_unit_tests(tmp_project)

        path = os.path.join(test_dir, "ItemRegistrationTest.java")
        with open(path) as f:
            content = f.read()

        # The food item should have property assertions
        assert (
            "FoodProperties" in content
            or "foodComponent" in content
            or "FOOD" in content
        ), "Should test food item properties like nutrition/saturation"


# ================================================================== #
# Section 4 – Gradle Properties                                      #
# Verifies gradle.properties has the right loader_version for JUnit   #
# ================================================================== #


class TestGradleProperties:
    """Test that gradle.properties is set up correctly for Fabric testing."""

    def test_gradle_properties_created(self, basic_mod, tmp_project):
        """gradle.properties should be created with required properties."""
        os.makedirs(tmp_project, exist_ok=True)
        basic_mod._ensure_gradle_properties(tmp_project)

        path = os.path.join(tmp_project, "gradle.properties")
        assert os.path.isfile(path)

    def test_gradle_properties_has_loader_version(self, basic_mod, tmp_project):
        """gradle.properties must have loader_version (used by fabric-loader-junit dep)."""
        os.makedirs(tmp_project, exist_ok=True)
        basic_mod._ensure_gradle_properties(tmp_project)

        with open(os.path.join(tmp_project, "gradle.properties")) as f:
            content = f.read()

        assert "loader_version" in content, (
            "gradle.properties must have loader_version for "
            'testImplementation "net.fabricmc:fabric-loader-junit:${project.loader_version}"'
        )

    def test_gradle_properties_has_mod_id(self, basic_mod, tmp_project):
        """gradle.properties should contain mod_id."""
        os.makedirs(tmp_project, exist_ok=True)
        basic_mod._ensure_gradle_properties(tmp_project)

        with open(os.path.join(tmp_project, "gradle.properties")) as f:
            content = f.read()

        assert f"mod_id={basic_mod.mod_id}" in content

    def test_gradle_properties_has_minecraft_version(self, basic_mod, tmp_project):
        """gradle.properties should specify minecraft_version."""
        os.makedirs(tmp_project, exist_ok=True)
        basic_mod._ensure_gradle_properties(tmp_project)

        with open(os.path.join(tmp_project, "gradle.properties")) as f:
            content = f.read()

        assert "minecraft_version" in content

    def test_gradle_properties_has_fabric_version(self, basic_mod, tmp_project):
        """gradle.properties should specify fabric_version."""
        os.makedirs(tmp_project, exist_ok=True)
        basic_mod._ensure_gradle_properties(tmp_project)

        with open(os.path.join(tmp_project, "gradle.properties")) as f:
            content = f.read()

        assert "fabric_version" in content

    def test_gradle_properties_has_loom_version(self, basic_mod, tmp_project):
        """gradle.properties should specify loom_version for Fabric Loom."""
        os.makedirs(tmp_project, exist_ok=True)
        basic_mod._ensure_gradle_properties(tmp_project)

        with open(os.path.join(tmp_project, "gradle.properties")) as f:
            content = f.read()

        assert "loom_version" in content


# ================================================================== #
# Section 5 – Recipe Validation Tests                                #
# Verifies generated recipe tests validate type & result_id           #
# ================================================================== #


class TestRecipeValidation:
    """Test that recipe validation tests are correctly generated."""

    def test_recipe_types_tested(self, full_mod, tmp_project):
        """Generated recipe test should validate recipe types."""
        os.makedirs(tmp_project, exist_ok=True)
        test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            full_mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        full_mod.generate_fabric_unit_tests(tmp_project)

        path = os.path.join(test_dir, "RecipeValidationTest.java")
        with open(path) as f:
            content = f.read()

        assert "RecipeType" in content, "Recipe test should reference RecipeType"

    def test_recipe_result_ids_tested(self, full_mod, tmp_project):
        """Generated recipe test should validate recipe result IDs match item IDs."""
        os.makedirs(tmp_project, exist_ok=True)
        test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            full_mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        full_mod.generate_fabric_unit_tests(tmp_project)

        path = os.path.join(test_dir, "RecipeValidationTest.java")
        with open(path) as f:
            content = f.read()

        assert "testRecipeResultIds" in content

    def test_recipe_test_has_bootstrap(self, full_mod, tmp_project):
        """Recipe validation test should also bootstrap registries."""
        os.makedirs(tmp_project, exist_ok=True)
        test_dir = os.path.join(
            tmp_project,
            "src",
            "test",
            "java",
            "com",
            "example",
            full_mod.mod_id,
            "test",
        )
        os.makedirs(test_dir, exist_ok=True)
        full_mod.generate_fabric_unit_tests(tmp_project)

        path = os.path.join(test_dir, "RecipeValidationTest.java")
        with open(path) as f:
            content = f.read()

        assert "SharedConstants.tryDetectVersion()" in content
        assert "Bootstrap.bootStrap()" in content


# ================================================================== #
# Section 6 – Unit Test Task Configuration                           #
# build.gradle should have a unitTest task that excludes GameTests    #
# ================================================================== #


class TestUnitTestTaskConfig:
    """Test that a separate unitTest Gradle task is defined."""

    def test_unit_test_task_defined(self, basic_mod, tmp_project):
        """build.gradle should have a unitTest task."""
        os.makedirs(tmp_project, exist_ok=True)
        with open(os.path.join(tmp_project, "build.gradle"), "w") as f:
            f.write("dependencies {}\n")

        basic_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "unitTest" in content, "build.gradle should define a unitTest task"

    def test_unit_test_excludes_game_tests(self, basic_mod, tmp_project):
        """unitTest task should exclude *GameTest.class files."""
        os.makedirs(tmp_project, exist_ok=True)
        with open(os.path.join(tmp_project, "build.gradle"), "w") as f:
            f.write("dependencies {}\n")

        basic_mod.setup_fabric_testing(tmp_project)

        with open(os.path.join(tmp_project, "build.gradle")) as f:
            content = f.read()

        assert "GameTest" in content, "unitTest task should exclude GameTest classes"


# ================================================================== #
# Section 7 – ModConfig & Java Constant Generation                   #
# ================================================================== #


class TestJavaConstantGeneration:
    """Test _to_java_constant produces valid Java identifiers."""

    @pytest.mark.parametrize(
        "input_id, expected",
        [
            ("mymod:cool_item", "MYMOD_COOL_ITEM"),
            ("my-special.item", "MY_SPECIAL_ITEM"),
            ("simple", "SIMPLE"),
            ("a:b-c.d", "A_B_C_D"),
        ],
    )
    def test_to_java_constant(self, basic_mod, input_id, expected):
        assert basic_mod._to_java_constant(input_id) == expected

    def test_constant_starts_with_digit_prefixed(self, basic_mod):
        """Java constants cannot start with a digit; prefix with _."""
        result = basic_mod._to_java_constant("123invalid")
        assert result.startswith("_"), "Must prefix digit-leading names with _"
        assert result == "_123INVALID"

    def test_constant_empty_chars_removed(self, basic_mod):
        """Non-alphanumeric/underscore chars should be stripped."""
        result = basic_mod._to_java_constant("my@mod#item")
        assert "@" not in result
        assert "#" not in result


# ================================================================== #
# Section 8 – ModConfig Registration API                             #
# ================================================================== #


class TestModConfigRegistration:
    """Test item/block registration with ModConfig."""

    def test_register_item(self, tmp_project):
        mod = ModConfig(
            mod_id="regtest",
            name="Reg Test",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
        )
        item = Item(id="regtest:test", name="Test")
        mod.registerItem(item)
        assert len(mod.registered_items) == 1
        assert mod.registered_items[0] is item

    def test_register_food_item(self, tmp_project):
        mod = ModConfig(
            mod_id="regtest",
            name="Reg Test",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
        )
        food = FoodItem(id="regtest:apple", name="Apple", nutrition=4, saturation=2.4)
        mod.registerFoodItem(food)
        assert len(mod.registered_items) == 1
        assert isinstance(mod.registered_items[0], FoodItem)

    def test_register_block(self, tmp_project):
        mod = ModConfig(
            mod_id="regtest",
            name="Reg Test",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
        )
        block = Block(id="regtest:stone", name="Stone")
        mod.registerBlock(block)
        assert len(mod.registered_blocks) == 1
        assert mod.registered_blocks[0] is block

    def test_register_multiple_items(self, tmp_project):
        mod = ModConfig(
            mod_id="regtest",
            name="Reg Test",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
        )
        for i in range(10):
            mod.registerItem(Item(id=f"regtest:item_{i}", name=f"Item {i}"))
        assert len(mod.registered_items) == 10

    def test_register_tool_item(self, tmp_project):
        mod = ModConfig(
            mod_id="regtest",
            name="Reg Test",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
        )
        tool = ToolItem(
            id="regtest:pick",
            name="Pick",
            durability=100,
            mining_speed_multiplier=6.0,
        )
        mod.registerItem(tool)
        assert isinstance(mod.registered_items[0], ToolItem)

    def test_modconfig_testing_flags_defaults(self, tmp_project):
        mod = ModConfig(
            mod_id="flagtest",
            name="Flag Test",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
        )
        assert mod.enable_testing is True
        assert mod.generate_unit_tests is True
        assert mod.generate_game_tests is False

    def test_modconfig_custom_testing_flags(self, tmp_project):
        mod = ModConfig(
            mod_id="flagtest",
            name="Flag Test",
            version="1.0.0",
            description="test",
            authors=["t"],
            project_dir=tmp_project,
            enable_testing=False,
            generate_unit_tests=False,
            generate_game_tests=True,
        )
        assert mod.enable_testing is False
        assert mod.generate_unit_tests is False
        assert mod.generate_game_tests is True


# ================================================================== #
# Section 9 – Item Classes                                           #
# ================================================================== #


class TestItemClasses:
    """Test Item, FoodItem, ToolItem constructors and defaults."""

    def test_item_defaults(self):
        item = Item(id="mod:x", name="X")
        assert item.max_stack_size == 64
        assert item.texture_path is None
        assert item.recipe is None
        assert item.item_group is None

    def test_food_item_defaults(self):
        food = FoodItem(id="mod:f", name="F")
        assert food.nutrition == 0
        assert food.saturation == 0.0
        assert food.always_edible is False
        assert food.max_stack_size == 64

    def test_food_item_inherits_item(self):
        food = FoodItem(id="mod:f", name="F")
        assert isinstance(food, Item)

    def test_tool_item_defaults(self):
        tool = ToolItem(id="mod:t", name="T")
        assert tool.max_stack_size == 1  # Tools stack to 1
        assert tool.durability == 0
        assert tool.mining_speed_multiplier == 1.0
        assert tool.attack_damage == 1.0
        assert tool.mining_level == 0
        assert tool.enchantability == 0
        assert tool.repair_ingredient is None

    def test_tool_item_custom_values(self):
        tool = ToolItem(
            id="mod:pick",
            name="Pick",
            durability=1561,
            mining_speed_multiplier=8.0,
            attack_damage=5.0,
            mining_level=3,
            enchantability=10,
            repair_ingredient="minecraft:diamond",
        )
        assert tool.durability == 1561
        assert tool.mining_speed_multiplier == 8.0
        assert tool.attack_damage == 5.0
        assert tool.mining_level == 3
        assert tool.enchantability == 10
        assert tool.repair_ingredient == "minecraft:diamond"

    def test_item_with_item_group(self):
        item = Item(id="mod:x", name="X", item_group=item_group.COMBAT)
        assert item.item_group == "combat"

    def test_item_with_custom_item_group(self):
        grp = ItemGroup(id="custom_tab", name="Custom Tab")
        item = Item(id="mod:x", name="X", item_group=grp)
        assert item.item_group is grp


# ================================================================== #
# Section 10 – Block Class                                           #
# ================================================================== #


class TestBlockClass:
    """Test Block constructor, textures, and event hooks."""

    def test_block_defaults(self):
        block = Block(id="mod:b", name="B")
        assert block.max_stack_size == 64
        assert block.block_texture_path is None
        assert block.inventory_texture_path is None
        assert block.recipe is None
        assert block.left_click_event is None
        assert block.right_click_event is None

    def test_block_inventory_texture_fallback(self):
        """inventory_texture_path should fall back to block_texture_path."""
        block = Block(
            id="mod:b",
            name="B",
            block_texture_path="textures/block.png",
        )
        assert block.inventory_texture_path == "textures/block.png"

    def test_block_separate_inventory_texture(self):
        block = Block(
            id="mod:b",
            name="B",
            block_texture_path="textures/block.png",
            inventory_texture_path="textures/item.png",
        )
        assert block.inventory_texture_path == "textures/item.png"

    def test_block_on_left_click(self):
        block = Block(
            id="mod:b",
            name="B",
            left_click_event='System.out.println("left");',
        )
        assert block.on_left_click() == 'System.out.println("left");'

    def test_block_on_right_click(self):
        block = Block(
            id="mod:b",
            name="B",
            right_click_event='System.out.println("right");',
        )
        assert block.on_right_click() == 'System.out.println("right");'

    def test_block_no_events_returns_none(self):
        block = Block(id="mod:b", name="B")
        assert block.on_left_click() is None
        assert block.on_right_click() is None


# ================================================================== #
# Section 11 – RecipeJson                                            #
# ================================================================== #


class TestRecipeJson:
    """Test RecipeJson parsing, validation, and result_id extraction."""

    def test_recipe_from_dict(self):
        recipe = RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["##"],
                "key": {"#": "minecraft:stone"},
                "result": {"id": "mod:item", "count": 1},
            }
        )
        assert recipe.data["type"] == "minecraft:crafting_shaped"

    def test_recipe_from_json_string(self):
        recipe = RecipeJson(
            json.dumps(
                {
                    "type": "minecraft:smelting",
                    "ingredient": "minecraft:iron_ore",
                    "result": "minecraft:iron_ingot",
                }
            )
        )
        assert recipe.data["type"] == "minecraft:smelting"

    def test_recipe_result_id_dict_id(self):
        recipe = RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "result": {"id": "mod:item", "count": 1},
            }
        )
        assert recipe.result_id == "mod:item"

    def test_recipe_result_id_dict_item(self):
        """Pre-1.21 'item' key should still work."""
        recipe = RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "result": {"item": "mod:legacy", "count": 1},
            }
        )
        assert recipe.result_id == "mod:legacy"

    def test_recipe_result_id_string(self):
        recipe = RecipeJson(
            {
                "type": "minecraft:smelting",
                "result": "mod:ingot",
            }
        )
        assert recipe.result_id == "mod:ingot"

    def test_recipe_result_id_none(self):
        recipe = RecipeJson(
            {
                "type": "minecraft:crafting_special_armordye",
            }
        )
        assert recipe.result_id is None

    def test_recipe_missing_type_raises(self):
        with pytest.raises(ValueError, match="type"):
            RecipeJson({"result": "mod:x"})

    def test_recipe_empty_type_raises(self):
        with pytest.raises(ValueError, match="type"):
            RecipeJson({"type": ""})

    def test_recipe_invalid_json_string_raises(self):
        with pytest.raises(json.JSONDecodeError):
            RecipeJson("not valid json {{{}")

    def test_recipe_text_roundtrip(self):
        """RecipeJson text should be valid JSON that round-trips."""
        original = {
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:a", "minecraft:b"],
            "result": {"id": "mod:c", "count": 1},
        }
        recipe = RecipeJson(original)
        roundtripped = json.loads(recipe.text)
        assert roundtripped == original


# ================================================================== #
# Section 12 – ItemGroup / item_group Constants                      #
# ================================================================== #


class TestItemGroup:
    """Test ItemGroup and vanilla constants."""

    def test_vanilla_constants(self):
        assert item_group.BUILDING_BLOCKS == "building_blocks"
        assert item_group.NATURAL == "natural_blocks"
        assert item_group.FUNCTIONAL == "functional_blocks"
        assert item_group.REDSTONE == "redstone_blocks"
        assert item_group.TOOLS == "tools_and_utilities"
        assert item_group.COMBAT == "combat"
        assert item_group.FOOD_AND_DRINK == "food_and_drinks"
        assert item_group.INGREDIENTS == "ingredients"
        assert item_group.SPAWN_EGGS == "spawn_eggs"

    def test_custom_item_group_creation(self):
        grp = ItemGroup(id="my_tab", name="My Tab")
        assert grp.id == "my_tab"
        assert grp.item_id == "my_tab"
        assert grp.name == "My Tab"

    def test_item_group_id_alias(self):
        """Both 'id' and 'item_id' should work."""
        grp1 = ItemGroup(id="test")
        grp2 = ItemGroup(item_id="test")
        assert grp1.id == grp2.id == "test"

    def test_item_group_dual_id_raises(self):
        """Specifying both id and item_id should raise ValueError."""
        with pytest.raises(ValueError):
            ItemGroup(id="a", item_id="b")

    def test_item_group_set_icon(self):
        grp = ItemGroup(id="weapons", name="Weapons")
        dummy_item = Item(id="mod:sword", name="Sword")
        grp.set_icon(dummy_item)
        assert grp.icon is dummy_item
        assert grp.icon_item_id == "mod:sword"

    def test_item_group_equality(self):
        grp1 = ItemGroup(id="same", name="A")
        grp2 = ItemGroup(id="same", name="B")
        assert grp1 == grp2

    def test_item_group_inequality(self):
        grp1 = ItemGroup(id="a")
        grp2 = ItemGroup(id="b")
        assert grp1 != grp2


# ================================================================== #
# Section 13 – Message Helpers                                       #
# ================================================================== #


class TestMessageHelpers:
    """Test send_message and send_action_bar_message Java snippets."""

    def test_send_message(self):
        result = message.send_message("Hello World")
        assert "displayClientMessage" in result
        assert "Hello World" in result
        assert "Component.literal" in result
        assert "false" in result

    def test_send_action_bar_message(self):
        result = message.send_action_bar_message("Action!")
        assert "displayClientMessage" in result
        assert "Action!" in result
        assert "true" in result

    def test_send_message_custom_player_var(self):
        result = message.send_message("Hi", player_var="p")
        assert result.startswith("p.")

    def test_send_message_escapes_quotes(self):
        result = message.send_message('He said "hello"')
        assert '\\"hello\\"' in result
