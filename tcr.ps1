# Run Python unittest
pipenv run black .
python -m unittest

# Check the exit code of the last command
if ($LASTEXITCODE -eq 0) {
    # Test passed, stage changes and commit
    git add .
    git commit -m "Working"
} else {
    # Test failed, reset to HEAD
    git reset --hard HEAD
}