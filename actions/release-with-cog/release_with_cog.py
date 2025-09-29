#!/usr/bin/env python3
"""GitHub Action script to replace bash logic for release-with-cog action.

This script handles version management, changelog generation, and Forgejo release
creation using Python libraries instead of complex bash scripting.
"""

# ruff: noqa: S603, S607

import json
import os
import subprocess
import sys

try:
    import tomllib
    from github_action_toolkit import (
        debug,
        end_group,
        error,
        get_env,
        get_user_input,
        info,
        notice,
        set_output,
        start_group,
        warning,
    )
    from pyforgejo import PyforgejoApi
except ImportError as e:
    print(f"Error: Required packages not found: {e}")  # noqa: T201
    sys.exit(1)

# Import the existing setup_cog_config function
from setup_cog_config import setup_cog_config


class ReleaseWithCogError(Exception):
    """Custom exception for release-with-cog errors."""


def get_action_inputs() -> dict[str, str]:
    """Get all action inputs with defaults."""
    inputs = {
        "working-directory": get_user_input("working-directory") or ".",
        "dry-run": get_user_input("dry-run") or "false",
        "dry-run-on-non-default-branch": get_user_input("dry-run-on-non-default-branch")
        or "true",
        "cog_bump_args": get_user_input("cog_bump_args") or "",
        "cog_changelog_args": get_user_input("cog_changelog_args") or "",
        "remote": get_user_input("remote") or "",
        "owner": get_user_input("owner") or "",
        "repo": get_user_input("repo") or "",
        "create-forgejo-release": get_user_input("create-forgejo-release") or "true",
        "update_cog_toml": get_user_input("update_cog_toml") or "true",
    }

    debug(f"Action inputs: {inputs}")
    return inputs


def extract_domain_from_server_url() -> str:
    """Extract domain from GITHUB_SERVER_URL environment variable."""
    server_url = get_env("GITHUB_SERVER_URL") or ""
    if "://" in server_url:
        return server_url.split("://", 1)[1]
    return server_url


def extract_repo_from_repository() -> str:
    """Extract repository name from GITHUB_REPOSITORY environment variable."""
    repository = get_env("GITHUB_REPOSITORY") or ""
    if "/" in repository:
        return repository.split("/", 1)[1]
    return repository


def set_default_values(inputs: dict[str, str]) -> tuple[str, str, str]:
    """Set default values for remote, owner, and repo if not provided."""
    start_group("Set default values for remote, owner, repo")

    # Set remote (extract domain from GITHUB_SERVER_URL)
    remote = inputs["remote"]
    if not remote:
        remote = extract_domain_from_server_url()

    # Set owner
    owner = inputs["owner"]
    if not owner:
        owner = get_env("GITHUB_REPOSITORY_OWNER") or ""

    # Set repo (extract repo name from GITHUB_REPOSITORY)
    repo = inputs["repo"]
    if not repo:
        repo = extract_repo_from_repository()

    notice(f"Set defaults - remote: {remote}, owner: {owner}, repo: {repo}")

    # Set outputs for other steps to use
    set_output("remote", remote)
    set_output("owner", owner)
    set_output("repo", repo)

    end_group()
    return remote, owner, repo


def determine_dry_run_mode(inputs: dict[str, str]) -> bool:
    """Determine if dry-run mode should be enabled."""
    start_group("Determine dry-run mode")

    dry_run = False

    # Check explicit dry-run flag
    if inputs["dry-run"].lower() == "true":
        head_ref = get_env("GITHUB_HEAD_REF") or ""
        base_ref = get_env("GITHUB_BASE_REF") or ""
        if head_ref == base_ref:
            dry_run = True
            info("Dry-run enabled: explicit dry-run flag set and on default branch")

    # Check dry-run-on-non-default-branch
    elif inputs["dry-run-on-non-default-branch"].lower() == "true":
        head_ref = get_env("GITHUB_HEAD_REF") or ""
        base_ref = get_env("GITHUB_BASE_REF") or ""
        if head_ref != base_ref:
            dry_run = True
            info("Dry-run enabled: on non-default branch")

    if not dry_run:
        info("Dry-run disabled")

    set_output("dry_run_arg", "--dry-run" if dry_run else "")
    notice(f"Dry-run mode: {'enabled' if dry_run else 'disabled'}")

    end_group()
    return dry_run


