# Release with Cog Action

Release using Cog (Conventional Commits tool), and output the version before run, the version after run, and the changelog.

This action is a fork from [PurpleBooth/common-pipelines](https://codeberg.org/PurpleBooth/common-pipelines/src/branch/main/actions/release-with-cog) under CC0 1.0 Universal License.

## Usage

```yaml
- name: Release with Cog
  uses: ./actions/release-with-cog
  with:
    working-directory: "."
    dry-run: "false"
    dry-run-on-non-default-branch: "true"
    cog_bump_args: ""
    cog_changelog_args: "--remote ${{ env.GITHUB_SERVER_URL##*/ }} --owner ${{ env.GITHUB_REPOSITORY_OWNER }} --repo ${{ env.GITHUB_REPOSITORY##*/ }}"
    create-forgejo-release: "true"
  id: release

- name: Use release outputs
  run: |
    echo "Previous version: ${{ steps.release.outputs.previous_version }}"
    echo "Current version: ${{ steps.release.outputs.current_version }}"
    echo "Release URL: ${{ steps.release.outputs.forgejo_release_url }}"
```

## Inputs

| Input                           | Description                                                               | Required | Default                                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `working-directory`             | The working dir to run in                                                 | No       | `"."`                                                                                                                        |
| `dry-run`                       | If true, no git tag or commit will be created when on main branch         | No       | `"false"`                                                                                                                    |
| `dry-run-on-non-default-branch` | If true, no git tag or commit will be created when on e.g. feature branch | No       | `"true"`                                                                                                                     |
| `cog_bump_args`                 | Additional arguments to pass to `cog bump`, e.g. `--major` or `--minor`   | No       | `""`                                                                                                                         |
| `cog_changelog_args`            | Additional arguments to pass to `cog changelog`, e.g. `--unreleased`      | No       | `"--remote ${{ env.GITHUB_SERVER_URL }} --owner ${{ env.GITHUB_REPOSITORY_OWNER }} --repo ${{ env.GITHUB_REPOSITORY##*/ }}"` |
| `create-forgejo-release`        | If true, create a Forgejo release for the new tag                         | No       | `"true"`                                                                                                                     |

## Outputs

| Output                   | Description                                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------------------------- |
| `current_version`        | The version after the bump                                                                              |
| `previous_version`       | The version prior to bump                                                                               |
| `changelog`              | Changelog since last release in markdown                                                                |
| `forgejo_release_url`    | URL of the created Forgejo release (e.g., `https://forgejo.example.com/owner/repo/releases/tag/v1.2.3`) |
| `forgejo_release_output` | Output from the Forgejo API when creating the release (JSON format)                                     |

## License

CC0 1.0 Universal - See [LICENSE](https://codeberg.org/PurpleBooth/common-pipelines/src/branch/main/LICENSE)
