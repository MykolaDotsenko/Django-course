#!/bin/sh
set -eu

umask 077

fail() {
  printf '%s\n' "postgres_restore: $*" >&2
  exit 1
}

: "${RESTORE_DATABASE_URL:?RESTORE_DATABASE_URL is required}"
: "${BACKUP_PATH:?BACKUP_PATH is required}"

RESTORE_CONFIRM="${RESTORE_CONFIRM:-}"
CHECKSUM_PATH="${CHECKSUM_PATH:-${BACKUP_PATH}.sha256}"

[ "$RESTORE_CONFIRM" = "restore-empty-database" ] || fail   "set RESTORE_CONFIRM=restore-empty-database after verifying the target is disposable/empty."

[ -f "$BACKUP_PATH" ] || fail "backup file does not exist."
[ -f "$CHECKSUM_PATH" ] || fail "checksum manifest does not exist."

command -v pg_restore >/dev/null 2>&1 || fail "pg_restore is required."
command -v psql >/dev/null 2>&1 || fail "psql is required."
command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required."

backup_dir=$(dirname "$BACKUP_PATH")
backup_name=$(basename "$BACKUP_PATH")
checksum_dir=$(dirname "$CHECKSUM_PATH")
checksum_name=$(basename "$CHECKSUM_PATH")

[ "$backup_dir" = "$checksum_dir" ] || fail   "backup and checksum manifest must be in the same directory."

(
  cd "$backup_dir"
  sha256sum -c "$checksum_name"
)

pg_restore --list "$BACKUP_PATH" >/dev/null

object_count=$(
  psql "$RESTORE_DATABASE_URL"     -X     -A     -t     -v ON_ERROR_STOP=1     -c "SELECT count(*)
        FROM pg_catalog.pg_class AS c
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
          AND n.nspname NOT LIKE 'pg_toast%'
          AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f');"
)

case "$object_count" in
  ''|*[!0-9]*)
    fail "could not determine whether the restore database is empty."
    ;;
esac

[ "$object_count" -eq 0 ] || fail   "restore database is not empty; create a fresh database instead of overwriting in place."

pg_restore   --exit-on-error   --single-transaction   --no-owner   --no-acl   --dbname="$RESTORE_DATABASE_URL"   "$BACKUP_PATH"

printf '%s\n' "PostgreSQL restore completed into the explicitly selected empty database."
