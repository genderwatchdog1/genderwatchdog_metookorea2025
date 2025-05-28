#!/bin/bash

# Get all commit hashes in reverse (oldest first)
commits=($(git rev-list --reverse HEAD))

# Start from 30 days ago, incrementing by a random amount for each commit
base_date=$(date -d "30 days ago" +%s)

for i in "${!commits[@]}"; do
    # Add a random offset (0-2 days) to the base date for each commit
    offset_days=$((RANDOM % 3))
    commit_date=$((base_date + (i + offset_days) * 86400))
    # Random hour/minute/second between 9:00 and 18:59
    hour=$((RANDOM % 10 + 9))
    minute=$((RANDOM % 60))
    second=$((RANDOM % 60))
    # Format as NY time (EDT, -04:00)
    formatted_date=$(date -d "@$commit_date" +"%Y-%m-%dT%02d:%02d:%02d-04:00" $hour $minute $second)
    export GIT_COMMITTER_DATE="$formatted_date"
    export GIT_AUTHOR_DATE="$formatted_date"
    # Rewrite this commit
    git filter-branch -f --env-filter "
        if [ \$GIT_COMMIT = ${commits[$i]} ]; then
            export GIT_AUTHOR_DATE='$formatted_date'
            export GIT_COMMITTER_DATE='$formatted_date'
        fi
    " ${commits[$i]}^..${commits[$i]}
done