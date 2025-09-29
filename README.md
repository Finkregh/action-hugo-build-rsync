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

### Cocogitto PR Changelog (`actions/cog-pr-changelog`)

Generates a changelog using cocogitto and posts it as a comment to Pull Requests, with automatic comment updating.

- Changelog generation from conventional commits using cocogitto
- Automatic PR comment posting and updating
- Customizable comment header and footer
- Configurable changelog generation options
- Works with Forgejo and GitHub
- Prevents duplicate comments by updating existing ones

[📖 Full Documentation](actions/cog-pr-changelog/README.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Oluf Lorenzen <ol+forgejo-action@oluflorenzen.de>
