#!/bin/sh
set -eu

umask 077

fail() {
  printf '%s\n' "postgres_backup: $*" >&2
  exit 1
}

: "${DATABASE_URL:?DATABASE_URL is required}"

BACKUP_PATH="${BACKUP_PATH:-artifacts/backups/cultural-currency.dump}"
BACKUP_OVERWRITE="${BACKUP_OVERWRITE:-false}"
CHECKSUM_PATH="${BACKUP_PATH}.sha256"

[ -n "$BACKUP_PATH" ] || fail "BACKUP_PATH must not be empty."
[ "$BACKUP_PATH" != "/" ] || fail "BACKUP_PATH must not be the filesystem root."

command -v pg_dump >/dev/null 2>&1 || fail "pg_dump is required."
command -v pg_restore >/dev/null 2>&1 || fail "pg_restore is required."
command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required."

if [ -e "$BACKUP_PATH" ] || [ -e "$CHECKSUM_PATH" ]; then
  [ "$BACKUP_OVERWRITE" = "true" ] || fail     "backup or checksum already exists; choose a unique BACKUP_PATH or set BACKUP_OVERWRITE=true."
fi

backup_dir=$(dirname "$BACKUP_PATH")
backup_name=$(basename "$BACKUP_PATH")
mkdir -p "$backup_dir"

tmp_backup="${BACKUP_PATH}.tmp.$$"
tmp_checksum="${CHECKSUM_PATH}.tmp.$$"

cleanup() {
  rm -f "$tmp_backup" "$tmp_checksum"
}
trap cleanup EXIT HUP INT TERM

pg_dump   --format=custom   --no-owner   --no-acl   --file="$tmp_backup"   "$DATABASE_URL"

pg_restore --list "$tmp_backup" >/dev/null

checksum=$(sha256sum "$tmp_backup" | awk '{print $1}')
[ -n "$checksum" ] || fail "failed to calculate backup checksum."

printf '%s  %s\n' "$checksum" "$backup_name" > "$tmp_checksum"

mv -f "$tmp_backup" "$BACKUP_PATH"
mv -f "$tmp_checksum" "$CHECKSUM_PATH"

trap - EXIT HUP INT TERM

printf '%s\n' "PostgreSQL backup created: $BACKUP_PATH"
printf '%s\n' "SHA-256 manifest created: $CHECKSUM_PATH"
