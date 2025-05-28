#!/bin/bash

git filter-branch -f --env-filter '
    # Use the commit hash as a seed for reproducible pseudo-randomness
    seed=$(echo $GIT_COMMIT | tr -dc "0-9" | tail -c 5)
    [ -z "$seed" ] && seed=1

    # Spread over the last 7 days
    days_ago=$(( (seed % 7) ))
    hour=$(( (seed % 14) + 9 ))         # 9 AM to 22 PM (10 PM)
    minute=$(( (seed * 3) % 60 ))
    second=$(( (seed * 7) % 60 ))

    new_date=$(date -d "$days_ago days ago" +%Y-%m-%d)
    new_time=$(printf "%02d:%02d:%02d" $hour $minute $second)

    export GIT_AUTHOR_DATE="${new_date}T${new_time}-04:00"
    export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
' HEAD