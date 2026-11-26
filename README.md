Trixie Mail
===========

**Trixie Mail** (software id **TrixieMail**) is an **agentic fork** of [Mail-in-a-Box](https://github.com/mail-in-a-box/mailinabox) by [@JoshData](https://github.com/JoshData) and [contributors](https://github.com/mail-in-a-box/mailinabox/graphs/contributors). Upstream credit stands: this project builds on that design and codebase.

It remains a one-click mail server (SMTP, IMAP, webmail, contacts, calendar, DNS) on a single machine, with changes aimed at Debian 13 and headless / AI-agent installs.

**This repository:** [https://github.com/quantenland-ai/TrixieMail](https://github.com/quantenland-ai/TrixieMail) (Quantenland AI GmbH / `quantenland-ai`)


What changed in this fork
-------------------------

| Area | This fork |
| --- | --- |
| OS | **Debian 13 (Trixie) only** (not Ubuntu) |
| Product name | **Trixie Mail** / **TrixieMail** |
| Versioning | **YY.MM[.N]** (current **26.11.1**) |
| Headless install | Optional `install.conf` + `--noninteractive` for agents |
| Uninstall | Experimental `setup/uninstall.sh` (package baseline) |
| Stack pins | Newer Nextcloud / PHP / crypto vs upstream Ubuntu 22.04 line |

Runtime paths inherited from Mail-in-a-Box (`/etc/mailinabox.conf`, `/usr/local/lib/mailinabox`, `/usr/local/bin/mailinabox`, systemd unit `mailinabox.service`, etc.) are **kept on purpose** so existing boxes and tooling do not break. Setup also installs a `trixiemail` command alias. See [Runtime paths](#runtime-paths).


Versioning
----------

This fork versions as **YY.MM[.N]** (see the top-level `VERSION` file; current release **26.11.1**), targeting a release about every 1–2 months. Release history is in `CHANGELOG.md`. The control panel, `/admin/system/version` API, and setup banner read `VERSION`. Git tags and `TAG=` in `setup/bootstrap.sh` use a leading `v` (for example `v26.11.1`).


Requirements
------------

* **OS:** Debian 13 (Trixie) only — fresh machine dedicated to mail (installer aborts otherwise)
* **CPU:** x86_64 or i686 (only architectures tested)
* **RAM:** 512 MB minimum (setup refuses less); 768 MB+ recommended to avoid load warnings; 1 GB+ preferred
* **Disk:** enough for the OS plus growing mail/Nextcloud data; if RAM is under 2 GB, setup may create a 1 GB swap file when ≥5 GB free disk is available
* **Network:** public IPv4 (IPv6 optional); outbound TCP port 25 must work (residential ISPs often block it)
* **Hostname / DNS:** a domain you control; suggested hostname `box.<your-domain>`; DNS (A/AAAA/NS) need not resolve before install — point nameserver (or equivalent) records at this box afterward
* **Inbound ports used:** 22 (SSH), 25/465/587 (SMTP), 80/443 (HTTP/HTTPS), 53 TCP/UDP (DNS), 993/995 (IMAP/POP), 4190 (ManageSieve)


Manual install
--------------

On the machine:

```
sudo apt update
sudo apt install -y git
git clone https://github.com/quantenland-ai/TrixieMail
cd TrixieMail
sudo setup/start.sh
```

Install from the `main` branch of this repository. This port sets up a new box; it does not upgrade an older Mail-in-a-Box Ubuntu data directory. Do not use the upstream one-line installer at mailinabox.email — that tracks the Ubuntu release.

Setup asks for:

* Time zone (`tzdata`) — pick the zone you live in
* Admin email address — the domain after `@` must be one you control
* Hostname — keep the suggestion `box.` plus that domain
* Public IP — when the machine cannot detect it; leave IPv6 empty if none
* Password for the first mail account — the prompt does not echo it

When it finishes it prints `Your Trixie Mail is running.` and the control panel URL:

	https://box.example.com/admin

Log in with that email and password. If DNS is not ready yet, use the `https://<ip>/admin` address printed at the end and verify the certificate fingerprint. The control panel lists the nameserver records to set at your registrar.

To change an answer later, run `sudo trixiemail` or `sudo mailinabox` from the install directory (both invoke the same setup).


### Agentic AI

Agents install without a TTY by writing `install.conf`, then running setup with `--noninteractive`. Setup will not prompt; missing required keys abort immediately. Follow this checklist in order.

**1. Ask the user (do not invent or derive silently)**

Collect these before writing any config file:

| Key | Ask | Rules |
| --- | --- | --- |
| `PRIMARY_HOSTNAME` | What FQDN should this box use? | **Must ask.** Explicit FQDN only (suggested `box.<their-domain>`). `auto` is rejected. |
| `EMAIL_ADDR` | What should the first admin mailbox be? | **Must ask.** Never invent `admin@` (or any address) from the hostname. Domain after `@` must be one they control. Becomes control-panel login. |
| `EMAIL_PW` | Generate a password, or use one you provide? | **Must ask.** If generating, show the password once securely (minimum 8 characters). Stored in the config file — protect the file. |
| `TIMEZONE` | What IANA time zone should the box use? | **Must ask** (e.g. `Europe/Berlin`). Do not silently default. Only if the user declines, use `Etc/UTC` and say so. |
| `PUBLIC_IP` | Is `PUBLIC_IP=auto` OK, or what is the public IPv4? | **Must confirm.** `auto` detects on typical VPS/DHCP; otherwise take an explicit address from the VPS panel / ISP. |

Also ask when relevant (defaults apply if omitted):

| Key | Ask | Default if omitted |
| --- | --- | --- |
| `PUBLIC_IPV6` | Public IPv6, if any? | Empty (none). Or `auto` to detect. |
| `STORAGE_USER` | System user that owns mail data? | `user-data` |
| `STORAGE_ROOT` | Directory for mail / Nextcloud data? | `/home/user-data` |
| `SKIP_NETWORK_CHECKS` | Skip Spamhaus / outbound port-25 checks? | unset (checks run). Set to `1` only if the user understands the risk. |

**DNS timing:** The primary hostname and domain do **not** need to resolve (A/AAAA/NS) before installation. Proceed even if DNS is unset; setup uses a self-signed certificate until DNS points here. Glue records, registrar nameservers, and the A/AAAA for `PRIMARY_HOSTNAME` can be configured afterward. (**TODO:** fuller agent-oriented DNS guidance later. Until then, the control panel lists the records to set after install.)

**2. Write `install.conf`**

Config search order (first existing file wins):

1. `--config=/path/to/file` on the command line
2. `$MAILINABOX_CONFIG` environment variable (kept for compatibility)
3. `install.conf` in the repository root (recommended; same directory as `README.md`)
4. `$HOME/mailinabox-install.conf`

```
cp conf/install.conf.example install.conf
# edit install.conf — never commit it (it is gitignored; it holds EMAIL_PW)
```

Or pass an explicit path with `--config=` / `$MAILINABOX_CONFIG`. See `conf/install.conf.example` for a commented template.

**3. Run noninteractive setup**

```
sudo setup/start.sh --noninteractive
```

Or: `sudo setup/start.sh --noninteractive --config=/path/to/install.conf`

**4. Report back**

After success, tell the user: admin email, password (if you generated it — show once), control panel URL (`https://<PRIMARY_HOSTNAME>/admin` or the `https://<ip>/admin` URL printed at the end), and that DNS (glue / registrar NS / A record) still needs to be set — see the control panel System status / DNS pages. Reminder: hostname need not have resolved before install.

**Behavior:**

* No config file → interactive prompts (unchanged default).
* Complete `install.conf` (all required keys set) → setup skips prompts even without the flag; still prefer `--noninteractive` so agents fail loudly if a key is missing.
* `--noninteractive` / `--headless` with incomplete config → exit with an error (does not hang on dialog/`getpass`).
* TLS / Let's Encrypt: unchanged from interactive install — setup auto-agrees to the LE subscriber agreement and uses a self-signed certificate until DNS for `PRIMARY_HOSTNAME` points at this box; public LE certs come after that.


Uninstall
---------

**Experimental.** The uninstaller is new tooling: test on a disposable machine before relying on it for a production box.

Setup records a package baseline early in install at `$STORAGE_ROOT/installer/dpkg-selections-baseline.txt` (normally `/home/user-data/installer/...`). Uninstall uses that baseline to purge packages the installer added, and also reverses other side effects (systemd units, cron, nginx fragments, fail2ban jails, `/usr/local/lib` trees, and so on).

From the repository root:

```
sudo setup/uninstall.sh
```

Confirm with `YES`, or pass `--yes` for non-interactive use. **Mail and other data under `/home/user-data` are kept by default.** To delete that data as well:

```
sudo setup/uninstall.sh --yes --purge-data
```

Use `--dry-run` to print actions without changing the system.

If the box was installed before baseline capture existed, uninstall falls back to a curated package list from `setup/*.sh` and may leave some installer-pulled dependencies behind. On a clean machine (or after uninstall), you can record a baseline for the next install with:

```
sudo setup/uninstall.sh --record-baseline
```

After uninstall, review `ufw status` and `/etc/resolv.conf`. Prefer a fresh OS image for a completely clean slate; otherwise keep `/home/user-data` and run `sudo setup/start.sh` again to reinstall on top of existing data.


Runtime paths
-------------

These Mail-in-a-Box paths are **unchanged** in Trixie Mail (compatibility):

| Path / name | Role |
| --- | --- |
| `/etc/mailinabox.conf` | Install settings |
| `/usr/local/lib/mailinabox/` | Management code + venv |
| `/usr/local/bin/mailinabox` | Re-run setup |
| `/usr/local/bin/trixiemail` | Same as `mailinabox` (alias) |
| `/var/lib/mailinabox/` | API key and related state |
| `mailinabox.service` | Management daemon unit |
| `$HOME/mailinabox` | Directory used by `setup/bootstrap.sh` when cloning |
| `$STORAGE_ROOT/mailinabox.version` | Migration marker |

Display name in the UI and docs is **Trixie Mail**; the software id is **TrixieMail**.


Compared with the original
--------------------------

The original column is what [mail-in-a-box/mailinabox](https://github.com/mail-in-a-box/mailinabox) `master` installs today. The fork column is what this repository installs on Debian 13.

| Software | Original Mail-in-a-Box | Trixie Mail |
| --- | --- | --- |
| Operating system | Ubuntu 22.04 LTS | Debian 13 (Trixie) only |
| PHP | 8.0 | 8.4 |
| Nextcloud | 27.1.11 | 35.0.2 |
| Contacts | 5.5.4 | 8.9.5 |
| Calendar | 4.7.20 | 6.6.5 |
| user_external | 3.4.0 | 4.0.0 |
| Roundcube | 1.6.20 | 1.6.20 |
| Roundcube CardDAV | 4.4.3 | 4.4.3 |
| Z-Push | 2.7.7 | 2.7.7 |
| cryptography | 37.0.2 | 50.0.2 |
| Admin UI jQuery | 2.2.4 | 2.2.4 |
| Admin UI Bootstrap | 3.4.1 | 3.4.1 |
| Dovecot | 2.3, from Ubuntu | 2.4, from Debian |
| Postfix, Nginx, SpamAssassin, NSD, BIND, Certbot, fail2ban | Ubuntu 22.04 packages | Debian 13 packages |
| Spam training when mail is moved to Spam | dovecot-antispam | Not installed. Debian 13 has no Dovecot 2.4 build of that plugin |

Roundcube, Z-Push, jQuery, and Bootstrap are the same pins as the original. Nextcloud, its apps, PHP, and the cryptography library are the ones this fork moves forward. This fork does not install on Ubuntu.

* * *

Our goals are to:

* Make deploying a good mail server easy.
* Promote [decentralization](http://redecentralize.org/), innovation, and privacy on the web.
* Have automated, auditable, and [idempotent](https://web.archive.org/web/20190518072631/https://sharknet.us/2014/02/01/automated-configuration-management-challenges-with-idempotency/) configuration.
* Support headless / agent-driven installs without sacrificing explicit user consent for identity and secrets.
* **Not** make a totally unhackable, NSA-proof server.
* **Not** make something customizable by power users.

Additionally, this project has a [Code of Conduct](CODE_OF_CONDUCT.md), which supersedes the goals above. Please review it when joining our community.


In The Box
----------

Trixie Mail turns a fresh Debian 13 (Trixie) 64-bit machine into a working mail server by installing and configuring various components.

It is a one-click email appliance. There are no user-configurable setup options beyond the few install questions (or `install.conf`). It "just works."

The components installed are:

* SMTP ([postfix](http://www.postfix.org/)), IMAP ([Dovecot](http://dovecot.org/)), CardDAV/CalDAV ([Nextcloud](https://nextcloud.com/)), and Exchange ActiveSync ([z-push](http://z-push.org/)) servers
* Webmail ([Roundcube](http://roundcube.net/)), mail filter rules (thanks to Roundcube and Dovecot), and email client autoconfig settings (served by [nginx](http://nginx.org/))
* Spam filtering ([spamassassin](https://spamassassin.apache.org/)) and optional greylisting ([postgrey](http://postgrey.schweikert.ch/), off by default)
* DNS ([nsd4](https://www.nlnetlabs.nl/projects/nsd/)) with [SPF](https://en.wikipedia.org/wiki/Sender_Policy_Framework), DKIM ([OpenDKIM](http://www.opendkim.org/)), [DMARC](https://en.wikipedia.org/wiki/DMARC), [DNSSEC](https://en.wikipedia.org/wiki/DNSSEC), [DANE TLSA](https://en.wikipedia.org/wiki/DNS-based_Authentication_of_Named_Entities), [MTA-STS](https://tools.ietf.org/html/rfc8461), and [SSHFP](https://tools.ietf.org/html/rfc4255) policy records automatically set
* TLS certificates are automatically provisioned using [Let's Encrypt](https://letsencrypt.org/) for protecting https and all of the other services on the box
* Backups ([duplicity](http://duplicity.nongnu.org/)), firewall ([ufw](https://launchpad.net/ufw)), intrusion protection ([fail2ban](http://www.fail2ban.org/wiki/index.php/Main_Page)), and basic system monitoring ([munin](http://munin-monitoring.org/))

It also includes system management tools:

* Comprehensive health monitoring that checks each day that services are running, ports are open, TLS certificates are valid, and DNS records are correct
* A control panel for adding/removing mail users, aliases, custom DNS records, configuring backups, etc.
* An API for all of the actions on the control panel

Internationalized domain names are supported and configured easily (but SMTPUTF8 is not supported, unfortunately).

It also supports static website hosting since the box is serving HTTPS anyway. (To serve a website for your domains elsewhere, just add a custom DNS "A" record in your Trixie Mail control panel to point domains to another server.)

For more information on privacy, see the [security details page](security.md).

For help with **upstream** Mail-in-a-Box (Ubuntu), use the [discussion forum](https://discourse.mailinabox.email/). For this fork, open an issue on [quantenland-ai/TrixieMail](https://github.com/quantenland-ai/TrixieMail).

Note that while we want everything to "just work," we can't control the rest of the Internet. Other mail services might block or spam-filter email sent from your box. This is a challenge faced by everyone who runs their own mail server.


Contributing and Development
----------------------------

Trixie Mail is an open source project. Your contributions and pull requests are welcome. See [CONTRIBUTING](CONTRIBUTING.md) to get started.


The Acknowledgements
--------------------

Upstream Mail-in-a-Box was inspired in part by the ["NSA-proof your email in 2 hours"](http://sealedabstract.com/code/nsa-proof-your-e-mail-in-2-hours/) blog post by Drew Crawford, [Sovereign](https://github.com/sovereign/sovereign) by Alex Payne, and conversations with <a href="https://twitter.com/shevski" target="_blank">@shevski</a>, <a href="https://github.com/konklone" target="_blank">@konklone</a>, and <a href="https://github.com/gregelin" target="_blank">@GregElin</a>.

Mail-in-a-Box (and thus this fork) is similar to [iRedMail](http://www.iredmail.org/) and [Modoboa](https://github.com/tonioo/modoboa).


The History
-----------

* In 2007 Josh Data wrote a relatively popular Mozilla Thunderbird extension that added client-side SPF and DKIM checks to mail to warn users about possible phishing: [add-on page](https://addons.mozilla.org/en-us/thunderbird/addon/sender-verification-anti-phish/), [source](https://github.com/JoshData/thunderbird-spf).
* In August 2013 Mail-in-a-Box began by combining that mail server configuration with the setup in ["NSA-proof your email in 2 hours"](http://sealedabstract.com/code/nsa-proof-your-e-mail-in-2-hours/) and making the setup steps reproducible with bash scripts.
* Mail-in-a-Box was a semifinalist in the 2014 [Knight News Challenge](https://www.newschallenge.org/challenge/2014/submissions/mail-in-a-box), but it was not selected as a winner.
* Mail-in-a-Box hit the front page of Hacker News in [April](https://news.ycombinator.com/item?id=7634514) 2014, [September](https://news.ycombinator.com/item?id=8276171) 2014, [May](https://news.ycombinator.com/item?id=9624267) 2015, and [November](https://news.ycombinator.com/item?id=13050500) 2016.
* FastCompany mentioned Mail-in-a-Box in a [roundup of privacy projects](http://www.fastcompany.com/3047645/your-own-private-cloud) on June 26, 2015.
* This **Trixie Mail** fork ports the stack to Debian 13 (Trixie), adds headless/`install.conf` agent installs, an experimental uninstaller, and is maintained under Quantenland AI as **TrixieMail**.
