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

# custom-dns.html JS
_("delete")
_("Secondary DNS")
_("Custom DNS")
_("Custom DNS (Error)")

# external-dns.html JS
_("Download Zonefile")
_("Download Zonefile (Error)")

# web.html JS
_("Change")
_("Nothing changed.")
_("Web Update")
_("Change Root Directory for %(domain)s")
_("You can change the static directory for <tt>%(domain)s</tt> to:")
_("First create this directory on the server. Then click Update to scan for the directory and update web settings.")
_("Update")

# mfa.html JS
_("QR code, scan this in your authenticator app")
_("Secret: %(secret)s")
_(" on device '%(label)s'")

# mail-guide.html JS
_("Greylisting is on. Mail from a new sender can be delayed by at least 3 minutes.")
_("Greylisting is off. Incoming mail is accepted on the first connection.")
_("Turn off greylisting")
_("Turn on greylisting")

# system-status.html
_("Enable")
_("Disable")
_("show more")
_("Summary: ")
_("All %(num)s %(symbol)s OK")
_("%(num)s %(symbol)s OK, ")
_("%(num)s %(symbol)s Error, ")
_("%(num)s %(symbol)s Warning")
_("Reboot")
_("This will reboot your Trixie Mail <code>%(hostname)s</code>.")
_("Until the machine is fully restarted, your users will not be able to send and receive email, and you will not be able to connect to this control panel or with SSH. The reboot cannot be cancelled.")
_("Reboot Now")
_("Please reload this page after a minute or so.")
_("The reboot command said:")

# system-backup.html
_("bytes")
_("KB")
_("MB")
_("GB")
_("TB")
_("Backup Error")
_("Backups are turned off.")
_("No backups have been made yet.")
_("%(delta)s ago")
_("full")
_("increment")
_("unknown")
_("Backup configuration")

# ssl.html
_("(select)")
_("Install Certificate")
_("Replace Certificate")
_("TLS Certificate Installation")
_("Certificate has been installed. Check that you have no connection problems to the domain.")
_("TLS Certificate Provisioning")
_("There were no domain names to provision certificates for.")
_("The TLS certificate was provisioned and installed.")
_("Log:")

# users.html
_("Mailbox size is unkown")
_("unlimited")
_("Remove Privilege")
_("remove privilege")
_("Add Privilege")
_("make <span class='name'>%(privilege)s</span>")
_("Add User")
_("Set Password")
_("<p class='text-danger'>If you change your own password, you will be logged out of this control panel and will need to log in again.</p>")
_("<p>Set a new password for <b>%(email)s</b>?</p> <p><label for='users_set_password_pw' style='display: block; font-weight: normal'>New Password:</label><input type='password' id='users_set_password_pw'></p><p><small>Passwords must be at least eight characters and may not contain spaces.</small>%(yourpw)s</p>")
_("Set Quota")
_("<p>Set quota for <b>%(email)s</b>?</p><p><label for='users_set_quota' style='display: block; font-weight: normal'>Quota:</label><input type='text' id='users_set_quota' value='%(quota)s'></p><p><small>Quotas may not contain any spaces or commas.  Suffixes of G (gigabytes) and M (megabytes) are allowed.</small></p><p><small>For unlimited storage enter 0 (zero)</small></p>")
_("Archive User")
_("You cannot archive your own account.")
_("<p>Are you sure you want to archive <b>%(email)s</b>?</p> <p>The user's mailboxes will not be deleted (you can do that later), but the user will no longer be able to log into any services on this machine.</p>")
_("Archive")
_("Remove User")
_("Modify Privileges")
_("You cannot remove the admin privilege from yourself.")
_("<p>Are you sure you want to remove the %(privilege)s privilege for <b>%(email)s</b>?</p>")
_("Remove")
_("<p>Are you sure you want to add the %(privilege)s privilege for <b>%(email)s</b>?</p>")
_("Add")
_("Random Password")
_("<p>Here, try this:</p> <p><code style='font-size: 110%'>%(password)s</code></p>")

# aliases.html
_("you@yourdomain.com (incoming email address)")
_("one address per line or separated by commas")
_("@yourdomain.com (incoming catch-all domain)")
_("@otherdomain.com (forward to other domain)")
_("Add Alias")
_("Update Alias")
_("You did not enter any permitted senders.")
_("Update")
_("Remove Alias")
_("Remove %(address)s?")
