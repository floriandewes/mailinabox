# Seed catalog for client-side strings used via t() / tn() in control-panel JS.
# Keep "Trixie Mail" untranslated in every language.
# pybabel extract picks these up so they land in messages.pot / JSON catalogs.

def _(s):
	return s


# Shared chrome (index.html)
_("Loading...")
_("Error")
_("Something went wrong, sorry.")
_("OK")
_("Cancel")
_("Yes")
_("Close Dialog")
_("Toggle navigation")

# Login panel JS
_("Login Failed")
_("Enter your email address.")
_("Enter your email password.")
_("Incorrect two factor authentication token.")
_("You are not an administrator on this system.")
