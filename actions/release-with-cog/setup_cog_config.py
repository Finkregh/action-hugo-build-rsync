#!/usr/bin/env python3
"""Set changelog configuration values in cog.toml if they don't exist.

This script checks for the presence of 'remote', 'repository', and 'owner' values
in the 'changelog' section of a cog.toml file. If any of these values are missing,
it sets them to the provided values.

Values are passed via environment variables:
- COG_REMOTE
- COG_REPOSITORY
- COG_OWNER
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import tomli_w
    import tomllib
except ImportError:
    print("Error: Required packages not found: tomli tomli-w")  # noqa: T201
    sys.exit(1)


def setup_cog_config(
    cog_toml_path: str = "cog.toml",
    remote: str | None = None,
    repository: str | None = None,
    owner: str | None = None,
) -> bool:
    """Set changelog configuration values in cog.toml if they don't exist.

    Args:
        cog_toml_path (str): Path to the cog.toml file
        remote (str): Remote value to set
        repository (str): Repository value to set
        owner (str): Owner value to set

    Returns:
        bool: True if changes were made, False if values already existed

    """
    if not Path(cog_toml_path).exists():
        msg = f"cog.toml not found at {cog_toml_path}"
        raise FileNotFoundError(msg)

    # Read existing config
    with open(cog_toml_path, "rb") as f:
        config = tomllib.load(f)

    # Ensure changelog section exists
    if "changelog" not in config:
        config["changelog"] = {}

    # Check if values already exist
    changelog = config["changelog"]
    changes_made = False

    # Set values only if they don't exist and are provided
    if "remote" not in changelog and remote is not None:
        changelog["remote"] = remote
        changes_made = True

    if "repository" not in changelog and repository is not None:
        changelog["repository"] = repository
        changes_made = True

    if "owner" not in changelog and owner is not None:
        changelog["owner"] = owner
        changes_made = True

    # Write back to file if changes were made
    if changes_made:
        with open(cog_toml_path, "wb") as f:
            tomli_w.dump(config, f)

    return changes_made


class TestSetupCogConfig(unittest.TestCase):
    """Unit tests for setup_cog_config function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.cog_toml_path = str(Path(self.test_dir) / "cog.toml")

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_values_dont_exist(self) -> None:
        """Test setting values when they don't exist."""
        # Create a cog.toml without the required values
        initial_config = {
            "changelog": {
                "path": "CHANGELOG.md",
                "authors": [],
                "template": "remote",
            },
        }

        with open(self.cog_toml_path, "wb") as f:
            tomli_w.dump(initial_config, f)

        # Run the function
        changes_made = setup_cog_config(
            self.cog_toml_path,
            remote="test-remote",
            repository="test-repo",
            owner="test-owner",
        )

        # Verify changes were made
        assert changes_made  # noqa: S101

        # Verify the values were set
        with open(self.cog_toml_path, "rb") as f:
            updated_config = tomllib.load(f)

        assert updated_config["changelog"]["remote"] == "test-remote"  # noqa: S101
        assert updated_config["changelog"]["repository"] == "test-repo"  # noqa: S101
        assert updated_config["changelog"]["owner"] == "test-owner"  # noqa: S101

        # Verify existing values were preserved
        assert updated_config["changelog"]["path"] == "CHANGELOG.md"  # noqa: S101
        assert updated_config["changelog"]["template"] == "remote"  # noqa: S101

    def test_values_already_exist(self) -> None:
        """Test when values already exist - should not modify them."""
        # Create a cog.toml with existing values
        initial_config = {
            "changelog": {
                "path": "CHANGELOG.md",
                "authors": [],
                "template": "remote",
                "remote": "existing-remote",
                "repository": "existing-repo",
                "owner": "existing-owner",
            },
        }

        with open(self.cog_toml_path, "wb") as f:
            tomli_w.dump(initial_config, f)

        # Run the function
        changes_made = setup_cog_config(
            self.cog_toml_path,
            remote="new-remote",
            repository="new-repo",
            owner="new-owner",
        )

        # Verify no changes were made
        assert not changes_made  # noqa: S101

        # Verify existing values were preserved
        with open(self.cog_toml_path, "rb") as f:
            updated_config = tomllib.load(f)

        assert updated_config["changelog"]["remote"] == "existing-remote"  # noqa: S101
        assert (  # noqa: S101
            updated_config["changelog"]["repository"] == "existing-repo"
        )
        assert updated_config["changelog"]["owner"] == "existing-owner"  # noqa: S101

    def test_values_none_provided(self) -> None:
        """Test when None values are provided - should not modify anything."""
        # Create a cog.toml without the required values
        initial_config = {
            "changelog": {
                "path": "CHANGELOG.md",
                "authors": [],
                "template": "remote",
            },
        }

        with open(self.cog_toml_path, "wb") as f:
            tomli_w.dump(initial_config, f)

        # Run the function with None values
        changes_made = setup_cog_config(
            self.cog_toml_path,
            remote=None,
            repository=None,
            owner=None,
        )

        # Verify no changes were made
        assert not changes_made  # noqa: S101

        # Verify the values were not set
        with open(self.cog_toml_path, "rb") as f:
            updated_config = tomllib.load(f)

        assert "remote" not in updated_config["changelog"]  # noqa: S101
        assert "repository" not in updated_config["changelog"]  # noqa: S101
        assert "owner" not in updated_config["changelog"]  # noqa: S101

        # Verify existing values were preserved
        assert updated_config["changelog"]["path"] == "CHANGELOG.md"  # noqa: S101
        assert updated_config["changelog"]["template"] == "remote"  # noqa: S101


def main() -> None:
    """Run the script or tests."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run unit tests
        unittest.main(argv=sys.argv[1:])
    else:
        # Read values from environment variables
        remote = os.environ.get("COG_REMOTE")
        repository = os.environ.get("COG_REPOSITORY")
        owner = os.environ.get("COG_OWNER")
        print(  # noqa: T201
            f"[DEBUG] COG_REMOTE: {remote}, COG_REPOSITORY: {repository}, COG_OWNER: {owner}",  # noqa: E501
        )

        # Run the actual configuration setup
        changes_made = setup_cog_config(
            remote=remote,
            repository=repository,
            owner=owner,
        )

        if changes_made:
            print(  # noqa: T201
                "✓ Added missing changelog configuration values to cog.toml",
            )
        else:
            print(  # noqa: T201
                "✓ All changelog configuration values already exist in cog.toml",
            )


if __name__ == "__main__":
    main()
