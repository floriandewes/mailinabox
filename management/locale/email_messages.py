# Seed catalog for admin notification email subjects (English msgids).
# daily_tasks.sh passes these as argv to email_administrator.py, which
# translates them with the box-wide UI locale. Keep "Trixiemail" untranslated.

def _(s):
	return s


_("Trixiemail Usage Report")
_("Backup Status")
_("TLS Certificate Provisioning Result")
_("Status Checks Change Notice")
