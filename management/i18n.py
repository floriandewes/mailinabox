# Trixie Mail control-panel localization helpers (fork-only; not for upstream MIAB).
# Locale preference: cookie trixiemail_lang → Accept-Language → en.
# Client mirror: localStorage key trixiemail-cp-lang.

import json
import os
import re

from flask import request, g

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

COOKIE_NAME = "trixiemail_lang"
LOCALSTORAGE_KEY = "trixiemail-cp-lang"
COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # ~1 year

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
_JSON_DIR = os.path.join(_LOCALE_DIR, "json")

_LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Za-z0-9]+)?$")


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
	return getattr(g, "locale", None) or get_locale()


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
	secure = request.is_secure
	response.set_cookie(
		COOKIE_NAME,
		lang,
		max_age=COOKIE_MAX_AGE,
		path="/admin",
		samesite="Lax",
		secure=secure,
	)
	return response
