#!/bin/bash
# Version management script for fabricpy

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_FILE="$SCRIPT_DIR/fabricpy/__version__.py"

# Function to get current version
get_version() {
    if [ -f "$VERSION_FILE" ]; then
        grep -o '__version__ = "[^"]*"' "$VERSION_FILE" | cut -d'"' -f2
    else
        echo "0.0.0"
    fi
}

# Function to set version
set_version() {
    local new_version=$1
    if [ -z "$new_version" ]; then
        echo "Error: No version specified"
        exit 1
    fi
    
    # Validate version format (basic semver check)
    if ! echo "$new_version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$'; then
        echo "Error: Invalid version format. Use semver format (e.g., 1.0.0)"
        exit 1
    fi
    
    echo "\"\"\"Version information for fabricpy.\"\"\"" > "$VERSION_FILE"
    echo "" >> "$VERSION_FILE"
    echo "__version__ = \"$new_version\"" >> "$VERSION_FILE"
    
    echo "Version updated to $new_version"
}

# Function to bump version
bump_version() {
    local bump_type=$1
    local current_version=$(get_version)
    
    if [ -z "$current_version" ] || [ "$current_version" = "0.0.0" ]; then
        echo "Error: Cannot determine current version"
        exit 1
    fi
    
    # Split version into parts
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    major=${VERSION_PARTS[0]}
    minor=${VERSION_PARTS[1]}
    patch=${VERSION_PARTS[2]}
    
    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Error: Invalid bump type. Use: major, minor, or patch"
            exit 1
            ;;
    esac
    
    new_version="$major.$minor.$patch"
    set_version "$new_version"
}

# Function to create release tag
create_tag() {
    local version=$(get_version)
    local tag_name="v$version"
    
    # Check if tag already exists
    if git tag -l | grep -q "^$tag_name$"; then
        echo "Error: Tag $tag_name already exists"
        exit 1
    fi
    
    # Create and push tag
    git tag -a "$tag_name" -m "Release version $version"
    echo "Created tag: $tag_name"
    echo "To push the tag, run: git push origin $tag_name"
}

# Main script logic
case "${1:-}" in
    get)
        get_version
        ;;
    set)
        set_version "$2"
        ;;
    bump)
        bump_version "$2"
        ;;
    tag)
        create_tag
        ;;
    release)
        bump_type="${2:-patch}"
        echo "Current version: $(get_version)"
        bump_version "$bump_type"
        echo "New version: $(get_version)"
        create_tag
        ;;
    *)
        echo "Usage: $0 {get|set <version>|bump <major|minor|patch>|tag|release [major|minor|patch]}"
        echo ""
        echo "Commands:"
        echo "  get                    - Show current version"
        echo "  set <version>          - Set specific version"
        echo "  bump <type>            - Bump version (major, minor, or patch)"
        echo "  tag                    - Create git tag for current version"
        echo "  release [type]         - Bump version and create tag (default: patch)"
        echo ""
        echo "Current version: $(get_version)"
        exit 1
        ;;
esac
