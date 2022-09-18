#!/bin/bash

set -euo pipefail

curl -X GET http://127.0.0.1:8000/list-branches
