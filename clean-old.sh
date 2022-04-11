#!/usr/bin/env bash

set -Eeuf -o pipefail
shopt -s inherit_errexit
set -x

main() {
  find /tmp -name '*.ics' -mmin +60 -delete
}
main "$@"
