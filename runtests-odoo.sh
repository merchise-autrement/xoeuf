#!/bin/bash
#
# Usage: ../runtests.sh [-i addons] [-s|--no-capture]
#
# This should be run inside an Odoo worktree.
#
# If a virtualenv is active it will use it unchanged.  Otherwise, it creates a
# new virtualenv, install the current Odoo tree, and the
# path-to-install-with-pip.
#
# Options:
#
#   `-i ADDONS`              Addons to test separated by commas.
#
#   `-s` (`--no-capture`)    Don't capture the output.  This allows to trace
#                            with pdb.
#
# The name of the DB is built from the name of the addon but it's hashed to
# avoid clashes in a shared DB env with a CI server not running in a
# container.
NOW=`date --utc +"%Y%m%d%H%M%N"`
CDIR=`pwd`
HASH=`echo "$CDIR-$NOW" | md5sum -t - | awk '{print $1}' |cut -b-9`
DB=tdb_"$HASH"
STDOUT="/tmp/odoo-$HASH.log"

echo "Logs in $STDOUT"

ADDONS=''
EXECUTABLE='xoeuf'

echo "POSTGRES_HOST: $POSTGRES_HOST, POSTGRES_USER: $POSTGRES_USER, POSTGRES_PASSWORD: $POSTGRES_PASSWORD"

function psql_wrapper() {
    cmd="$(which ${FUNCNAME[1]}) "
    if [ ! -z "$POSTGRES_HOST" ];then
        cmd="$cmd -h $POSTGRES_HOST"
    fi
    if [ ! -z "$POSTGRES_USER" ];then
        cmd="$cmd -U $POSTGRES_USER"
    fi
    echo $cmd $@
}

if [ ! -z "$POSTGRES_PASSWORD" ];then
    export PGPASSWORD="$POSTGRES_PASSWORD";
fi

function dropdb() { `psql_wrapper $@`; }
function createdb() { `psql_wrapper $@`; }
function psql() { `psql_wrapper $@`; }

while [ \! -z "$1" ]; do
    case $1 in
        -i)
            shift
            if [ -z "$1" ]; then
                echo "-i requires an argument"
                exit 1;
            else
                ADDONS="$1"
            fi
            ;;
        -s)
            STDOUT=''
            ;;
        --no-capture)
            STDOUT=''
            ;;
        *)
            ARGS="$ARGS $1"
            ;;
    esac
    shift
done

# Just in case
dropdb $DB 2>/dev/null

ARGS="$ARGS --stop-after-init --test-enable --log-level=test --workers=0 --max-cron-threads=0"
if [ -z "$ADDONS" ]; then
    # XXX: Putting -i all does not work.  I have to look in standard addons
    # places.  However, I omit hardware-related addons.
    ADDONS=`ls addons | grep -v ^hw| xargs | tr " " ","`
    ADDONS="$ADDONS,`ls odoo/addons | xargs | tr " " ","`"
fi
ARGS="$ARGS -i $ADDONS"

echo running $EXECUTABLE -d $DB $ARGS

# Create the DB install the addons and run tests.
if [ \! -z "$STDOUT" ]; then
    createdb -E UTF-8 --template=template0 "$DB" && \
        $EXECUTABLE -d $DB --db-filter=^$DB\$ $ARGS 2>&1 | tee $STDOUT
else
    createdb -E UTF-8 --template=template0 "$DB" && \
        $EXECUTABLE -d $DB --db-filter=^$DB\$ $ARGS
fi

egrep "(At least one test failed when loading the modules.|(ERROR|CRITICAL) $DB)" $STDOUT
code=$?
if (($code == 0 || $code == 2)); then
    CODE=1
else
    CODE=0
fi

exit $CODE
