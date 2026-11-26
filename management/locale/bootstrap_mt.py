#!/usr/bin/env python3
"""Bootstrap Phase 1 .po files with machine translations (MT-ok; fork-only).

Keeps the product name \"Trixie Mail\" untranslated. Run after extract.sh:
  python3 locale/bootstrap_mt.py
Then: ./locale/compile.sh

Uses Argos Translate offline. Placeholders (%(name)s), HTML tags, and the
brand name are masked before translation so gettext format stays valid.
Preserves existing non-empty msgstr that already have matching placeholders.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po

LOCALE_DIR = Path(__file__).resolve().parent
POT_PATH = LOCALE_DIR / "messages.pot"
LANGS = ("en", "de", "fr", "es", "it", "pt", "nl", "pl")
BRAND = "Trixie Mail"

PLURAL_FORMS = {
	"en": "nplurals=2; plural=(n != 1);",
	"de": "nplurals=2; plural=(n != 1);",
	"fr": "nplurals=2; plural=(n > 1);",
	"es": "nplurals=2; plural=(n != 1);",
	"it": "nplurals=2; plural=(n != 1);",
	"pt": "nplurals=2; plural=(n != 1);",
	"nl": "nplurals=2; plural=(n != 1);",
	"pl": "nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
}

PH_RE = re.compile(r"%\(([^)]+)\)s")
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>|&[a-zA-Z]+;|&#\w+;")


def placeholders(s: str) -> list[str]:
	return PH_RE.findall(s) if isinstance(s, str) else []


def placeholders_ok(msgid: str, msgstr: str) -> bool:
	return placeholders(msgid) == placeholders(msgstr)


def mask(s: str):
	ph_map: list[str] = []

	def ph_sub(m):
		ph_map.append(m.group(0))
		return f"⟦P{len(ph_map) - 1}⟧"

	s2 = PH_RE.sub(ph_sub, s)
	s2 = s2.replace(BRAND, "⟦BRAND⟧")
	tag_map: list[str] = []

	def tag_sub(m):
		tag_map.append(m.group(0))
		return f"⟦T{len(tag_map) - 1}⟧"

	s2 = TAG_RE.sub(tag_sub, s2)
	return s2, ph_map, tag_map


def unmask(s: str, ph_map: list[str], tag_map: list[str]) -> str:
	if not s:
		return s
	s = re.sub(r"⟦\s*BRAND\s*⟧", BRAND, s, flags=re.I)
	for i, tag in enumerate(tag_map):
		s = re.sub(rf"⟦\s*T{i}\s*⟧", tag, s)
	for i, ph in enumerate(ph_map):
		s = re.sub(rf"⟦\s*P{i}\s*⟧", ph, s)
	s = re.sub(r"Trixie[\s\-]*Mail", BRAND, s, flags=re.I)
	return s


def load_existing(lang: str) -> dict:
	path = LOCALE_DIR / lang / "LC_MESSAGES" / "messages.po"
	out = {}
	if not path.exists():
		return out
	with path.open(encoding="utf-8") as f:
		cat = read_po(f)
	for msg in cat:
		if not msg.id or not isinstance(msg.id, str) or not msg.string:
			continue
		out[msg.id] = msg.string
	return out


def translate_one(text: str, lang: str) -> str:
	try:
		from argostranslate import translate as argos_translate
	except ImportError:
		print("argostranslate not installed; using English fallback", file=sys.stderr)
		return text
	masked, ph_map, tag_map = mask(text)
	try:
		raw = argos_translate.translate(masked, "en", lang)
	except Exception as e:
		print(f"  Argos {lang} skip: {e!r}", file=sys.stderr)
		return text
	out = unmask(raw or "", ph_map, tag_map)
	if not out or not placeholders_ok(text, out):
		return text  # safe English fallback
	return out


def main():
	with POT_PATH.open(encoding="utf-8") as f:
		pot = read_po(f)

	for lang in LANGS:
		existing = load_existing(lang)
		cat = Catalog(
			locale=lang,
			domain="messages",
			header_comment=pot.header_comment,
			project=pot.project,
			version=pot.version,
			copyright_holder=pot.copyright_holder,
			msgid_bugs_address=pot.msgid_bugs_address,
			creation_date=pot.creation_date,
			revision_date="2026-11-26 15:10+0000",
			last_translator="Trixie Mail MT bootstrap <noreply@localhost>",
			language_team=lang,
			fuzzy=False,
		)
		n_new = 0
		n_keep = 0
		n_fb = 0
		for message in pot:
			if not message.id:
				continue
			msgid = message.id
			if lang == "en":
				msgstr = msgid
			elif isinstance(msgid, str) and msgid in existing and placeholders_ok(msgid, existing[msgid]):
				msgstr = existing[msgid]
				n_keep += 1
			elif isinstance(msgid, str):
				msgstr = translate_one(msgid, lang)
				if msgstr == msgid:
					n_fb += 1
				else:
					n_new += 1
			else:
				msgstr = ""
			cat.add(
				msgid,
				string=msgstr,
				locations=message.locations,
				auto_comments=list(message.auto_comments)
				+ (
					["Status: mt", "Phase: 1"]
					if lang != "en"
					else ["Status: source", "Phase: 1"]
				),
				user_comments=message.user_comments,
				context=message.context,
			)

		out_dir = LOCALE_DIR / lang / "LC_MESSAGES"
		out_dir.mkdir(parents=True, exist_ok=True)
		out_path = out_dir / "messages.po"
		with out_path.open("wb") as f:
			write_po(f, cat, ignore_obsolete=True, include_previous=False, width=76)
		text = out_path.read_text(encoding="utf-8")
		if "Plural-Forms:" not in text:
			text = text.replace(
				'"Content-Transfer-Encoding: 8bit\\n"\n',
				'"Content-Transfer-Encoding: 8bit\\n"\n'
				f'"Plural-Forms: {PLURAL_FORMS[lang]}\\n"\n',
			)
			out_path.write_text(text, encoding="utf-8")
		filled = sum(1 for m in cat if m.id and m.string)
		print(f"Wrote {out_path} filled={filled} keep={n_keep} new={n_new} en_fallback={n_fb}")


if __name__ == "__main__":
	os.chdir(LOCALE_DIR.parent)
	main()
