# Migration from Poetry to uv - Complete Instructions

This file contains the complete migration plan from Poetry to uv for the linkml-runtime project.

## Step 1: Update main repo clone

```bash
cd /Users/ck/linkml/linkml-runtime
git checkout main
git pull origin main
git checkout migrate-to-uv
git rebase main
```

If the rebase has conflicts, resolve them manually.

## Step 2: Files to copy from fork to main repo

Copy these files from `/Users/ck/linkml/forks/linkml-runtime/` to `/Users/ck/linkml/linkml-runtime/`:

### Files to copy (overwrite):
1. .github/workflows/main.yaml
2. .github/workflows/check-dependencies.yaml
3. .github/workflows/test-upstream.yaml
4. .github/workflows/pypi-publish.yaml
5. .github/dependabot.yml
6. pyproject.toml
7. Makefile
8. CONTRIBUTING.md
9. uv.lock

### Files to delete in main repo:
1. poetry.lock (if it exists)
2. tox.ini (if it exists)

## Step 3: Copy commands

```bash
# Copy the updated files
cp /Users/ck/linkml/forks/linkml-runtime/.github/workflows/main.yaml /Users/ck/linkml/linkml-runtime/.github/workflows/
cp /Users/ck/linkml/forks/linkml-runtime/.github/workflows/check-dependencies.yaml /Users/ck/linkml/linkml-runtime/.github/workflows/
cp /Users/ck/linkml/forks/linkml-runtime/.github/workflows/test-upstream.yaml /Users/ck/linkml/linkml-runtime/.github/workflows/
cp /Users/ck/linkml/forks/linkml-runtime/.github/workflows/pypi-publish.yaml /Users/ck/linkml/linkml-runtime/.github/workflows/
cp /Users/ck/linkml/forks/linkml-runtime/.github/dependabot.yml /Users/ck/linkml/linkml-runtime/.github/
cp /Users/ck/linkml/forks/linkml-runtime/pyproject.toml /Users/ck/linkml/linkml-runtime/
cp /Users/ck/linkml/forks/linkml-runtime/Makefile /Users/ck/linkml/linkml-runtime/
cp /Users/ck/linkml/forks/linkml-runtime/CONTRIBUTING.md /Users/ck/linkml/linkml-runtime/
cp /Users/ck/linkml/forks/linkml-runtime/uv.lock /Users/ck/linkml/linkml-runtime/

# Remove old files
rm -f /Users/ck/linkml/linkml-runtime/poetry.lock
rm -f /Users/ck/linkml/linkml-runtime/tox.ini
```

## Step 4: Test and commit

```bash
cd /Users/ck/linkml/linkml-runtime
uv sync --group dev
uv run python -c "import linkml_runtime; print('Success')"
git add .
git status  # Review what changed
git commit -m "Migrate from Poetry to uv

- Replace Poetry with uv package manager
- Update all GitHub workflows to use uv
- Add uv.lock file and remove poetry.lock
- Update pyproject.toml to use modern dependency groups
- Remove obsolete tox.ini file"
```

## Notes
- We already completed Step 1 successfully with conflict resolution
- Now we need to execute Steps 2-4 to complete the migration
- The fork directory path should be verified before copying