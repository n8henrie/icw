#!/usr/bin/env bash

set -Eeuf -o pipefail
shopt -s inherit_errexit

main() {
  find /tmp -name '*.ics' -mmin +60 -delete
}
main "$@"
