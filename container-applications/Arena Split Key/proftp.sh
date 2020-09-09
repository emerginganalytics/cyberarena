#!/bin/bash

## Bash Script to maintain ftp server.
### if server not running, restart process

FPTPROC="$(ps -ax | grep '[p]roftp')"
SUB="proftp"
if [[ $FPTPROC != *"proftp"* ]]; then
    cd /opt/proftp/proftp-1.3.5 && ./proftp
fi