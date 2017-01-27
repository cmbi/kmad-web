#!/bin/bash

MYDIR=$(dirname $0)

UPDATE=$MYDIR/update_databanks.bash
chmod 755 $UPDATE

if ! [ -f /data/nr.pal ] ; then

    # Databanks not present, build now!
    $UPDATE
fi

ENV="
PATH=$PATH
"

CRONFILE=$MYDIR/update_cron

/bin/echo -e "$ENV\n0 20 * * 5 /bin/bash $UPDATE\n" > $CRONFILE
crontab $CRONFILE

cron -f
