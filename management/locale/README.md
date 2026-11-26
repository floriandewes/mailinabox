# Control panel locales (Trixie Mail fork-only)

gettext catalogs for the admin UI. Phase 1 languages: `en de fr es it pt nl pl`.

- `extract.sh` — refresh `messages.pot` from Python/Jinja (+ `js_messages.py`, `email_messages.py`)
- `compile.sh` — build `.mo` and browser `json/<lang>.json`
- `bootstrap_mt.py` — fill Phase 1 `.po` files with MT strings (re-run after extract when bootstrapping)

Brand name **Trixie Mail** stays untranslated. Switcher lists every Phase 1 locale that has a catalog.

## Box-wide preference (`$STORAGE_ROOT/ui_locale`)

Changing language in the control panel also writes `$STORAGE_ROOT/ui_locale`. That file drives:

- translated subjects in `management/email_administrator.py` (cron mail)
- Roundcube `$config['language']` and Nextcloud `default_language` on the next setup re-run

The public default homepage (`conf/www_default.html`) is a static BBS-style placeholder (not localized).
