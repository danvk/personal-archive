#!/usr/bin/python2.7

import mailbox

assert len(sys.argv) == 2

m = mailbox.mbox(sys.argv[1])
