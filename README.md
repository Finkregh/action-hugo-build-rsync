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

### Cocogitto Release and Changelog (`actions/cog-release-changelog`)

Combines version determination using cocogitto, release creation, and optional package building/publishing using custom commands.

- Version management with cocogitto (current, new, and development versions)
- Automatic release creation with changelogs
- Generic build tool integration (supports UV, Poetry, npm, Cargo, Maven, Gradle, etc.)
- Flexible configuration with customizable build commands
- Environment variables support
- Optional Forgejo integration

[📖 Full Documentation](actions/cog-release-changelog/README.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Oluf Lorenzen <ol+forgejo-action@oluflorenzen.de>
