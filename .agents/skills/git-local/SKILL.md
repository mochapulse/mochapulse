---
name: git-local
description: Use Git and GitHub tools (commits, clones, pull requests, status checks, profile switching) on this local WSL machine. Covers multi-account setup for UNAL (~/GIT/UNAL) and Mocha (~/GIT/Mocha) environments.
---

Manage multi-account Git and GitHub CLI configurations seamlessly between academic (UNAL) and personal (Mocha) environments using local directory context routing.

## Directory and Profile Mapping

- **UNAL Profile**: Located in `~/GIT/UNAL/`. Uses identity `dramirezbe` (`dramirezbe@unal.edu.co`) and custom SSH host `github.com-unal`.
- **Mocha Profile**: Located in `~/GIT/Mocha/`. Uses identity `mochapulse` (`mochapulse@gmail.com`) and custom SSH host `github.com-mocha`.

## Core Workflows

### 1. Cloning Repositories

Because conditional configurations include standard-to-custom URL rewriting, always change directories into the destination profile folder **before** executing a clone.

```bash
# To clone a UNAL repository
cd ~/GIT/UNAL
git clone git@github.com:owner/repo.git

# To clone a Mocha repository
cd ~/GIT/Mocha
git clone git@github.com:owner/repo.git
```

### 2. Working with GitHub CLI (gh) for Pull Requests

The GitHub CLI handles API operations and requires matching authentication tokens alongside your directory's SSH key profiles.

#### Check Active CLI User

Before pushing changes or submitting PRs, verify which account the GitHub CLI is actively using:

```bash
gh auth status
```

#### Switch CLI Accounts

Manually toggle the CLI identity context if it does not match your active working folder:

```bash
# When working within ~/GIT/UNAL/
gh auth switch --user dramirezbe

# When working within ~/GIT/Mocha/
gh auth switch --user mochapulse
```

#### Create a Pull Request

Once the context matches, use the standard `gh` commands. Git dynamically replaces host routing protocols via underlying config hooks:

```bash
gh pr create --title "Your PR Title" --body "Your PR description"
```

## Troubleshooting and Verification

If commits show the wrong email or SSH handshakes fail, run these inside the repository directory to verify contextual variable resolution:

```bash
# Verify active user email matches the folder rule
git config user.email

# Verify URL rewrite rules are firing locally
git config --get-regexp url
```
