# Development Guide

Simply [fork the repository](#1-forking-the-repository) and make a [pull requst](#2-making-a-pull-request-pr) when you're done. You are free to add README translations to other languages too.

## 1. Forking the repository

Fork this Github repo and clone your fork locally. Then make changes in a local branch to the fork.

See [creating a pull request from a fork](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) for more information.

To fork this repository simply [click here](https://github.com/KK-mp4/portal-location-parser/fork).

```bash
# 1. Fork via GitHub UI
# 2. Clone your fork locally (replace your-username)
git clone git@github.com:your-username/portal-location-parser.git
cd portal-location-parser

# Add upstream remote (original repo)
git remote add upstream git@github.com:KK-mp4/portal-location-parser.git
git fetch upstream
```

## 2. Making a pull request (PR)

### 2.1. PR checklist

A quick list of things to keep in mind as you're making changes:
- As you make changes
  - Make your changes in a forked repo (instead of making a branch on the main repo)
  - [Sign your commits](#23-signing-off-commits) as you go
  - Rebase from master instead of using `git pull` on your PR branch
- When you make the PR
  - Make a PR from the forked repo you made
  - Ensure the title of the PR matches [semantic release conventions](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13) (e.g. start with `feat:` or `fix:` or `ci:` or `chore:` or `docs:`)
  - Ensure you leave a release note for any user facing changes in the PR
  - Try to keep PRs smaller. This makes them easier to review
  - Assign @KK-mp4 as reviewer

### 2.2. Good practices to keep in mind

- Fill in the description based on the default portal-location-parser configured when you first open the PR
  - What this PR does/why it's need it
  - Which issue(s) this PR fixes
  - Does this PR introduce a user-facing change
- Add `WIP:` to PR name if more work needs to be done prior to review

### 2.3. Signing off commits

> [!WARNING]
> Using the default integrations with IDEs like VSCode or IntelliJ will not sign commits.

Use [git signoffs](https://docs.github.com/en/github/authenticating-to-github/managing-commit-signature-verification) to sign your commits.

Then, you can sign off commits with the `-s` flag:

```bash
git commit -s -m "My first commit"
```

### 2.4. Incorporating upstream changes from master

Use `git rebase [master]` instead of `git merge` : `git pull -r`.

Note that this means if you are midway through working through a PR and rebase, you'll have to force push:

```bash
git push --force-with-lease origin [branch name]
```

Keep your fork up to date and rebase your branch:

```bash
# Ensure local master is up-to-date with upstream
git checkout master
git fetch upstream
git rebase upstream/master

# Switch back to your branch and rebase from updated master
git checkout my-feature-branch
git rebase master

# Resolve conflicts if any, then push
git push --force-with-lease origin my-feature-branch
```
