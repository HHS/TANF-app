# Pre-commit Setup
To support a consistently styled codebase, we use pre-commit. Follow the instructions below or go to https://pre-commit.com/#installation to install and configure pre-commit. All commands should be ran from the root of the repository.

```bash
pip install pre-commit
pre-commit install
```
The last command instructs pre-commit to execute each time you run a `git commit ...`.

# Git Blame Ignore Revs
When the codebase was reformatted it changed the git blame. To ensure a consistent blame history you must run the following command from the root of the repo.
`git config blame.ignoreRevsFile .git-blame-ignore-revs`

# Install Black & Isort
- Install Black 23.10.1 (`pip install black==23.10.1`)
- Install Isort 5.13.2 (`pip install isort==5.13.2`)
