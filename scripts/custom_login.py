"""Manage the override-credential list (`customized_login.py`).

    python3 scripts/custom_login.py list
    python3 scripts/custom_login.py hash  someone@example.com   # prints a SEED line
    python3 scripts/custom_login.py set   someone@example.com   # writes to the store

`hash` never touches storage — it prints a line to paste into `SEED_HASHES`, so
the committed list holds hashes and the plaintext never enters the repo.
`set` writes to the live store (Postgres if `JERRY_GPT_DB_URL` is set, else the
local JSON file).

The password is read from a prompt, not an argument, so it stays out of your
shell history and the process list.
"""
from __future__ import annotations

import getpass
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import customized_login as cl                                        # noqa: E402


def _read_password(confirm: bool = True) -> str:
    pw = getpass.getpass("New password: ")
    err = cl.validate_new_password(pw)
    if err:
        sys.exit(f"  {err}")
    if confirm and getpass.getpass("Confirm password: ") != pw:
        sys.exit("  Passwords do not match.")
    return pw


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1].lower()

    if cmd == "list":
        emails = cl.all_emails()
        print(f"  storage backend: {cl.storage_backend()}")
        print(f"  {len(emails)} account(s) on the override list:")
        for e in emails:
            has = bool(cl._overrides().get(e) or cl._seed().get(e))
            print(f"    {e:40s} {'password set' if has else 'NO PASSWORD YET'}")
        return

    if cmd in ("hash", "set"):
        if len(sys.argv) < 3:
            sys.exit(f"  usage: {sys.argv[0]} {cmd} <email>")
        email = sys.argv[2].strip().lower()
        pw = _read_password()

        if cmd == "hash":
            print("\n  Paste this into SEED_HASHES in customized_login.py:\n")
            print(f'    "{email}": "{cl.hash_password(pw)}",\n')
            print("  (a hash, not a password — safe to commit)")
            return

        ok, detail = cl.set_password(email, pw)
        if not ok:
            sys.exit(f"  {detail}")
        print(f"  password set for {email} in the {cl.storage_backend()}")
        return

    sys.exit(__doc__)


if __name__ == "__main__":
    main()