def setup_cog_configuration(
    inputs: dict[str, str],
    remote: str,
    owner: str,
    repo: str,
) -> None:
    """Set up cog configuration if requested."""
    if inputs["update_cog_toml"].lower() != "true":
        return

    start_group("Verify/set cog config values")

    try:
        # Set environment variables for setup_cog_config
        os.environ["COG_REMOTE"] = remote
        os.environ["COG_OWNER"] = owner
        os.environ["COG_REPOSITORY"] = repo

        # Use the existing setup_cog_config function
        changes_made = setup_cog_config(
            remote=remote,
            repository=repo,
            owner=owner,
        )

        if changes_made:
            info("✓ Added missing changelog configuration values to cog.toml")

            # Add and commit changes
            subprocess.run(["git", "add", "cog.toml"], check=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                check=False,
                capture_output=True,
            )
            if result.returncode != 0:  # There are changes
                try:
                    subprocess.run(
                        [
                            "git",
                            "commit",
                            "-m",
                            "chore: update cog.toml with remote/owner/repo [skip ci]",
                        ],
                        check=True,
                    )
                    subprocess.run(["git", "push", "origin", "HEAD"], check=True)
                    info("Committed and pushed cog.toml changes")
                except subprocess.CalledProcessError:
                    # Commit might fail if there are no changes, that's ok
                    info("No changes to commit or push failed")
            else:
                info("No changes to cog.toml")
        else:
            info("✓ All changelog configuration values already exist in cog.toml")

    except Exception as e:
        error(f"Failed to setup cog configuration: {e}")
        msg = f"Cog configuration setup failed: {e}"
        raise ReleaseWithCogError(msg) from e

    end_group()


