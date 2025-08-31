# Prettier and Markdownlint Action

A GitHub composite action that runs Prettier and Markdownlint.

## Features

- Runs Prettier
- Runs Markdownlint
- Automatically commits and pushes linting fixes (on PRs or non-default branches)
  - Configurable commit message, author, and user details

## Usage

```yaml
name: Lint and Format
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Run Prettier and Markdownlint
        uses: ./action-prettier-markdownlint
        with:
          prettier_plugins: "prettier-plugin-toml prettier-plugin-sh prettier-plugin-merge"
          commit_message: "style: automated linting fixes"
          commit_user_name: "Linting Bot"
          commit_user_email: "linting-bot@example.com"
          commit_author: "Linting Bot <linting-bot@example.com>"
```

## Inputs

| Input                 | Description                                                 | Required | Default                                                         |
| --------------------- | ----------------------------------------------------------- | -------- | --------------------------------------------------------------- |
| `prettier_plugins`    | Space-separated list of prettier plugins to install and use | No       | `prettier-plugin-toml prettier-plugin-sh prettier-plugin-merge` |
| `commit_message`      | Commit message for linting fixes                            | No       | `style: changes from ci`                                        |
| `commit_user_name`    | Git user name for commits                                   | No       | _(uses stefanzweifel/git-auto-commit-action default)_           |
| `commit_user_email`   | Git user email for commits                                  | No       | _(uses stefanzweifel/git-auto-commit-action default)_           |
| `commit_author`       | Git commit author                                           | No       | _(uses stefanzweifel/git-auto-commit-action default)_           |
| `prettier_options`    | Additional options to pass to prettier                      | No       | `--write .`                                                     |
| `markdownlint_globs`  | Glob patterns for markdownlint                              | No       | `**/*.md`                                                       |
| `allow_other_plugins` | Allow other prettier plugins                                | No       | `true`                                                          |
| `skip_commit`         | Skip committing and pushing changes                         | No       | `false`                                                         |

## Behavior

1. **Branch Detection**: Automatically detects the current branch name
2. **Checkout**: Checks out the repository with full history
3. **Plugin Installation**: Installs prettier and specified plugins
4. **Prettier Formatting**: Runs prettier with the specified options and plugins
5. **Markdownlint (Non-blocking)**: Runs markdownlint with fix mode enabled, continues on error
6. **Git Status**: Shows current git status and diff
7. **Auto-commit**: Commits and pushes changes only on:
   - Pull requests, OR
   - Non-default branches
8. **Markdownlint (Blocking)**: Runs markdownlint again in blocking mode to ensure all issues are resolved

## Example with Custom Settings

```yaml
- name: Custom Lint and Format
  uses: ./action-prettier-markdownlint
  with:
    prettier_plugins: "prettier-plugin-yaml prettier-plugin-json"
    commit_message: "fix: automated code formatting"
    commit_user_name: "Format Bot"
    commit_user_email: "format-bot@company.com"
    commit_author: "Format Bot <format-bot@company.com>"
    prettier_options: "--write --tab-width 2 ."
    markdownlint_globs: "docs/**/*.md README.md"
```

## Example with Skip Commit (Testing/CI)

```yaml
- name: Lint and Format (No Commit)
  uses: ./action-prettier-markdownlint
  with:
    prettier_plugins: "prettier-plugin-toml prettier-plugin-sh"
    prettier_options: "--write ."
    markdownlint_globs: "**/*.md"
    skip_commit: "true" # Only format files, don't commit changes
```

This is useful for:

- Testing the action without making commits
- CI workflows that only want to check formatting
- Local development workflows where you want to format but handle commits manually
