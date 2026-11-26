# Trixie Mail control-panel localization helpers (fork-only; not for upstream MIAB).
# Locale preference: cookie trixiemail_lang → Accept-Language → en.
# Client mirror: localStorage key trixiemail-cp-lang.
# System preference (admin emails / Roundcube / Nextcloud defaults):
#   $STORAGE_ROOT/ui_locale — written when the CP language is changed.
#
# gettext/_ work both in Flask request context and in multiprocessing pool
# workers (status checks): call activate_locale() before Pool creation so
# forked children inherit the Translations object.

import gettext
import json
import os
import re

# Flask is optional for CLI callers (email_administrator.py). Request helpers
# import it lazily so cron mail works even if only gettext is needed.
try:
	from flask import request, g
except ImportError:  # pragma: no cover - management venv always has Flask
	request = None
	g = None

try:
	from babel.support import Translations
except ImportError:  # pragma: no cover - Babel is a management dependency
	Translations = None

# Phase 1 shipped languages (ISO 639-1). English is the source locale.
SUPPORTED_LOCALES = ("en", "de", "fr", "es", "it", "pt", "nl", "pl")

# Short labels for the navbar list switcher (ISO codes; not flags).
LOCALE_LABELS = {
	"en": "EN",
	"de": "DE",
	"fr": "FR",
	"es": "ES",
	"it": "IT",
	"pt": "PT",
	"nl": "NL",
	"pl": "PL",
}

# Roundcube expects locale tags like de_DE (bundled with the app).
ROUNDCUBE_LOCALES = {
	"en": "en_US",
	"de": "de_DE",
	"fr": "fr_FR",
	"es": "es_ES",
	"it": "it_IT",
	"pt": "pt_PT",
	"nl": "nl_NL",
	"pl": "pl_PL",
}

# Nextcloud default_language codes (European Portuguese → pt_PT).
NEXTCLOUD_LOCALES = {
	"en": "en",
	"de": "de",
	"fr": "fr",
	"es": "es",
	"it": "it",
	"pt": "pt_PT",
	"nl": "nl",
	"pl": "pl",
}

COOKIE_NAME = "trixiemail_lang"
LOCALSTORAGE_KEY = "trixiemail-cp-lang"
COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # ~1 year
SYSTEM_LOCALE_FILENAME = "ui_locale"

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
_JSON_DIR = os.path.join(_LOCALE_DIR, "json")

_LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Za-z0-9]+)?$")

# Module-level active catalog for pool workers / non-request code paths.
_active_locale = "en"
_active_translations = None


def locale_dir():
	return _LOCALE_DIR


def json_catalog_dir():
	return _JSON_DIR


def normalize_locale(code):
	"""Map a BCP 47 / Accept-Language tag to a supported base locale, or None."""
	if not code:
		return None
	code = code.strip().replace("_", "-")
	if not _LOCALE_RE.match(code):
		return None
	base = code.split("-", 1)[0].lower()
	if base in SUPPORTED_LOCALES:
		return base
	return None


def get_locale():
	"""Resolve the active locale for this request (cookie → Accept-Language → en)."""
	if request is None:
		return "en"

	# Explicit user choice via cookie.
	cookie = request.cookies.get(COOKIE_NAME)
	resolved = normalize_locale(cookie)
	if resolved:
		return resolved

	# Browser preference.
	best = request.accept_languages.best_match(SUPPORTED_LOCALES)
	if best:
		return best

	return "en"


def get_locale_for_template():
	"""Locale already selected for this request (set in before_request)."""
	if g is None:
		return get_locale()
	return getattr(g, "locale", None) or get_locale()


def system_locale_path(env):
	"""Path of the box-wide UI locale file under STORAGE_ROOT."""
	return os.path.join(env["STORAGE_ROOT"], SYSTEM_LOCALE_FILENAME)


def get_system_locale(env):
	"""Box-wide locale for cron emails and app defaults. Falls back to en."""
	try:
		path = system_locale_path(env)
		with open(path, encoding="utf-8") as f:
			return normalize_locale(f.read()) or "en"
	except (OSError, TypeError, KeyError):
		return "en"


