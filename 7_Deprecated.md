Deprecated
=======================================

Customize Linux image using Puppet
=============================================================================================================

You could use a Linux image from Turnkey or from another vendor that
already contains applications you need. Anyhow, here’s the quick guide
how to install Wordpress on plain Ubuntu server image using Puppet as a
configuration management tool. For the sake of simplicity we’re not
using an external volume to store data into nor we are using an external
database in this example.

Launching a plain Ubuntu Linux image
-----------------------------------------------------------------------------------------------------------------

Login to the OpenStack with your credentials and go to **Images &
Snapshots** tab. Select the plain Ubuntu image to be launched from the
list of existing images. If plain Ubuntu image is not available then you
can create a new one according to instructions in [Create Linux
image](3_OpenStackIaaSplatform.md#create-linux-image). When you are launching an image, you have
to provide following parameters and then wait for it to be loaded.

    - Details: The name for the new instance and other parameters
    - Access & Security: SSH keypair and security group
    - Networking: Select the network to be used
    - Post-Creation: You can define the customization script that runs after you instance launches

Making the instance accessible
-----------------------------------------------------------------------------------------------------

In order to access launched instance with SSH, you must associate the
instance with IP and configure a security group. If there are no IPs
available, then you can allocate more IPs from the pool assuming the
pool has still some left.

The security group rules for your instance should be configured so that
all access is denied other than SSH (typically port 22) access from your
local IP address. Then when you have your application configured
properly you can reconfigure security group rules according to your
application needs.

Image vendors have typically set the default username and password for
SSH connections but you can also use the SSH key you selected during
instance definition because the key is injected into the instance.

Finally is should be possible to configure and customize your instance.

Customizing the image by installing new software
-----------------------------------------------------------------------------------------------------------------------------------------

SSH into the instance and install Puppet configuration management tool
from puppetlabs repository as a root user

    # wget http://apt.puppetlabs.com/puppetlabs-release-precise.deb
    # dpkg -i puppetlabs-release-precise.deb
    # apt-get update
    # apt-get install puppet

Then you can setup Wordpress using Puppet

1.  Install Wordpress puppet module

<!-- -->

    # puppet module install jonhadfield/wordpress
    # puppet apply --noop /etc/puppet/modules/wordpress/tests/init.pp
    # puppet apply /etc/puppet/modules/wordpress/tests/init.pp

1.  If everything went well, you have your Wordpress instance up and
    running at your desired IP address. Nobody is able to access it yet,
    since the security group rules prevent it. You should modify the
    security group rules to allow http (port 80) from your local IP.
    After this you are able to finalize the Wordpress installation with
    your web browser at http://IP/wp-login.php

2.  Finally after you have finalized Wordpress installation, you can
    open it for the rest of the world by modifying the security group
    rules to allow everybody to access port 80. After this the Wordpress
    is accessible to whole world at http://IP/.

Create a Linux image
---------------------------------------------------------------------------------

After you have your customized Linux image ready you can make a snapshot
out of it in order to launch more instances of it later. Follow
instructions in [Take a snapshot of your Linux
instance](3_OpenStackIaaSplatform.md#take-a-snapshot-of-the-instance)


WordPress (Salt version)
=============================================================================

This document shows how to get a WordPress instance working in an
OpenStack instance. There are a number of methods of accomplishing the
same thing with varying degrees of difficulty.

1.  [The supereasy, superfast way](#the-supereasy-superfast-way). (Let's
    use pre-provided components)
2.  [The supereasy, superfast way with a
    twist](#the-supereasy-superfast-way-with-a-twist). (Let's use
    pre-provided components)
3.  [The supereasy, not so fast way](#the-supereasy-not-so-fast-way).
    (I'll use provided components but I want my own infrastructure)
4.  [The not so easy anymore way](#the-not-so-easy-anymore-way). (What's
    under the hood? I want to replicate it)
5.  [The masterless way](#the-masterless-way). (I don't care for salt
    master, just give me wordpress)
6.  [The nitty gritty details](#the-nitty-gritty-details). (How did we
    come this far?)

**Note:** For the purposes of this guide, we assume that you know how to
[set up a network on OpenStack](3_OpenStackIaaSplatform.md#configuring-a-subnet)
and have already done so. We'll further assume that this network is
called "Salt" and has a subnet of 192.168.0.0/24.

The supereasy superfast way
--------------------------------------------------------------------------------------

**This method requires being a member of the "digile" project on
[OpenStack](https://cloud.forgeservicelab.fi) and being connected to the Digile
network.**
 After logging into OpenStack, select the "Project" tab, make sure your
current project is "digile" and under the Manage Compute section select
"Images & Snapshots"
 On the Images & Snapshots panel, under the Image Snapshots section,
there is a snapshot named "salt-minion-with-master-knowledge", we're
going to launch an instance of this snapshot.

1.  Click the "Launch" button on the right hand side of the snapshot
    list entry.
2.  A configuration wizard pops up; enter a name for this instance, e.g.
    'Wordpress'.
3.  Select the "Access & Security" tab. Make sure there is a keypair
    selected and the security groups 'default' and 'digile' are enabled.
4.  Select the "Networking" tab and click on the '+' sign beside the
    available network named "Salt".
5.  Click "Launch".
6.  You'll be taken to the "Instances" view, click the "Associate
    Floating IP" button.
7.  On the modal dialog, select an available IP and click "Associate".
8.  Log into the newly created instance via SSH into the associated IP.
9.  Run the following command:

    ` sudo salt-call state.sls wordpress`

10. Point your browser to the associated IP. You should be landing on
    Wordpress' configuration page.

The supereasy superfast way with a twist
----------------------------------------------------------------------------------------------------------------

This method is basically the same as the one above but with the benefit
of being able to use blank images with no need for access to pre-built
snapshots.
 **This method assumes that you know how to [create a linux
image](3_OpenStackIaaSplatform.md#create-linux-image) and that you have provisioned a blank ubuntu
image for your project.**
 After logging into OpenStack, select the "Project" tab and under the
Manage Compute section select "Instances"

1.  Click on the "Launch Instance" button.
2.  On the modal dialog, select the prepared blank ubuntu image and give
    the instance a name, e.g. 'Wordpress'
3.  Select the "Access & Security" tab. Make sure there is a keypair
    selected and the appropriate security groups are enabled.
4.  Select the "Networking" tab and click on the '+' sign beside the
    available network named "Salt".
5.  Click "Launch".
6.  You'll be taken to the "Instances" view, click the "Associate
    Floating IP" button.
7.  On the modal dialog, select an available IP and click "Associate".
8.  Log into the newly created instance via SSH into the associated IP.
9.  Run the following commands:

    ` wget -O - http://bootstrap.saltstack.org | sudo sh sudo salt-call --master 193.166.24.110 state.sls wordpress`

10. Point your browser to the associated IP. You should be landing on
    Wordpress' configuration page.

The supereasy not so fast way
------------------------------------------------------------------------------------------

**This method requires that you have access to the Instance Snapshot
"Salt Master (with salt hack)".**
 After logging into OpenStack, select the "Project" tab and under the
Manage Compute section select "Images & Snapshots"
 On the Images & Snapshots panel, under the Image Snapshots section,
there is a snapshot named "Salt Master (with salt hack)", we're going to
launch an instance of this snapshot.

1.  Click the "Launch" button on the right hand side of the snapshot
    list entry.
2.  A configuration wizard pops up; enter a name for this instance, e.g.
    'Salt Master'.
3.  Select the "Access & Security" tab. Make sure there is a keypair
    selected and the appropriate security groups are enabled.
4.  Select the "Networking" tab and click on the '+' sign beside the
    available network named "Salt".
5.  Click "Launch".

Your very own, pre-configured salt master is running on your Salt
network. Now we'll prepare a salt minion to host the Wordpress service.
We assume you know how to [create a linux image](3_OpenStackIaaSplatform.md#create-linux-image)
and that you have provisioned a blank ubuntu image for your project.

1.  Click on the "Launch Instance" button.
2.  On the modal dialog, select the prepared blank ubuntu image and give
    the instance a name, e.g. 'Wordpress'
3.  Select the "Access & Security" tab. Make sure there is a keypair
    selected and the appropriate security groups are enabled.
4.  Select the "Networking" tab and click on the '+' sign beside the
    available network named "Salt".
5.  Click "Launch".
6.  You'll be taken to the "Instances" view, click the "Associate
    Floating IP" button.
7.  On the modal dialog, select an available IP and click "Associate".
8.  Take note of the IP for your Salt Master instance. For the purposes
    of this guide let's assume it's 192.168.0.2
9.  Log into the newly created instance via SSH into the associated IP.
10. Run the following commands:

        wget -O - http://bootstrap.saltstack.org | sudo sh
        sudo salt-call --master 192.168.0.2 state.sls wordpress

11. Point your browser to the associated IP. You should be landing on
    Wordpress' configuration page.

The not so easy anymore way
-------------------------------------------------------------------------------------

This method will walk you through the process of setting up a true salt
master/minion infrastructure from scratch, the configuration of the
nodes and running of the states to arrive at a working instance of
Wordpress.
 **This method requires that you have at least read access to Forge's
gitlab.**
 For this section we're going to assume that your project on OpenStack
has a blank ubuntu image available and that two instances of it have
been launched. We'll call these images "Master" and "Minion"
respectively. We'll also take for granted that a properly configured
network exists on the project, that the two instances are properly
attached to it and that the security groups are on a suitable working
state.

1.  Log into the Master instance. To install the salt master service run
    the following command:

        wget -O - http://bootstrap.saltstack.org | sudo sh -s -- -M -N

2.  Log into the Minion instance and install the salt minion service by
    running the following command:

        wget -O - http://bootstrap.saltstack.org | sudo sh

3.  The minion needs to know the location of the master, this is the IP
    within the local "Salt" subnet of the Master instance, let's say
    it's 192.168.0.2, you'll need to add this bit of info to the
    minion's configuration file.

    1.  Edit the minion's configuration file:

            sudo vi /etc/salt/minion  

        On the second paragraph of this file you'll see information
        about setting the location of the master, you'll be fine by
        adding `master: 192.168.0.2` right below this paragraph.

    2.  Restart the minion service:

            sudo service salt-minion restart  

4.  The rest of the work will take place on the Master instance, log on
    to it. By now, your minion would have generated a ssl key and
    submitted it to the master for verification, to accept it run:

        sudo salt-key -A

    The utility will present you with any yet unaccepted keys on the
    master, which by now should be the one from the minion, identified
    by the minion's hostname, follow the on-screen instructions.

5.  Once you accept the minion's key, the master should be able to
    communicate with the minion. You can verify this by running the
    following:

        sudo salt '*' test.ping

6.  The master and minion can now communicate with each other, but there
    are no state configurations on the master so far. Let's get hold of
    the wordpress state.

    1.  First we need to provide some formulas that our state will
        depend on, we'll get these from the public saltstack formulas
        github repositories. To let the master know about this we need
        to edit its configuration file.

            sudo vi /etc/salt/master

        You need to search for the line containing `fileserver_backend`,
        once you find it edit the file with the following lines:

            fileserver_backend:
            - roots
            - git

        This instructs the master to first search for states within its
        local filesystem, then use the git backend. Now find the line
        containing `gitfs_remotes` and edit the file with the following
        lines:

            gitfs_remotes:
            - git://github.com/saltstack-formulas/apache-formula.git
            - git://github.com/saltstack-formulas/mysql-formula.git
            - git://github.com/saltstack-formulas/php-formula.git
            - git://github.com/saltstack-formulas/apt-formula.git

    2.  To use git as a backend, the salt master needs python's git
        module, install it by running:

            sudo apt-get update
            sudo apt-get install python-git

    3.  We now have access to the dependencies for our state, let's get
        hold of the pre-written state available on FORGE's gitlab and
        place it where salt expects it.

            GIT_SSL_NO_VERIFY=true git clone https://git.forgeservicelab.fi/jrodrigu/wordpress-formula.git
            sudo mkdir /srv/salt
            sudo mv wordpress-formula/wordpress /srv/salt

        That will take care of the state, now we can get a sample pillar
        that will configure apache for our needs.

            GIT_SSL_NO_VERIFY=true git clone https://git.forgeservicelab.fi/jrodrigu/salt-pillars.git
            sudo mkdir /srv/pillar
            sudo cp -R salt-pillars/* /srv/pillar

7.  At this point, the Master instance is configured to know about the
    state that will configure wordpress and its dependencies, but it's
    not aware of them yet, we need to restart the service

        sudo service salt-master restart

8.  Now that the Master knows about the wordpress state and its
    dependencies, we can tell the Minion to set itself up to that state
    template, directly from the Master, by running:

        sudo salt '*' state.sls wordpress

    Note that the previous command has a target of `'*'` and therefore
    will target all minions on the infrastructure. This works for this
    particular scenario because there is only one minion. If there were
    any more all of them will get set to the wordpress state and
    serve wordpress. Targeting is out of the scope of this guide.

9.  At this point you should be able to point your browser to the
    Minion's associated IP and land on Wordpress' initial
    configuration page.

The masterless way
-------------------------------------------------------------------

This section explains how to get wordpress into an instance, using Salt
infrastructure but without the need for a salt master node, we assume
you have launched a blank ubuntu instance, associated a floating IP to
it and that you're logged in, now let's get started.

1.  The first thing you'll need is to get your salt minion service
    installed:

        wget -O - http://bootstrap.saltstack.org | sudo sh

2.  You're going to need git to continue, so let's get that as well:

        sudo apt-get install git

3.  With git installed we can proceed to get useful files off of gitlab
    but first we need to [generate some ssh keys and upload them to
    gitlab](2_Userguides.md#ssh-access). It is
    **very important** to generate the keys as the root user; salt runs
    as root and won't be able to access gitlab if the key pair belongs
    to any other user.
    
     Once the keypair is generated, we can get our masterless salt
    formula and place it where salt expects it:

        sudo git clone ssh://gitlab@git.forgeservicelab.fi:10022/jrodrigu/masterless-formulas.git
        sudo mkdir /srv/salt
        sudo ln -s `pwd`/masterless-formulas/ml-wordpress /srv/salt/ml-wordpress

4.  The wordpress formula requires a pillar file, there are two ways of
    going about this:

    1.  You could grab the pillar from gitlab and place it where gitlab
        expects it:

            sudo git clone ssh://gitlab@git.forgeservicelab.fi:10022/jrodrigu/salt-pillars.git
            sudo ln -s `pwd`/salt-pillars /srv/pillar

    2.  Or you can create your pillar tree yourself. For that, you'll
        need to create the file `/srv/pillar/top.sls` with the following
        contents:

            base:
              '*':
                - wordpress-apache

        And then the file `/srv/pillar/wordpress-apache/init.sls` with
        contents similar to the following:

            apache:
              sites:
                wordpress.forgeservicelab.fi: # You will most likely want to change this to your own domain name.
                  # This server alias allows this vhost to listen as the default
                  ServerAlias: _
                  DocumentRoot: /opt/wordpress
                  DirectoryIndex: index.php

        Whichever route you choose, you should edit the
        `/srv/pillar/wordpress-apache/init.sls` file to suit your needs.

5.  And that completes the list of prerequisites, all you need to do
    know is let salt do the hard work:

        sudo salt-call --local state.sls ml-wordpress

6.  Navigate to the instance's floating IP, wordpress' installation page
    should be waiting for you there.

The nitty gritty details
-------------------------------------------------------------------------------

This section builds on the previous walkthrough. It does not provide a
guide to set up a working environment but rather dots the Is and crosses
the Ts from the above section to explain how the actual salt master on
the FORGE project was further configured. We will discuss here both the
configuration changes made on the above setup as well as the salt
formula developed for this state.

### Configuration changes

The working FORGE salt master hosts no salt formulas whatsoever, instead
these files are hosted on FORGE's gitlab (the same location we used on
the walkthrough above). The difference is that FORGE's salt master is
configured to poll FORGE's gitlab directly rather than copy them onto
the local filesystem, although the master does keep an internal cache of
the git repositories, but that is salt internals and out of the scope of
this document.
 Salt is capable of using git as a backend for both states and pillars.
Adding the FORGE's state repository is trivial and involves just adding
its URI to the list of gitfs\_remotes, in this case

    - git+ssh://gitlab@git.forgeservicelab.fi:10022/jrodrigu/wordpress-formula.git

Note that, because we're using the ssh transport, the master must have
generated an ssh key pair for the root user and the public key must be
present on gitlab.

[Using git as a pillar
backend](http://docs.saltstack.com/ref/pillar/all/salt.pillar.git_pillar.html#module-salt.pillar.git_pillar)
is not much more complicated in theory but we run into a few pitfalls.
Because both the salt code and python's git module are fairly young,
there is no straightforward way of ignoring SSL warnings when connecting
to git and manually setting git's global flag to ignore ssl verification
didn't seem to work either. To work around the issue we had to modify
salt's code itself to allocate a new flag to enable or disable ssl
verification, this change is [pending a pull
request](https://github.com/saltstack/salt/pull/8936) on salt's project
on github. With this change in place, the master was able to get pillar
info from our gitlab repository and so, it no longer needs to store this
information locally.

FORGE's server is also configured in "open mode" and "auto accept" mode.
This breaks salt's security structure but allows us to provide state
configuration to newly created minions without the need for active
configuration thus working as an open configuration service.

### The formula

Let's dissect the wordpress salt state section by section:

    include:
      - apache.rewrite
      - apache.vhosts.standard
      - php
      - php.mysql
      - mysql.server
      - mysql.python

This is the dependencies section. In it we configure all the components
that are needed to run Wordpress.

-   apache.rewrite ensures that the apache webserver is installed and
    running with mod\_rewrite enabled.
-   apache.vhosts.standard creates a baseline configuration for apache
    to serve wordpress, this is highly dependent on hardcoded values
    that should be moved to the pillar infrastructure.
-   php ensures php5 is installed on the system
-   php.mysql installs php mysql transport
-   mysql.server ensures MySQL server version 5 is installed on the
    system
-   mysql.python installs the python transport for mysql, this is needed
    for mysql configuration in later sections of this state file.

<!-- -->

    disable-default:
      cmd:
        - run
        - name: "/usr/sbin/a2dissite default"
        - requires:
          - pkg: apache
      service:
        - running
        - name: apache2
        - restart: True
        - watch:
          - cmd: disable-default

Apache ships with a default virtual host that works as a fallback
catchall. We want our wordpress service to assume that role, so we
disable the default to avoid resolution conflicts.

    wordpress-db:
      mysql_database:
        - present

    wpadmin:
      mysql_user:
        - present
        - host: localhost
        - password: wppasswd

    wp-admin-grant:
      mysql_grants:
        - present
        - grant: all privileges
        - database: wordpress-db.*
        - user: wpadmin

Wordpress needs mysql as a backend and it requires a pre-configured
database and user. Those are set up in this section.

    /tmp/wordpress-3.7.1.tar.gz:
      file:
        - managed
        - source: http://wordpress.org/wordpress-3.7.1.tar.gz
        - source_hash: md5=8af9a4885ad134d354eb5f12dcc17fd9
        - unless: "[ -e /tmp/wordpress-3.7.1.tar.gz ]"

    unpack-wordpress:
      cmd:
        - run
        - name: "/bin/tar xzf /tmp/wordpress-3.7.1.tar.gz -C /tmp"
        - require:
          - file: /tmp/wordpress-3.7.1.tar.gz
        - unless: "[ -e /opt/wordpress/wp-config-sample.php ]"

    move-wordpress:
      cmd:
        - run
        - name: "/bin/mv /tmp/wordpress /opt"
        - require:
          - cmd: unpack-wordpress
        - unless: "[ -e /opt/wordpress/wp-config-sample.php ]"

    move-config:
      cmd:
        - run
        - name: "/bin/mv /opt/wordpress/wp-config-sample.php /opt/wordpress/wp-config.php"
        - require:
          - cmd: move-wordpress
        - unless: "[ -e /opt/wordpress/wp-config.php ]"

    edit-db-config:
      cmd:
        - run
        - name: "/bin/sed -i -e 's/database_name_here/wordpress-db/g' /opt/wordpress/wp-config.php"
        - require:
          - cmd: move-config

    edit-user-config:
      cmd:
        - run
        - name: "/bin/sed -i -e 's/username_here/wpadmin/g' /opt/wordpress/wp-config.php"
        - require:
          - cmd: edit-db-config

    edit-pwd-config:
      cmd:
        - run
        - name: "/bin/sed -i -e 's/password_here/wppasswd/g' /opt/wordpress/wp-config.php"
        - require:
          - cmd: edit-user-config

This last section downloads the wordpress package, unpacks it under
`/opt` and configures the database access with the values set up on the
configuration section for MySQL.

### The Pillar

The following pillar file sets up variables used by the apache-formula
pillar infrastructure. We are not, at the moment, using pillar directly
on our formula.

    apache:
      sites:
        wordpress.forgeservicelab.fi:
          # This server alias allows this vhost to listen as the default
          ServerAlias: _
          DocumentRoot: /opt/wordpress
          DirectoryIndex: index.php

This pillar file instructs the apache.vhosts.standard state to generate
a configuration file for a virtual host with a server name of
"wordpress.forgeservicelab.fi" which will have its document root pointed
at wordpress' installation folder on the filesystem. The directory index
directive ensures that it will serve wordpress' php site.
 Because this configuration uses apache's named virtual host resolution,
the virtual host would only respond to requests to
<http://wordpress.forgeservicelab.fi>, the ServerAlias directive set to
"\_" allows this virtual host to work as the default fallback and
respond to requests on the instance's IP.

### TODO

There are a number of hardcoded values throughout both the formula and
the pillar that should be parameterized into Saltstack's Pillar
infrastructure:

-   Wordpress' target installation folder
-   Apache's virtual host name
-   All three of MySQL's parameters:
    -   Wordpress user name.
    -   Wordpress user password.
    -   Wordpress database name.

Additionally, the formula could be rewritten so that it is not linked to
a specific version of wordpress.

The formula only works on the Debian family of Operating Systems, but
**it is not platform agnostic**, both the state and the pillar files
should be parameterized to do nothing if the target platform is not
debian-like, as [specified on SaltStack's
documentation](http://docs.saltstack.com/topics/conventions/formulas.html?highlight=formulas#platform-agnostic).
At a later stage, the formula could be improved to accomodate additional
target platforms.
