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

[ "$RESTORE_CONFIRM" = "restore-empty-database" ] || fail "set RESTORE_CONFIRM=restore-empty-database after verifying the target is disposable/empty."
[ -f "$BACKUP_PATH" ] || fail "backup file does not exist."
[ -f "$CHECKSUM_PATH" ] || fail "checksum manifest does not exist."

command -v pg_restore >/dev/null 2>&1 || fail "pg_restore is required."
command -v psql >/dev/null 2>&1 || fail "psql is required."
command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required."
command -v awk >/dev/null 2>&1 || fail "awk is required."

expected_checksum=$(awk 'NR == 1 {print $1} NR == 2 {exit 1}' "$CHECKSUM_PATH") || fail "checksum manifest must contain exactly one entry."
[ "${#expected_checksum}" -eq 64 ] || fail "checksum manifest does not contain one SHA-256 digest."

case "$expected_checksum" in
  *[!0-9A-Fa-f]*)
    fail "checksum manifest does not contain one SHA-256 digest."
    ;;
esac

actual_checksum=$(sha256sum "$BACKUP_PATH" | awk '{print $1}')
[ "$actual_checksum" = "$expected_checksum" ] || fail "backup checksum verification failed."

pg_restore --list "$BACKUP_PATH" >/dev/null

object_count=$(psql "$RESTORE_DATABASE_URL" -X -A -t -v ON_ERROR_STOP=1 -c "SELECT count(*) FROM pg_catalog.pg_class AS c JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace WHERE n.nspname NOT IN ('pg_catalog', 'information_schema') AND n.nspname NOT LIKE 'pg_toast%' AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f');")

case "$object_count" in
  ''|*[!0-9]*)
    fail "could not determine whether the restore database is empty."
    ;;
esac

[ "$object_count" -eq 0 ] || fail "restore database is not empty; create a fresh database instead of overwriting in place."

pg_restore --exit-on-error --single-transaction --no-owner --no-acl --dbname="$RESTORE_DATABASE_URL" "$BACKUP_PATH"

printf '%s\n' "PostgreSQL restore completed into the explicitly selected empty database."
