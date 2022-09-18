#!/bin/bash

set -euo pipefail

BASE_BRANCH=$1
NEW_BRANCH=$2

function print_usage() {
    echo "create_branch.sh BASE_BRANCH NEW_BRANCH";
}

if [ -z ${BASE_BRANCH+x} ]; then 
    print_usage();
    echo "BASE_BRANCH is required";
    exit 1;
fi

if [ -z ${NEW_BRANCH+x} ]; then 
    print_usage();
    echo "NEW_BRANCH is required";
    exit 1;
fi


curl -X POST http://127.0.0.1:8000/create-branch \
    -H 'Content-Type: application/json' \
    -d "{\"base_branch\": \"$BASE_BRANCH\", \"branch_name\": \"$NEW_BRANCH\"}"
