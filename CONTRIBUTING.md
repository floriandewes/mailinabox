Contributing
============

Trixie Mail is an open source project (an agentic fork of [Mail-in-a-Box](https://github.com/mail-in-a-box/mailinabox)). Your contributions and pull requests are welcome.

For developers
--------------

To start developing Trixie Mail, [clone this repository](https://github.com/quantenland-ai/TrixieMail) and familiarize yourself with the code.

    $ git clone https://github.com/quantenland-ai/TrixieMail
    $ cd TrixieMail

To start a local development environment, we recommend using [Vagrant](https://www.vagrantup.com/) to create a virtual machine, and then you install Trixie Mail into the VM. Install Vagrant and VirtualBox, and if you are on Windows [also Rsync](https://github.com/nilgradisnik/vagrant-plugin-rsync).

With Vagrant set up, the following should boot up Trixie Mail inside a virtual machine:

    $ vagrant up --provision

(You may need to `export DEFAULT_PUBLIC_IP=192.168.56.4` beforehand or edit the Vagrantfile.)

After a while, Trixie Mail will be available at `192.168.56.4` (unless you changed that in your `Vagrantfile`). To be able to use the web-based bits, we recommend to add a hostname to your `hosts` file:

    192.168.56.4 meow.mailinabox.lan

(And then visit `https://meow.mailinabox.lan/admin`.)

Your working copy of Trixie Mail will be mounted inside your VM at `/vagrant`. Any change you make locally will appear inside your VM automatically.

To debug the Python-based management daemon, which serves the control panel API, you'll need to first install Trixie Mail and then:

    $ sudo service mailinabox stop
    $ sudo /usr/local/lib/mailinabox/env/bin/python management/daemon.py

And for testing:

    $ sudo NO_NETWORK_TESTING=1 tests/run.sh

Please see the [Code of Conduct](CODE_OF_CONDUCT.md).

Testing
-------

Trixie Mail needs more tests. If you're still looking for a way to help out, writing and contributing tests would be a great start!
