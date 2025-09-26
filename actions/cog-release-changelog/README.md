# Cocogitto Release and Changelog with Build Tools

A composite GitHub Action that combines version determination using cocogitto, release creation, and optional package building/publishing using custom commands.

## Features

- **Version Management**: Uses cocogitto to determine current, new, and development versions
- **Release Creation**: Automatically creates releases with changelogs
- **Generic Build Tool Integration**: Conditionally run any build tool commands (install, version, build, publish)
- **Flexible Configuration**: All build commands can be customized or disabled via inputs
- **Environment Variables**: Support for custom environment variables
- **Forgejo Integration**: Optional integration with Forgejo API

## Usage

### Basic Usage (Cocogitto only)

```yaml
- name: Release with cocogitto
  uses: ./actions/cog-release-changelog
```

### With UV (Python Package Manager)

```yaml
- name: Release and publish Python package with UV
  uses: ./actions/cog-release-changelog
  with:
    # Install UV
    install_build_tools_command: |
      curl -LsSf https://astral.sh/uv/install.sh | sh
      source $HOME/.cargo/env
      uv python install 3.13

    # UV Commands
    set_version_command: "uv version"
    build_command: "uv build"
    publish_command: "uv publish -v"

    # Environment Variables for UV
    env_vars: |
      UV_PUBLISH_USERNAME=myuser
      UV_PUBLISH_PASSWORD=${{ secrets.PACKAGE_UPLOAD_TOKEN }}
      UV_PUBLISH_URL=https://pypi.org/simple/

    # Forgejo Configuration (optional)
    forgejo_server_url: ${{ github.server_url }}
    forgejo_token: ${{ secrets.FORGEJO_TOKEN }}
```

### With Poetry (Python Package Manager)

```yaml
- name: Release and publish Python package with Poetry
  uses: ./actions/cog-release-changelog
  with:
    # Install Poetry
    install_build_tools_command: |
      curl -sSL https://install.python-poetry.org | python3 -
      export PATH="$HOME/.local/bin:$PATH"

    # Poetry Commands
    set_version_command: "poetry version"
    build_command: "poetry build"
    publish_command: "poetry publish"

    # Environment Variables for Poetry
    env_vars: |
      POETRY_PYPI_TOKEN_PYPI=${{ secrets.PYPI_TOKEN }}
```

### With npm (Node.js Package Manager)

```yaml
- name: Release and publish npm package
  uses: ./actions/cog-release-changelog
  with:
    # Install Node.js dependencies
    install_build_tools_command: "npm ci"

    # npm Commands
    set_version_command: "npm version"
    build_command: "npm run build"
    publish_command: "npm publish"

    # Environment Variables for npm
    env_vars: |
      NPM_TOKEN=${{ secrets.NPM_TOKEN }}
```

### With Cargo (Rust Package Manager)

```yaml
- name: Release and publish Rust crate
  uses: ./actions/cog-release-changelog
  with:
    # Rust is typically pre-installed, but you could install specific tools
    install_build_tools_command: "rustup update stable"

    # Cargo Commands
    build_command: "cargo build --release"
    publish_command: "cargo publish"

    # Environment Variables for Cargo
    env_vars: |
      CARGO_REGISTRY_TOKEN=${{ secrets.CARGO_REGISTRY_TOKEN }}
```

### Using with astral-sh/setup-uv Action

```yaml
# Install UV using the official action first
- name: Install uv and set the python version
  uses: https://github.com/astral-sh/setup-uv@v6
  with:
    python-version: "3.13"
    enable-cache: true
    prune-cache: false

- name: Release and publish Python package
  uses: ./actions/cog-release-changelog
  with:
    # Skip installation since UV is already installed
    set_version_command: "uv version"
    build_command: "uv build"
    publish_command: "uv publish -v"
    env_vars: |
      UV_PUBLISH_USERNAME=finkregh
      UV_PUBLISH_PASSWORD=${{ secrets.PACKAGE_UPLOAD_TOKEN }}
      UV_PUBLISH_URL=${{ github.server_url }}/api/packages/finkregh/pypi
```

