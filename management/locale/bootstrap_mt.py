#!/usr/bin/env python3
"""Bootstrap Phase 1 .po files with machine translations (MT-ok; fork-only).

Keeps the product name \"Trixie Mail\" untranslated. Run after extract.sh:
  python3 locale/bootstrap_mt.py
Then: ./locale/compile.sh

Inline MT covers chrome strings; management/locale/mt_extra.json holds
Status Checks + auth/API error follow-up translations (merged at runtime).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po

LOCALE_DIR = Path(__file__).resolve().parent
POT_PATH = LOCALE_DIR / "messages.pot"
MT_EXTRA_PATH = LOCALE_DIR / "mt_extra.json"
LANGS = ("en", "de", "fr", "es", "it", "pt", "nl", "pl")

# msgid (English) → {lang: msgstr}. Empty = leave English / identity.
# "Trixie Mail" is never translated.
MT = {
	"Loading...": {
		"de": "Laden…",
		"fr": "Chargement…",
		"es": "Cargando…",
		"it": "Caricamento…",
		"pt": "A carregar…",
		"nl": "Laden…",
		"pl": "Ładowanie…",
	},
	"Error": {
		"de": "Fehler",
		"fr": "Erreur",
		"es": "Error",
		"it": "Errore",
		"pt": "Erro",
		"nl": "Fout",
		"pl": "Błąd",
	},
	"Something went wrong, sorry.": {
		"de": "Etwas ist schiefgelaufen, Entschuldigung.",
		"fr": "Une erreur s’est produite, désolé.",
		"es": "Algo salió mal, lo sentimos.",
		"it": "Qualcosa è andato storto, ci dispiace.",
		"pt": "Algo correu mal, desculpe.",
		"nl": "Er ging iets mis, sorry.",
		"pl": "Coś poszło nie tak, przepraszamy.",
	},
	"OK": {
		"de": "OK",
		"fr": "OK",
		"es": "Aceptar",
		"it": "OK",
		"pt": "OK",
		"nl": "OK",
		"pl": "OK",
	},
	"Cancel": {
		"de": "Abbrechen",
		"fr": "Annuler",
		"es": "Cancelar",
		"it": "Annulla",
		"pt": "Cancelar",
		"nl": "Annuleren",
		"pl": "Anuluj",
	},
	"Yes": {
		"de": "Ja",
		"fr": "Oui",
		"es": "Sí",
		"it": "Sì",
		"pt": "Sim",
		"nl": "Ja",
		"pl": "Tak",
	},
	"Close Dialog": {
		"de": "Dialog schließen",
		"fr": "Fermer la boîte de dialogue",
		"es": "Cerrar diálogo",
		"it": "Chiudi finestra",
		"pt": "Fechar diálogo",
		"nl": "Dialoog sluiten",
		"pl": "Zamknij okno",
	},
	"Toggle navigation": {
		"de": "Navigation umschalten",
		"fr": "Afficher/masquer la navigation",
		"es": "Alternar navegación",
		"it": "Attiva/disattiva navigazione",
		"pt": "Alternar navegação",
		"nl": "Navigatie tonen/verbergen",
		"pl": "Przełącz nawigację",
	},
	"Login Failed": {
		"de": "Anmeldung fehlgeschlagen",
		"fr": "Échec de la connexion",
		"es": "Error de inicio de sesión",
		"it": "Accesso non riuscito",
		"pt": "Falha no início de sessão",
		"nl": "Inloggen mislukt",
		"pl": "Logowanie nie powiodło się",
	},
	"Enter your email address.": {
		"de": "Geben Sie Ihre E-Mail-Adresse ein.",
		"fr": "Saisissez votre adresse e-mail.",
		"es": "Introduzca su dirección de correo electrónico.",
		"it": "Inserisci il tuo indirizzo e-mail.",
		"pt": "Introduza o seu endereço de e-mail.",
		"nl": "Voer uw e-mailadres in.",
		"pl": "Wprowadź swój adres e-mail.",
	},
	"Enter your email password.": {
		"de": "Geben Sie Ihr E-Mail-Passwort ein.",
		"fr": "Saisissez votre mot de passe e-mail.",
		"es": "Introduzca su contraseña de correo electrónico.",
		"it": "Inserisci la password della tua e-mail.",
		"pt": "Introduza a palavra-passe do e-mail.",
		"nl": "Voer uw e-mailwachtwoord in.",
		"pl": "Wprowadź hasło do skrzynki e-mail.",
	},
	"Incorrect two factor authentication token.": {
		"de": "Falscher Zwei-Faktor-Authentifizierungscode.",
		"fr": "Code d’authentification à deux facteurs incorrect.",
		"es": "Código de autenticación en dos pasos incorrecto.",
		"it": "Codice di autenticazione a due fattori non corretto.",
		"pt": "Código de autenticação de dois fatores incorreto.",
		"nl": "Onjuiste tweefactorauthenticatiecode.",
		"pl": "Nieprawidłowy kod uwierzytelniania dwuskładnikowego.",
	},
	"You are not an administrator on this system.": {
		"de": "Sie sind kein Administrator auf diesem System.",
		"fr": "Vous n’êtes pas administrateur sur ce système.",
		"es": "No es administrador en este sistema.",
		"it": "Non sei un amministratore di questo sistema.",
		"pt": "Não é administrador neste sistema.",
		"nl": "U bent geen beheerder op dit systeem.",
		"pl": "Nie jesteś administratorem tego systemu.",
	},
	"Trixie Mail Control Panel": {
		"de": "Trixie Mail Control Panel",
		"fr": "Panneau de contrôle Trixie Mail",
		"es": "Panel de control de Trixie Mail",
		"it": "Pannello di controllo Trixie Mail",
		"pt": "Painel de controlo Trixie Mail",
		"nl": "Trixie Mail-beheerpaneel",
		"pl": "Panel sterowania Trixie Mail",
	},
	"Internet Explorer version 8 or any modern web browser is required to use this website, sorry.": {
		"de": "Internet Explorer Version 8 oder ein moderner Webbrowser ist erforderlich, um diese Website zu nutzen.",
		"fr": "Internet Explorer version 8 ou tout navigateur moderne est requis pour utiliser ce site, désolé.",
		"es": "Se requiere Internet Explorer versión 8 o cualquier navegador moderno para usar este sitio, lo sentimos.",
		"it": "Per usare questo sito è necessario Internet Explorer versione 8 o un browser moderno.",
		"pt": "É necessário o Internet Explorer versão 8 ou qualquer navegador moderno para usar este site.",
		"nl": "Internet Explorer versie 8 of een moderne webbrowser is vereist om deze site te gebruiken.",
		"pl": "Do korzystania z tej witryny wymagany jest Internet Explorer w wersji 8 lub nowa przeglądarka.",
	},
	"System": {
		"de": "System",
		"fr": "Système",
		"es": "Sistema",
		"it": "Sistema",
		"pt": "Sistema",
		"nl": "Systeem",
		"pl": "System",
	},
	"Status Checks": {
		"de": "Statusprüfungen",
		"fr": "Vérifications d’état",
		"es": "Comprobaciones de estado",
		"it": "Controlli di stato",
		"pt": "Verificações de estado",
		"nl": "Statuscontroles",
		"pl": "Kontrole stanu",
	},
	"TLS (SSL) Certificates": {
		"de": "TLS-(SSL-)Zertifikate",
		"fr": "Certificats TLS (SSL)",
		"es": "Certificados TLS (SSL)",
		"it": "Certificati TLS (SSL)",
		"pt": "Certificados TLS (SSL)",
		"nl": "TLS-(SSL-)certificaten",
		"pl": "Certyfikaty TLS (SSL)",
	},
	"Backup Status": {
		"de": "Backup-Status",
		"fr": "État des sauvegardes",
		"es": "Estado de la copia de seguridad",
		"it": "Stato del backup",
		"pt": "Estado da cópia de segurança",
		"nl": "Back-upstatus",
		"pl": "Stan kopii zapasowej",
	},
	"Advanced Pages": {
		"de": "Erweiterte Seiten",
		"fr": "Pages avancées",
		"es": "Páginas avanzadas",
		"it": "Pagine avanzate",
		"pt": "Páginas avançadas",
		"nl": "Geavanceerde pagina’s",
		"pl": "Zaawansowane strony",
	},
	"Custom DNS": {
		"de": "Benutzerdefiniertes DNS",
		"fr": "DNS personnalisé",
		"es": "DNS personalizado",
		"it": "DNS personalizzato",
		"pt": "DNS personalizado",
		"nl": "Aangepaste DNS",
		"pl": "Niestandardowy DNS",
	},
	"External DNS": {
		"de": "Externes DNS",
		"fr": "DNS externe",
		"es": "DNS externo",
		"it": "DNS esterno",
		"pt": "DNS externo",
		"nl": "Externe DNS",
		"pl": "Zewnętrzny DNS",
	},
	"Munin Monitoring": {
		"de": "Munin-Überwachung",
		"fr": "Surveillance Munin",
		"es": "Monitorización Munin",
		"it": "Monitoraggio Munin",
		"pt": "Monitorização Munin",
		"nl": "Munin-monitoring",
		"pl": "Monitoring Munin",
	},
	"Mail": {
		"de": "E-Mail",
		"fr": "Courrier",
		"es": "Correo",
		"it": "Posta",
		"pt": "Correio",
		"nl": "E-mail",
		"pl": "Poczta",
	},
	"Mail & Users": {
		"de": "E-Mail & Benutzer",
		"fr": "Courrier et utilisateurs",
		"es": "Correo y usuarios",
		"it": "Posta e utenti",
		"pt": "Correio e utilizadores",
		"nl": "E-mail en gebruikers",
		"pl": "Poczta i użytkownicy",
	},
	"Instructions": {
		"de": "Anleitung",
		"fr": "Instructions",
		"es": "Instrucciones",
		"it": "Istruzioni",
		"pt": "Instruções",
		"nl": "Instructies",
		"pl": "Instrukcje",
	},
	"Users": {
		"de": "Benutzer",
		"fr": "Utilisateurs",
		"es": "Usuarios",
		"it": "Utenti",
		"pt": "Utilizadores",
		"nl": "Gebruikers",
		"pl": "Użytkownicy",
	},
	"Aliases": {
		"de": "Aliasse",
		"fr": "Alias",
		"es": "Alias",
		"it": "Alias",
		"pt": "Aliás",
		"nl": "Aliassen",
		"pl": "Aliasy",
	},
	"Your Account": {
		"de": "Ihr Konto",
		"fr": "Votre compte",
		"es": "Su cuenta",
		"it": "Il tuo account",
		"pt": "A sua conta",
		"nl": "Uw account",
		"pl": "Twoje konto",
	},
	"Two-Factor Authentication": {
		"de": "Zwei-Faktor-Authentifizierung",
		"fr": "Authentification à deux facteurs",
		"es": "Autenticación en dos pasos",
		"it": "Autenticazione a due fattori",
		"pt": "Autenticação de dois fatores",
		"nl": "Tweefactorauthenticatie",
		"pl": "Uwierzytelnianie dwuskładnikowe",
	},
	"Contacts/Calendar": {
		"de": "Kontakte/Kalender",
		"fr": "Contacts/Calendrier",
		"es": "Contactos/Calendario",
		"it": "Contatti/Calendario",
		"pt": "Contactos/Calendário",
		"nl": "Contacten/Agenda",
		"pl": "Kontakty/Kalendarz",
	},
	"Web": {
		"de": "Web",
		"fr": "Web",
		"es": "Web",
		"it": "Web",
		"pt": "Web",
		"nl": "Web",
		"pl": "WWW",
	},
	"Language": {
		"de": "Sprache",
		"fr": "Langue",
		"es": "Idioma",
		"it": "Lingua",
		"pt": "Idioma",
		"nl": "Taal",
		"pl": "Język",
	},
	"Log out": {
		"de": "Abmelden",
		"fr": "Déconnexion",
		"es": "Cerrar sesión",
		"it": "Esci",
		"pt": "Terminar sessão",
		"nl": "Uitloggen",
		"pl": "Wyloguj",
	},
	'This is <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (agentic fork of Mail-in-a-Box).': {
		"de": 'Dies ist <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (agentischer Fork von Mail-in-a-Box).',
		"fr": 'Ceci est <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (fork agentique de Mail-in-a-Box).',
		"es": 'Esto es <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (fork agentico de Mail-in-a-Box).',
		"it": 'Questo è <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (fork agentico di Mail-in-a-Box).',
		"pt": 'Isto é <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (fork agentico do Mail-in-a-Box).',
		"nl": 'Dit is <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (agentic fork van Mail-in-a-Box).',
		"pl": 'To jest <a href="https://github.com/quantenland-ai/TrixieMail">Trixie Mail</a> (agentyczny fork Mail-in-a-Box).',
	},
	"There are no users on this system! To make an administrative user, log into this machine using SSH (like when you first set it up) and run:": {
		"de": "Es gibt keine Benutzer auf diesem System! Um einen Administrator anzulegen, melden Sie sich per SSH an diesem Rechner an (wie bei der Ersteinrichtung) und führen Sie aus:",
		"fr": "Il n’y a aucun utilisateur sur ce système ! Pour créer un administrateur, connectez-vous à cette machine en SSH (comme lors de l’installation) et exécutez :",
		"es": "¡No hay usuarios en este sistema! Para crear un administrador, inicie sesión en esta máquina por SSH (como en la instalación) y ejecute:",
		"it": "Non ci sono utenti su questo sistema! Per creare un amministratore, accedi a questa macchina via SSH (come durante l’installazione) ed esegui:",
		"pt": "Não existem utilizadores neste sistema! Para criar um administrador, inicie sessão nesta máquina por SSH (como na instalação) e execute:",
		"nl": "Er zijn geen gebruikers op dit systeem! Om een beheerder aan te maken, logt u via SSH in op deze machine (zoals bij de eerste installatie) en voert u uit:",
		"pl": "Na tym systemie nie ma użytkowników! Aby utworzyć administratora, zaloguj się na tę maszynę przez SSH (jak przy pierwszej instalacji) i uruchom:",
	},
	"from your Trixie Mail install directory (e.g. TrixieMail or mailinabox)": {
		"de": "aus Ihrem Trixie Mail-Installationsverzeichnis (z. B. TrixieMail oder mailinabox)",
		"fr": "depuis votre répertoire d’installation Trixie Mail (p. ex. TrixieMail ou mailinabox)",
		"es": "desde el directorio de instalación de Trixie Mail (p. ej. TrixieMail o mailinabox)",
		"it": "dalla directory di installazione di Trixie Mail (ad es. TrixieMail o mailinabox)",
		"pt": "a partir do diretório de instalação do Trixie Mail (p. ex. TrixieMail ou mailinabox)",
		"nl": "vanuit uw Trixie Mail-installatiemap (bijv. TrixieMail of mailinabox)",
		"pl": "z katalogu instalacji Trixie Mail (np. TrixieMail lub mailinabox)",
	},
	"There are no administrative users on this system! To make an administrative user, log into this machine using SSH (like when you first set it up) and run:": {
		"de": "Es gibt keine Administratoren auf diesem System! Um einen Administrator anzulegen, melden Sie sich per SSH an diesem Rechner an (wie bei der Ersteinrichtung) und führen Sie aus:",
		"fr": "Il n’y a aucun administrateur sur ce système ! Pour en créer un, connectez-vous à cette machine en SSH (comme lors de l’installation) et exécutez :",
		"es": "¡No hay usuarios administrativos en este sistema! Para crear uno, inicie sesión en esta máquina por SSH (como en la instalación) y ejecute:",
		"it": "Non ci sono utenti amministratori su questo sistema! Per crearne uno, accedi a questa macchina via SSH (come durante l’installazione) ed esegui:",
		"pt": "Não existem utilizadores administrativos neste sistema! Para criar um, inicie sessão nesta máquina por SSH (como na instalação) e execute:",
		"nl": "Er zijn geen beheerders op dit systeem! Om er een aan te maken, logt u via SSH in op deze machine (zoals bij de eerste installatie) en voert u uit:",
		"pl": "Na tym systemie nie ma użytkowników administracyjnych! Aby utworzyć administratora, zaloguj się na tę maszynę przez SSH (jak przy pierwszej instalacji) i uruchom:",
	},
	"Log in here for your Trixie Mail control panel.": {
		"de": "Melden Sie sich hier am Trixie Mail Control Panel an.",
		"fr": "Connectez-vous ici à votre panneau de contrôle Trixie Mail.",
		"es": "Inicie sesión aquí en el panel de control de Trixie Mail.",
		"it": "Accedi qui al pannello di controllo Trixie Mail.",
		"pt": "Inicie sessão aqui no painel de controlo Trixie Mail.",
		"nl": "Log hier in op uw Trixie Mail-beheerpaneel.",
		"pl": "Zaloguj się tutaj do panelu sterowania Trixie Mail.",
	},
	"Email": {
		"de": "E-Mail",
		"fr": "E-mail",
		"es": "Correo electrónico",
		"it": "E-mail",
		"pt": "E-mail",
		"nl": "E-mail",
		"pl": "E-mail",
	},
	"Password": {
		"de": "Passwort",
		"fr": "Mot de passe",
		"es": "Contraseña",
		"it": "Password",
		"pt": "Palavra-passe",
		"nl": "Wachtwoord",
		"pl": "Hasło",
	},
	"Code": {
		"de": "Code",
		"fr": "Code",
		"es": "Código",
		"it": "Codice",
		"pt": "Código",
		"nl": "Code",
		"pl": "Kod",
	},
	"6-digit code": {
		"de": "6-stelliger Code",
		"fr": "Code à 6 chiffres",
		"es": "Código de 6 dígitos",
		"it": "Codice a 6 cifre",
		"pt": "Código de 6 dígitos",
		"nl": "6-cijferige code",
		"pl": "6-cyfrowy kod",
	},
	"Enter the six-digit code generated by your two factor authentication app.": {
		"de": "Geben Sie den sechsstelligen Code ein, den Ihre Zwei-Faktor-App erzeugt.",
		"fr": "Saisissez le code à six chiffres généré par votre application d’authentification à deux facteurs.",
		"es": "Introduzca el código de seis dígitos generado por su aplicación de autenticación en dos pasos.",
		"it": "Inserisci il codice a sei cifre generato dalla tua app di autenticazione a due fattori.",
		"pt": "Introduza o código de seis dígitos gerado pela aplicação de autenticação de dois fatores.",
		"nl": "Voer de zescijferige code in die door uw tweefactorauthenticatie-app is gegenereerd.",
		"pl": "Wprowadź sześciocyfrowy kod wygenerowany przez aplikację uwierzytelniania dwuskładnikowego.",
	},
	"Remember me": {
		"de": "Angemeldet bleiben",
		"fr": "Se souvenir de moi",
		"es": "Recordarme",
		"it": "Ricordami",
		"pt": "Lembrar-me",
		"nl": "Onthoud mij",
		"pl": "Zapamiętaj mnie",
	},
	"Sign in": {
		"de": "Anmelden",
		"fr": "Connexion",
		"es": "Iniciar sesión",
		"it": "Accedi",
		"pt": "Iniciar sessão",
		"nl": "Inloggen",
		"pl": "Zaloguj się",
	},
	"Welcome to your Trixie Mail control panel.": {
		"de": "Willkommen in Ihrem Trixie Mail Control Panel.",
		"fr": "Bienvenue dans votre panneau de contrôle Trixie Mail.",
		"es": "Bienvenido al panel de control de Trixie Mail.",
		"it": "Benvenuto nel pannello di controllo Trixie Mail.",
		"pt": "Bem-vindo ao painel de controlo Trixie Mail.",
		"nl": "Welkom bij uw Trixie Mail-beheerpaneel.",
		"pl": "Witamy w panelu sterowania Trixie Mail.",
	},
	# Admin notification email subjects (email_messages.py / daily_tasks.sh)
	"Trixie Mail Usage Report": {
		"de": "Trixie Mail Nutzungsbericht",
		"fr": "Rapport d’utilisation Trixie Mail",
		"es": "Informe de uso de Trixie Mail",
		"it": "Rapporto di utilizzo di Trixie Mail",
		"pt": "Relatório de utilização do Trixie Mail",
		"nl": "Trixie Mail gebruiksrapport",
		"pl": "Raport użycia Trixie Mail",
	},
	"Backup Status": {
		"de": "Backup-Status",
		"fr": "État de la sauvegarde",
		"es": "Estado de la copia de seguridad",
		"it": "Stato del backup",
		"pt": "Estado da cópia de segurança",
		"nl": "Back-upstatus",
		"pl": "Status kopii zapasowej",
	},
	"TLS Certificate Provisioning Result": {
		"de": "Ergebnis der TLS-Zertifikatsbereitstellung",
		"fr": "Résultat du provisionnement des certificats TLS",
		"es": "Resultado del aprovisionamiento de certificados TLS",
		"it": "Esito del provisioning dei certificati TLS",
		"pt": "Resultado do aprovisionamento de certificados TLS",
		"nl": "Resultaat van TLS-certificaatvoorziening",
		"pl": "Wynik provisioningu certyfikatów TLS",
	},
	"Status Checks Change Notice": {
		"de": "Hinweis zu Änderungen bei Statusprüfungen",
		"fr": "Avis de changement des contrôles d’état",
		"es": "Aviso de cambio en las comprobaciones de estado",
		"it": "Avviso di modifica dei controlli di stato",
		"pt": "Aviso de alteração das verificações de estado",
		"nl": "Melding over wijzigingen in statuscontroles",
		"pl": "Powiadomienie o zmianach kontroli stanu",
	},
}

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


def load_mt_table():
	"""Merge inline MT dict with optional mt_extra.json (status/API follow-up)."""
	table = {k: dict(v) for k, v in MT.items()}
	if MT_EXTRA_PATH.is_file():
		extra = json.loads(MT_EXTRA_PATH.read_text(encoding="utf-8"))
		for msgid, langs in extra.items():
			if not isinstance(langs, dict):
				continue
			slot = table.setdefault(msgid, {})
			for lang, msgstr in langs.items():
				if msgstr:
					slot[lang] = msgstr
	return table


def main():
	with POT_PATH.open(encoding="utf-8") as f:
		pot = read_po(f)

	mt_table = load_mt_table()

	for lang in LANGS:
		cat = Catalog(
			locale=lang,
			domain="messages",
			header_comment=pot.header_comment,
			project=pot.project,
			version=pot.version,
			copyright_holder=pot.copyright_holder,
			msgid_bugs_address=pot.msgid_bugs_address,
			creation_date=pot.creation_date,
			revision_date="2026-11-26 14:00+0000",
			last_translator="Trixie Mail MT bootstrap <noreply@localhost>",
			language_team=f"{lang}",
			fuzzy=False,
		)
		for message in pot:
			if not message.id:
				continue
			msgid = message.id
			if lang == "en":
				msgstr = msgid if isinstance(msgid, str) else msgid
			else:
				key = msgid if isinstance(msgid, str) else msgid[0]
				msgstr = mt_table.get(key, {}).get(lang, "")
			cat.add(
				msgid,
				string=msgstr,
				locations=message.locations,
				auto_comments=list(message.auto_comments) + (["Status: mt", "Phase: 1"] if lang != "en" else ["Status: source", "Phase: 1"]),
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
		print(f"Wrote {out_path}")


if __name__ == "__main__":
	os.chdir(LOCALE_DIR.parent)
	main()
