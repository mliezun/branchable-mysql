#!/bin/bash

set -euo pipefail

BRANCH_NAME=$1

function print_usage() {
    echo "delete_branch.sh BRANCH_NAME";
}

if [ -z ${BRANCH_NAME+x} ]; then 
    print_usage();
    echo "BRANCH_NAME is required";
    exit 1;
fi

curl -X DELETE http://127.0.0.1:8000/delete-branch \
    -H 'Content-Type: application/json' \
    -d "{\"branch_name\": \"$BRANCH_NAME\"}"