def run_cog_command(args: list, working_dir: str = ".") -> str:
    """Run a cog command and return its output."""
    try:
        result = subprocess.run(
            ["cog", *args],
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error(f"Cog command failed: cog {' '.join(args)}")
        error(f"Error: {e.stderr}")
        msg = f"Cog command failed: {e}"
        raise ReleaseWithCogError(msg) from e


def get_cog_version(working_dir: str) -> str:
    """Get current version from cog."""
    start_group("Determine previous version")

    try:
        version = run_cog_command(["get-version"], working_dir)
        info(f"Current version: {version}")
        end_group()
        return version  # noqa: TRY300
    except ReleaseWithCogError:
        end_group()
        return ""


def bump_version(inputs: dict[str, str], working_dir: str, *, dry_run: bool) -> bool:
    """Bump version using cog."""
    start_group("Semver release")

    try:
        args = ["bump"]

        # Add user-specified bump arguments
        if inputs["cog_bump_args"].strip():
            args.extend(inputs["cog_bump_args"].strip().split())

        # Add dry-run flag if needed
        if dry_run:
            args.append("--dry-run")

        # Add standard flags
        args.extend(["--auto", "--skip-ci"])

        info(f"Running: cog {' '.join(args)}")

        # Run the command, but don't fail
        result = subprocess.run(
            ["cog", *args],
            check=False,
            cwd=working_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            info("Version bump successful")
            if result.stdout:
                info(f"Output: {result.stdout}")
        else:
            warning(f"Version bump returned non-zero exit code: {result.returncode}")
            if result.stderr:
                warning(f"Error output: {result.stderr}")

        # Show git status and diff for debugging
        try:
            status_result = subprocess.run(
                ["git", "status"],
                check=False,
                cwd=working_dir,
                capture_output=True,
                text=True,
            )
            if status_result.stdout:
                info(f"Git status:\n{status_result.stdout}")

            diff_result = subprocess.run(
                ["git", "diff"],
                check=False,
                cwd=working_dir,
                capture_output=True,
                text=True,
            )
            if diff_result.stdout:
                info(f"Git diff:\n{diff_result.stdout}")
        except subprocess.CalledProcessError:
            pass  # Git commands might fail, that's ok

        end_group()
        return result.returncode == 0  # noqa: TRY300

    except Exception as e:  # noqa: BLE001
        warning(f"Version bump failed with exception: {e}")
        end_group()
        return False


def get_tag_prefix() -> str:
    """Get tag prefix from cog.toml."""
    try:
        with open("cog.toml", "rb") as f:
            config = tomllib.load(f)
        return config.get("tag_prefix", "")
    except Exception:  # noqa: BLE001
        info("No tag_prefix found in cog.toml, using empty prefix")
        return ""


def generate_changelog(
    inputs: dict[str, str],
    remote: str,
    owner: str,
    repo: str,
    version: str,
) -> str:
    """Generate changelog using cog."""
    start_group("Generate changelog")

    try:
        args = ["changelog"]

        # Add user-specified changelog arguments
        if inputs["cog_changelog_args"].strip():
            args.extend(inputs["cog_changelog_args"].strip().split())

        # Add remote, owner, repo if available
        if remote and owner and repo:
            args.extend(["--remote", remote, "--owner", owner, "--repository", repo])

        # Add --at flag with tag prefix and version
        if version:
            tag_prefix = get_tag_prefix()
            full_tag = f"{tag_prefix}{version}"
            args.extend(["--at", full_tag])

        info(f"Generating changelog with: cog {' '.join(args)}")

        changelog = run_cog_command(args)
        info("Changelog generated successfully")

        end_group()

    except ReleaseWithCogError as e:
        error(f"Failed to generate changelog: {e}")
        end_group()
        return ""

    return changelog


def create_forgejo_release(
    version: str,
    changelog: str,
    owner: str,
    repo: str,
) -> str | None:
    """Create a Forgejo release using pyforgejo."""
    if not version:
        info("No version available, skipping Forgejo release creation")
        return None

    start_group("Create Forgejo release")

    try:
        # Get Forgejo token and server URL
        token = get_env("FORGEJO_TOKEN")
        server_url = get_env("FORGEJO_SERVER_URL") or get_env("GITHUB_SERVER_URL")

        if not token:
            error("FORGEJO_TOKEN environment variable not set")
            end_group()
            return None

        if not server_url:
            error(
                "FORGEJO_SERVER_URL or GITHUB_SERVER_URL environment variable not set",
            )
            end_group()
            return None

        # Ensure server URL has protocol
        if not server_url.startswith(("http://", "https://")):
            server_url = f"https://{server_url}"

        info(f"Creating Forgejo release for {owner}/{repo} version {version}")

        # Create pyforgejo client
        client = PyforgejoApi(base_url=server_url, api_key=token)

        # Create release
        response = client.repository.repo_create_release(
            owner=owner,
            repo=repo,
            tag_name=version,
            name=version,
            body=changelog,
        )

        # Convert Release object to JSON string for output
        release_url = getattr(
            response,
            "html_url",
            f"{server_url}/{owner}/{repo}/releases/tag/{version}",
        )
        info(f"Forgejo release created successfully: {release_url}")

        # Create a simple dict representation for JSON output
        release_dict = {
            "tag_name": version,
            "name": version,
            "body": changelog,
            "html_url": release_url,
            "id": getattr(response, "id", None),
        }

        end_group()
        return json.dumps(release_dict)

    except Exception as e:  # noqa: BLE001
        error(f"Failed to create Forgejo release: {e}")
        end_group()
        return None


def main() -> None:
    """Orchestrate the release process."""
    try:
        info("Starting release-with-cog Python implementation")

        # Get action inputs
        inputs = get_action_inputs()

        # Set default values
        remote, owner, repo = set_default_values(inputs=inputs)

        # Determine dry-run mode
        dry_run = determine_dry_run_mode(inputs=inputs)

        # Setup cog configuration
        setup_cog_configuration(inputs=inputs, remote=remote, owner=owner, repo=repo)

        # Get previous version
        working_dir = inputs["working-directory"]
        previous_version = get_cog_version(working_dir=working_dir)
        set_output(name="previous_version", value=previous_version)

        # Bump version
        bump_version(
            inputs=inputs,
            dry_run=dry_run,
            working_dir=working_dir,
        )

        # Get current version (after bump)
        current_version = get_cog_version(working_dir)
        set_output("current_version", current_version)

        # Generate changelog
        changelog = generate_changelog(
            inputs=inputs,
            remote=remote,
            owner=owner,
            repo=repo,
            version=current_version,
        )
        set_output(name="changelog", value=changelog)

        # Create Forgejo release if requested and version is available
        forgejo_release_output = None
        if inputs["create-forgejo-release"].lower() == "true" and current_version:
            release_response = create_forgejo_release(
                version=current_version,
                changelog=changelog,
                owner=owner,
                repo=repo,
            )
            if release_response:
                forgejo_release_output = json.dumps(release_response)
                set_output("forgejo_release_output", forgejo_release_output)

        info("Release process completed successfully")

    except ReleaseWithCogError as e:
        error(f"Release process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
