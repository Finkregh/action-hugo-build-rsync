# action-hugo-build-rsync

Forgejo-Action to build a hugo site and rsync it somewhere.

Jobs:

- install required packages
  - curl, bash, openssh-client, rsync, tar, zstd
- restore cached `resources` and `hugo_cachedir`
- set variables depending on if it started from a PR or not
- run `hugo build`
- save/update caches for `resources` and `hugo_cachedir`
- rsync `public/*` somewhere
- if started from PR: add a comment to the PR pointing to where the build can be accessed (if the comment does not yet exist)

## Requirements

- alpine based image, e.g. `hugomods/hugo:exts-0.148.1`
- variable `SSH_KNOWN_HOSTS` (if using below example)
- secret `SSH_PRIVATE_KEY` (if using below example)

## PR builds

PR builds behave differently from non-pr builds and use the `pr_` prefixed variables.

The domain/folders/etc. are combined from `pr_domain`, `pr_subdomain` and `-pr-{TheCurrentPRsID}`.

Example:

`pr_domain: development.example.com` and `pr_subdomain: prod-test` in a PR with the ID `1312` will run with [hugoBaseurl](gohugo.io/methods/site/baseurl/) = <http://prod-test-pr-1312.development.example.com> and rsync the files in `public/` to the directory `prod-test-pr-1312.development.example.com/`.

## Server configuration

### rsync/ssh

This can be combined with [rrsync](https://man.archlinux.org/man/rrsync.1) to limit where the SSH key can write into via rsync.

If you add this to your `~/.ssh/authorized_keys` the specified key can only write into `/srv`; [`-munge`](https://man.archlinux.org/man/rsync.1#munge-links) is a security feature that breaks symlinks, that you can not access e.g. files outside of `/srv`.

```
command="/usr/bin/rrsync -munge /srv",no-agent-forwarding,no-port-forwarding,no-pty,no-user-rc,no-X11-forwarding ssh-something YOUR KEY HERE
```

### Webserver

I use [caddy](https://caddyserver.com/) with this configuration for the PR builds:

```text
*.development.example.com:80 {
 root /srv
 rewrite /{host}{uri}
 @forbidden {
  path /.*
 }
 respond @forbidden 404
 file_server
}
```

It listens only on HTTP (tcp/80), as I do not want to have ACME certificates for every PR build (or setup wildcard certs).
Any subdomain under `.development.example.com` can be used, files are expected in `/srv/somesubdomain.development.example.com/` e.g. `/srv/myblog-pr-1.development.example.com`.

## Example usage

The values that have to be set are not commented, the commented ones show their default values.

```yaml
name: publish

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches:
      - main
  # this will only work with the main branch, as it checks if it has been started by a PR or not
  workflow_dispatch:

jobs:
  build-and-publish:
    runs-on: docker
    container:
      # alpine based image wiht hugo installed
      image: "hugomods/hugo:exts-0.148.1"
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 1
      - uses: https://git.h.oluflorenzen.de/finkregh/action-hugo-build-rsync@main # or pin to version, e.g. @0.0.1
        with:
          #hugo_cachedir: "/tmp/hugo_cache"
          #hugo_args: "--minify"
          main_domain: productiondomain.example.com
          # these will be combined to `prod-test-pr-${number}.testdomain.example.com`
          pr_domain: development.example.com
          pr_subdomain: prod-test
          # rsync to the users' $HOME
          main_rsync_destination_dir: ""
          #pr_rsync_destination_basedir:
          main_rsync_server: prod-rsync-host.example.com
          pr_rsync_server: development-rsync-host.example.com
          main_rsync_user: hopefully-not-root
          pr_rsync_user: caddy
          #main_rsync_rsh: "ssh"
          #pr_rsync_rsh: "ssh"
          #main_rsync_args: "-atv --progress --delete"
          #pr_rsync_args: "-atv --progress --delete"
          ssh_known_hosts: ${{ vars.SSH_KNOWN_HOSTS }}
          ssh_secret_key: ${{ secrets.SSH_PRIVATE_KEY }}
          #forgejo_curl_source: "https://git.h.oluflorenzen.de/mirrors/forgejo-curl/raw/branch/main/forgejo-curl.sh"
```
