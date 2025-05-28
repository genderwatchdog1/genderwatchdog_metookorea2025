#!/bin/bash

# Get all commit hashes in reverse (oldest first)
commits=$(git rev-list --reverse HEAD)

for commit in $commits; do
    # Generate a random date in the last 60 days, between 9:00 and 18:59
    rand_date=$(python3 -c "
import random, datetime
days_ago = random.randint(0, 59)
hour = random.randint(9, 18)
minute = random.randint(0, 59)
second = random.randint(0, 59)
dt = datetime.datetime.now() - datetime.timedelta(days=days_ago)
dt = dt.replace(hour=hour, minute=minute, second=second, microsecond=0)
print(dt.strftime('%Y-%m-%dT%H:%M:%S-04:00'))
")
    # Rewrite the commit date
    GIT_COMMITTER_DATE="$rand_date" GIT_AUTHOR_DATE="$rand_date" git filter-branch -f --env-filter "
        if [ \$GIT_COMMIT = $commit ]; then
            export GIT_AUTHOR_DATE='$rand_date'
            export GIT_COMMITTER_DATE='$rand_date'
        fi
    " $commit^..$commit
done