## Inputs

| Input                         | Description                                                                        | Required |
| ----------------------------- | ---------------------------------------------------------------------------------- | -------- |
| `install_build_tools_command` | Command to install build tools and dependencies. Leave empty to skip installation. | No       |
| `set_version_command`         | Command to set package version. Leave empty to skip version setting.               | No       |
| `build_command`               | Command to build package. Leave empty to skip building.                            | No       |
| `publish_command`             | Command to publish package. Leave empty to skip publishing.                        | No       |
| `env_vars`                    | Custom environment variables to set, one per line in KEY=VALUE format.             | No       |
| `forgejo_server_url`          | Forgejo server URL for API calls                                                   | No       |
| `forgejo_token`               | Forgejo API token                                                                  | No       |

## Outputs

| Output    | Description                               |
| --------- | ----------------------------------------- |
| `current` | Current version from cocogitto            |
| `new`     | New version from cocogitto auto bump      |
| `new_dev` | New development version with \_dev suffix |

## Environment Variables Format

The `env_vars` input accepts multi-line strings in KEY=VALUE format:

```yaml
env_vars: |
  BUILD_TOKEN=${{ secrets.TOKEN }}
  PUBLISH_URL=https://example.com/registry
  CUSTOM_VAR=value
```

## Build Tool Examples

### UV (Python - Fast Package Manager)

```yaml
install_build_tools_command: "curl -LsSf https://astral.sh/uv/install.sh | sh && source $HOME/.cargo/env"
set_version_command: "uv version"
build_command: "uv build"
publish_command: "uv publish -v"
```

### Poetry (Python - Traditional Package Manager)

```yaml
install_build_tools_command: "curl -sSL https://install.python-poetry.org | python3 -"
set_version_command: "poetry version"
build_command: "poetry build"
publish_command: "poetry publish"
```

### npm (Node.js)

```yaml
install_build_tools_command: "npm ci"
set_version_command: "npm version"
build_command: "npm run build"
publish_command: "npm publish"
```

### Cargo (Rust)

```yaml
install_build_tools_command: "rustup update stable"
build_command: "cargo build --release"
publish_command: "cargo publish"
```

### Maven (Java)

```yaml
install_build_tools_command: "mvn dependency:resolve"
build_command: "mvn package"
publish_command: "mvn deploy"
```

### Gradle (Java/Kotlin)

```yaml
install_build_tools_command: "./gradlew dependencies"
build_command: "./gradlew build"
publish_command: "./gradlew publish"
```

## Advanced Examples

### Multi-step Build Process

```yaml
- name: Complex build and publish
  uses: ./actions/cog-release-changelog
  with:
    install_build_tools_command: |
      # Install multiple tools
      curl -LsSf https://astral.sh/uv/install.sh | sh
      source $HOME/.cargo/env
      npm install -g @semantic-release/changelog

    set_version_command: "uv version"

    build_command: |
      # Multi-step build
      uv build
      npm run build:docs
      tar -czf dist/package.tar.gz dist/

    publish_command: |
      # Publish to multiple registries
      uv publish -v
      npm run publish:docs
```

### Conditional Publishing

```yaml
- name: Build always, publish only on main
  uses: ./actions/cog-release-changelog
  with:
    set_version_command: "uv version"
    build_command: "uv build"
    # Only publish on main branch
    publish_command: ${{ github.ref == 'refs/heads/main' && 'uv publish -v' || 'echo "Skipping publish on non-main branch"' }}
```

## Requirements

- Repository must be configured for cocogitto (cog.toml file)
- For package operations: Project must have appropriate configuration files (pyproject.toml, package.json, Cargo.toml, etc.)
- For Forgejo integration: Valid Forgejo server and token

## License

MIT
