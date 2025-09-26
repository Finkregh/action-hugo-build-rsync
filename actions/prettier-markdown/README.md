# action-prettier-markdown

Forgejo-Action to format code with Prettier and lint Markdown files with Markdownlint, then automatically commit any fixes.

## Jobs

- Extract the current branch name for proper checkout
- Checkout the repository with full history
- Install Prettier and plugins
- Run Prettier
- Run Markdownlint (non-blocking first pass)
- Commit and push any formatting/linting fixes automatically
- Run Markdownlint again in blocking mode to show issues still present in the pipeline state

## Requirements

- Repository with write access for the action to commit changes
- Compatible with any runner that supports composite actions

## Inputs

| Input              | Description                                             | Required | Default                                                         |
| ------------------ | ------------------------------------------------------- | -------- | --------------------------------------------------------------- |
| `prettier_plugins` | Additional prettier plugins to install, space-separated | No       | `prettier-plugin-toml prettier-plugin-sh prettier-plugin-merge` |

## Example usage

```yaml
name: Format and Lint

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches:

jobs:
  format-and-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: https://git.h.oluflorenzen.de/finkregh/action-hugo-build-rsync/actions/prettier-markdown@v1
        #with:
        #  prettier_plugins: "prettier-plugin-toml prettier-plugin-sh prettier-plugin-merge"
```

## Configuration

The action uses default configurations but can be customized by:

- Prettier: <https://prettier.io/docs/options>
- Markdownlint: <https://github.com/DavidAnson/markdownlint-cli2>

## Notes

- The action uses a development version of prettier_action to work around plugin loading issues
- Commits are made with the user "ci-linting" to distinguish automated changes
- The action continues on error during the first Markdownlint pass to allow fixes to be committed
- A second, blocking Markdownlint run ensures the repository meets all linting standards