def set_system_locale(lang, env):
	"""Persist box-wide locale (used by admin emails / setup defaults)."""
	lang = normalize_locale(lang) or "en"
	path = system_locale_path(env)
	# Match typical STORAGE_ROOT permissions (owner-writable).
	with open(path, "w", encoding="utf-8") as f:
		f.write(lang + "\n")
	return lang


def gettext_for_locale(lang):
	"""Return a gettext.gettext bound to lang (stdlib; works outside Flask)."""
	lang = normalize_locale(lang) or "en"
	try:
		trans = gettext.translation(
			"messages",
			localedir=_LOCALE_DIR,
			languages=[lang],
		)
		return trans.gettext
	except OSError:
		return lambda s: s


def roundcube_language(lang):
	"""Roundcube $config['language'] value for a Phase 1 locale."""
	lang = normalize_locale(lang) or "en"
	return ROUNDCUBE_LOCALES.get(lang, "en_US")


def nextcloud_language(lang):
	"""Nextcloud default_language value for a Phase 1 locale."""
	lang = normalize_locale(lang) or "en"
	return NEXTCLOUD_LOCALES.get(lang, "en")


def activate_locale(lang):
	"""Load gettext Translations for lang into module state (fork-friendly).

	Call this before creating a multiprocessing.Pool so workers inherit the
	active catalog. English keeps translations as None (identity).
	"""
	global _active_locale, _active_translations
	lang = normalize_locale(lang) or "en"
	_active_locale = lang
	if lang == "en" or Translations is None:
		_active_translations = None
		return
	# Babel expects the parent locale/ dir (…/locale/<lang>/LC_MESSAGES/messages.mo).
	try:
		_active_translations = Translations.load(_LOCALE_DIR, locales=[lang], domain="messages")
	except Exception:
		_active_translations = None


def get_active_locale():
	return _active_locale


def gettext(message):
	"""Translate message using request locale, or activated module locale."""
	if not message:
		return message
	# Prefer Flask-Babel when a request context is active (main daemon thread).
	try:
		from flask import has_request_context
		if has_request_context():
			from flask_babel import gettext as flask_gettext
			return flask_gettext(message)
	except Exception:
		pass
	# Pool workers / CLI: use Translations loaded by activate_locale().
	if _active_translations is not None:
		return _active_translations.gettext(message)
	return message


def ngettext(singular, plural, n):
	"""Plural-aware gettext; same fallback chain as gettext()."""
	try:
		from flask import has_request_context
		if has_request_context():
			from flask_babel import ngettext as flask_ngettext
			return flask_ngettext(singular, plural, n)
	except Exception:
		pass
	if _active_translations is not None:
		return _active_translations.ngettext(singular, plural, n)
	return singular if n == 1 else plural


# Conventional alias used throughout management/*.py
_ = gettext


def load_json_catalog(lang):
	"""Load the browser JSON catalog for lang. Falls back to {} (English msgids)."""
	lang = normalize_locale(lang) or "en"
	path = os.path.join(_JSON_DIR, f"{lang}.json")
	if not os.path.isfile(path):
		return {}
	try:
		with open(path, encoding="utf-8") as f:
			data = json.load(f)
		if isinstance(data, dict):
			return data
	except (OSError, ValueError, TypeError):
		pass
	return {}


def locale_switcher_entries():
	"""List of {code, label} for every Phase 1 language with a catalog (or en)."""
	entries = []
	for code in SUPPORTED_LOCALES:
		# Ship when catalog exists; en always available (source language).
		json_path = os.path.join(_JSON_DIR, f"{code}.json")
		po_path = os.path.join(_LOCALE_DIR, code, "LC_MESSAGES", "messages.po")
		if code == "en" or os.path.isfile(json_path) or os.path.isfile(po_path):
			entries.append({
				"code": code,
				"label": LOCALE_LABELS.get(code, code.upper()),
			})
	return entries


def apply_locale_cookie(response, lang):
	"""Set the locale cookie on a Flask response."""
	lang = normalize_locale(lang) or "en"
	secure = bool(request is not None and request.is_secure)
	response.set_cookie(
		COOKIE_NAME,
		lang,
		max_age=COOKIE_MAX_AGE,
		path="/admin",
		samesite="Lax",
		secure=secure,
	)
	return response
