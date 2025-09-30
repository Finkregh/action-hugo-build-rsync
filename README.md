# Forgejo Actions Collection

A collection of reusable Forgejo (and GitHub, untested) Actions for common CI/CD tasks.

## Available Actions

### Hugo Build & Rsync (`actions/hugo-build-rsync`)

Builds a Hugo static site and deploys it via rsync; support for PR previews and branch builds.

[📖 Full Documentation](actions/hugo-build-rsync/README.md)

### Prettier + Markdownlint (`actions/prettier-markdown`)

Formats code with Prettier and lints Markdown files, automatically pushing any fixes.

- Formatting with Prettier (supports JS, TS, JSON, YAML, TOML, etc.)
- Markdown linting and auto-fixing with markdownlint-cli2
- Automatic commit and push of formatting fixes

[📖 Full Documentation](actions/prettier-markdown/README.md)

### Release with Cog (`actions/release-with-cog`)

Creates releases using [cocogitto](https://github.com/cocogitto/cocogitto) with changelog generation and PR comment support.

- Main branch mode: Creates releases, bumps versions, and generates changelogs - all based on [conventional commits](https://www.conventionalcommits.org/)
- Pull request mode: Generates changelogs and posts them as PR comments
- Supports Forgejo release creation
- used in this repository
  - [cogitto config](cog.toml)
  - [workflow](.forgejo/workflows/release-changelog.yml)

[📖 Full Documentation](actions/release-with-cog/README.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Oluf Lorenzen <ol+forgejo-action@oluflorenzen.de>
