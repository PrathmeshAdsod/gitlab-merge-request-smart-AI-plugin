#!/usr/bin/env bash
set -e

# Only format files changed in the MR, by extension.
# Customize FILE_GLOBS and FORMATTER_COMMANDS as needed.

TARGET_BRANCH="${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-main}"
SOURCE_BRANCH="${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME:-$CI_COMMIT_REF_NAME}"

echo "Diffing $TARGET_BRANCH...$SOURCE_BRANCH"

# List changed files with relevant extensions
CHANGED_FILES=$(git diff --name-only "$TARGET_BRANCH"..."$SOURCE_BRANCH" | grep -E '\.py$|\.js$|\.ts$|\.go$|\.rb$' || true)

if [ -z "$CHANGED_FILES" ]; then
  echo "No relevant files changed."
  exit 0
fi

echo "Changed files:"
echo "$CHANGED_FILES"

# Formatters per language (customize as needed)
for file in $CHANGED_FILES; do
  case "$file" in
    *.py)
      echo "Formatting $file with black and flake8"
      black "$file" || true
      flake8 "$file" || true
      ;;
    *.js|*.ts)
      echo "Formatting $file with prettier and eslint"
      npx prettier --write "$file" || true
      npx eslint --fix "$file" || true
      ;;
    *.go)
      echo "Formatting $file with gofmt"
      gofmt -w "$file" || true
      ;;
    *.rb)
      echo "Formatting $file with rubocop"
      rubocop -A "$file" || true
      ;;
    *)
      echo "No formatter for $file"
      ;;
  esac
done

# Fail if formatting issues remain
if ! git diff --exit-code; then
  echo "Formatting or lint errors remain. Please fix and commit."
  exit 1
fi

echo "Formatting complete."
