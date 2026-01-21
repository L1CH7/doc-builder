#!/bin/bash
# Helper to push to multiple remotes

# Prerequisite: Remotes must be added
# git remote add origin https://github.com/L1CH7/doc-builder.git
# git remote add work https://gitlab.work...

echo "Pushing to origin..."
git push origin main

if git remote | grep -q "work"; then
    echo "Pushing to work..."
    git push work main
else
    echo "Remote 'work' not defined."
fi
