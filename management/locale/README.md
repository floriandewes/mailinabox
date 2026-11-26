# Control panel locales (Trixie Mail fork-only)

gettext catalogs for the admin UI. Phase 1 languages: `en de fr es it pt nl pl`.

- `extract.sh` — refresh `messages.pot` from Python/Jinja (+ `js_messages.py`)
- `compile.sh` — build `.mo` and browser `json/<lang>.json`
- `bootstrap_mt.py` — fill Phase 1 `.po` files with MT strings (re-run after extract when bootstrapping)

Brand name **Trixie Mail** stays untranslated. Switcher lists every Phase 1 locale that has a catalog.
