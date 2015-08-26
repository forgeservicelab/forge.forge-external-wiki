Example application
======================================================================

-------------------------------------------------------------------------------

Drupal-HA cluster architecture
=====================================================================================================

-   [High Availability
    clusters](#high-availability-clusters)
-   [How to partition a block device and set up LVM for
    DRBD](#how-to-partition-a-block-device-and-set-up-lvm-for-drbd)
-   [Identity
    backend](#identity-backend)

**Very Important!**

 Across the length of the following guide there will be references to
"floating IPs", this is OpenStack jargon and it refers to a public IP
that can be assigned to (floated around) different instances.
 In an OpenStack environment, usage of this public IP by the different
instances must be enabled on the security groups by allowing connections
from the networ router's IP.
 In non-OpenStack environments a "floating IP" will be a run-of-the-mill
Virtual IP and it will be typically allocated within the cluster's
private network.

Overview
---------------------------------------------------------

![Drupal HA
Architecture](/files/drupalHA.png)

Components
-------------------------------------------------------------

-   **Load Balancer:** Only element exposed to the world. Performs SSL
    termination and load distribution.

    -   [Nginx](http://nginx.org) web server to handle SSL termination.
    -   [HAProxy](http://haproxy.1wt.eu) load balancer.
-   **Drupal webserver cluster:** At least two nodes, scales out.

    -   [Apache](http://www.apache.org) web server with mod\_php5 and
        mod\_rewrite to serve [Drupal](https://drupal.org)
    -   [PHP5](http://php.net) as per Drupal's requirements
    -   [NFS
        client](https://help.ubuntu.com/lts/serverguide/network-file-system.html)
        to access the shared storage cluster.
-   **MySQL HA cluster:** Two nodes, does not scale out.

    -   [MySQL server](http://www.mysql.com) version 5.1 or higher.
    -   [DRBD](http://www.drbd.org) distributed block device, version 8.
    -   [Heartbeat](http://linux-ha.org/wiki/Heartbeat) cluster daemon.
    -   [Python Nova
        Client](https://pypi.python.org/pypi/python-novaclient/) tool,
        needed only on OpenStack deployments.
    -   [Heartbeat
        FloatingIP](https://git.forgeservicelab.fi/heartbeat-openstack/floatingip)
        script, needed only on OpenStack deployments.
-   **NFS HA cluster:** Two nodes, does not scale out.

    -   [NFS
        server](https://help.ubuntu.com/lts/serverguide/network-file-system.html)
        to provide shared storage.
    -   [DRBD](http://www.drbd.org) distributed block device, version 8.
    -   [Heartbeat](http://linux-ha.org/wiki/Heartbeat) cluster daemon.
    -   [Python Nova
        Client](https://pypi.python.org/pypi/python-novaclient/) tool,
        needed only on OpenStack deployments.
    -   [Heartbeat
        FloatingIP](https://git.forgeservicelab.fi/heartbeat-openstack/floatingip)
        script, needed only on OpenStack deployments.

Setup
---------------------------------------------------

Detailed description of the cluster setup, from the bottom up:

### High Availability clusters

The setup of both the NFS and the MySQL HA clusters is a lengthy process
and it's detailed step by step on the [High Availability
clusters](#high-availability-clusters) wiki article. From an eagle eye
point of view, this process involves the following steps:

-   [Partition the
    images'](#high-availability-clusters-image-partitioning) disk in
    order to accomodate the distributed block devices.
-   [Setup DRBD](#high-availability-clusters-drbd-setup), this will
    ensure data consistency between the primary and the failover nodes
    on the cluster.
-   [Tweak the NFS](#high-availability-clusters-nfs-setup) server
    installation on the shared storage cluster.
-   [Tweak the MySQL](#high-availability-clusters-mysql-setup) server
    installation on the database cluster.
-   [Setup Heartbeat](#high-availability-clusters-heartbeat-setup)
    daemon on both clusters to provide failover functionality.

### Drupal webserver cluster

All of the nodes in the Drupal webserver cluster are carbon copies of
each other and need no internetworking configuration; as far as each
node is concerned, it is the only webserver serving drupal.

There is a dependency on the NFS client tools, as the nodes on this
cluster store none of the drupal files which will be, instead, held on
the NFS server cluster.

    $ sudo apt-get install nfs-common

To serve drupal we will use the Apache webserver and its PHP5 module, we
also need to enable Apache's rewrite module in order to use "pretty
URLs". PHP itself needs the imagemagick and mysql modules to be able to
run drupal properly; the following will take care of all necessary
dependencies:

    $ sudo apt-get install apache2 libapache2-mod-php5 php5-gd php5-mysql php5-json
    $ sudo a2enmod rewrite

If we take care to mount the NFS drive under `/var/www` we won't need to
touch Apache's default configuration. To make the NFS mount permanent
across reboots, edit the `/etc/fstab` file and append the following
line:

    NFS.ALLOCATED.FLOATING.IP:/data/export    /var/www    nfs    rw,vers=3    0 0

Remember to replace `NFS.ALLOCATED.FLOATING.IP` with the actual
allocated floating IP from the OpenStack project (or your virtual IP of
choice if you're not deploying on OpenStack).

The installation will work with the settings above however, if we want
to enable clean URLs for drupal there is a small change to be made to
the Apache configuration, we need to tell the webserver to disable
MultiViews (Drupal's clean URLs don't work well with it) and to allow
access overrides so it will honor `.htaccess` files.

            AccessFileName .htaccess                # Add this line
            <Directory /var/www/>
                    Options Indexes FollowSymLinks  # Remove MultiViews
                    AllowOverride All               # Replace default None with All
                    Order allow,deny
                    allow from all
            </Directory>

With this in place, we can mount the NFS share and restart Apache to
pick up the changes.

    $ sudo mount /var/www
    $ sudo service apache2 restart

### Load Balancer

The software load balancer has two components, nginx webserver for SSL
termination and reverse proxy to the load balancer and HAProxy as the
load balancer proper.

    $ sudo apt-get install nginx haproxy

The nginx configuration file for SSL termination and reverse proxying at
`/etc/nginx/sites-available/default` reads as follows:

    server {
        location / {
            return https://$host$request_uri;
        }
    }

    server {
        listen 443;
        ssl on;
        ssl_certificate cert.pem; # Replace with path to actual certificate file
        ssl_certificate_key cert.key; # Replace with path to actual key file

        location / {
            proxy_pass http://localhost:10005;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_http_version 1.1;
        }
    }

The HAProxy configuration for load balancing at
`/etc/haproxy/haproxy.cfg` reads as follows:

    global
            log 127.0.0.1   local0
            log 127.0.0.1   local1 notice
            maxconn 4096
            user haproxy
            group haproxy
            daemon

    defaults
            log     global
            mode    http
            option  httplog
            option  dontlognull
            retries 3
            option redispatch
            maxconn 2000
            contimeout      5000
            clitimeout      50000
            srvtimeout      50000

    listen  plaza 127.0.0.1:10005
            option  httpchk *
            balance roundrobin
            cookie  SERVERID insert indirect nocache

            server  inst1 IP.TO.NODE.1:80 cookie drupal01 check inter 2000 fall 3 # Replace IP.TO.NODE.1 with actual node's IP
            server  inst2 IP.TO.NODE.2:80 cookie drupal02 check inter 2000 fall 3 # Replace IP.TO.NODE.2 with actual node's IP
    #       ....
    #       server  instN IP.TO.NODE.N:80 cookie drupal0N check inter 2000 fall 3 # Replace IP.TO.NODE.N with actual node's IP

            capture cookie ASPSESSION len 32
            srvtimeout      20000

            option  httpclose               # disable keep-alive
            option  checkcache              # block response if set-cookie & cacheable

            rspidel ^Set-cookie:\ IP=       # do not let this cookie tell our internal IP address

            errorfile       400     /etc/haproxy/errors/400.http
            errorfile       403     /etc/haproxy/errors/403.http
            errorfile       408     /etc/haproxy/errors/408.http
            errorfile       500     /etc/haproxy/errors/500.http
            errorfile       502     /etc/haproxy/errors/502.http
            errorfile       503     /etc/haproxy/errors/503.http
            errorfile       504     /etc/haproxy/errors/504.http

Restart the servers to pick up the configuration changes.

    $ sudo service nginx restart
    $ sudo service haproxy restart

### Install Drupal

Drupal installation needs to be done in just one node of the Drupal
webserver cluster. Grab the latest stable [distribution of
drupal](https://drupal.org/project/drupal) and unpack it to the
`/var/www` directory.

    $ wget http://ftp.drupal.org/files/projects/drupal-7.XX.tar.gz
    $ tar xzf drupal-7.XX.tar.gz
    $ sudo mv drupal-7.XX/* /var/www/
    $ sudo mv drupal-7.XX/.htaccess /var/www/
    $ sudo mv drupal-7.XX/.gitignore /var/www/
    $ sudo chown -R www-data:www-data /var/www

From here on, you can follow [drupal's installation
guide](https://drupal.org/documentation/install/create-database)

**NOTE:** Running drupal behind a reverse proxy that handles the SSL
termination will cause drupal to send content that the browsers will tag
as "insecure". To fix this issue we need to tell drupal that it is being
served through https by editing the `settings.php` file and adding this
line:

    $base_url = 'https://your.domain.name';  # No trailing slashes!!

High Availability clusters
===========================================================================================

The purpose of this guide is to document how to set up services in a
Highly Available primary/failover cluster to avoid SPOFs. We will be
using [DRBD](http://www.drbd.org) for data replication, unfortunately
this limits the cluster size to two nodes. While it is possible to scale
out the cluster by stacking DRBD devices on top of each other, it
provides little added value for the extra complexity at the moment.

**Note:** Unless otherwise specified, all actions on this guide must be
executed on all server nodes.

### Notation:

In this guide we will set up two clusters with two nodes each, one will
serve an NFS share, the other will serve MySQL. During the rest of the
guide we will use the following conventions:

-   **NFS server 1:** hostname: nfs1, ip: 192.168.0.11
-   **NFS server 2:** hostname: nfs2, ip: 192.168.0.12
-   **Floating IP for NFS:** 193.166.0.10
-   **MySQL server 1:** hostname: mysql1, ip: 192.168.0.21
-   **MySQL server 2:** hostname: mysql2, ip: 192.168.0.22
-   **FloatingIP for MySQL:** 193.166.0.20

When implementing this setup, remember to replace these hostnames and
IPs with the proper ones for your own implementation. Also, for all
intents and purposes, the hostnames above are the output of the command
`uname -n`

High Availability clusters image partitioning
---------------------------------------------------------------------------

DRBD can be understood as a network-distributed RAID-1, what this means
for us is that we will need to set up two separate partitions for the
DRBD service:

-   A metadata partition. This is for DRBD internals and should be at
    least 150MB in size, although increasing the size adds no value.
-   A data partition. This will hold the data shared across the cluster
    and can be as big as needed.

Both partitions should have `ext4` filesystem and none of them should be
mounted by default.
 OpenStack holds a 30GB Debian Wheezy image already partitioned for this
purpose, by the name of `DRBD-partition-table`; typically though you'd
want to use any given image and setup the partitions above on an
attached block device (a Cinder device on OpenStack).

### How to partition a block device and set up LVM for DRBD

For reference, during the rest of this guide we will use the following
device names:

-   **/dev/vda7** - The 150MB metadata partition
-   **/dev/vda8** - The data partition

These device names happen to match the ones on OpenStack instances
launched from the `DRBD-partition-table` image.

High Availability clusters DRBD setup
-----------------------------------------------------------

First of all, we need to ensure that the system clock on all cluster
nodes are in sync, to ensure that NTP is installed, run:

    $ sudo apt-get install ntp

Installing DRBD is easily done via package management:

    $ sudo apt-get install drbd8-utils

Append the following lines to `/etc/drbd.conf`

    resource nfs {        # replace with 'resource mysql {' on MySQL cluster nodes
      protocol C;

      startup {
        degr-wfc-timeout 120;
      }

      disk {
        on-io-error detach;
      }

      syncer {
        rate 10M;
        al-extents 257;
      }

      on nfs1 {          # replace with 'on mysql1 {' on MySQL cluster nodes
        device        /dev/drbd0;
        disk          /dev/vda8;
        address       192.168.0.11:7788;        # replace with 'address   192.168.0.21:7788' on MySQL cluster nodes
        meta-disk     /dev/vda7[0];
      }

      on nfs2 {          # replace with 'on mysql2 {' on MySQL cluster nodes
        device        /dev/drbd0;
        disk          /dev/vda8;
        address       192.168.0.12:7788;        # replace with 'address   192.168.0.22:7788' on MySQL cluster nodes
        meta-disk     /dev/vda7[0];
      }
    }

DRBD needs to initialize the metadata partition and requires its
beginning to be zeroed out:

    $ sudo modprobe drbd
    $ sudo dd if=/dev/zero of=/dev/vda7 bs=1M count=128
    $ sudo drbdadm create-md nfs
    $ sudo drbdadm up all

Remember that the create-md command should be
`sudo drbdadm create-md mysql` on mysql cluster nodes.

 If `modprobe` outputs the following error:

    FATAL: Module drbd not found.

you may need to install the `linux-server` package.

    $ sudo apt-get install linux-server

Now the DRBD device should be up and running but it will be in an
inconsistent state, we need to invalidate the failover server and force
the primary to become DRBD's primary.
 On nfs2/mysql2 run:

    $ sudo drbdadm invalidate nfs

And on nfs1/mysql1 run:

    sudo drbdadm -f primary nfs

As before, remember to replace `nfs` with `mysql` on mysql cluster
nodes.

Now the initial sync should have started and `cat /proc/drbd` should
produce an output similar to the following:

    version: 8.3.11 (api:88/proto:86-96)
    srcversion: F937DCB2E5D83C6CCE4A6C9 
     0: cs:Connected ro:Secondary/Primary ds:UpToDate/UpToDate C r-----
        ns:1104 nr:2052 dw:3156 dr:6782 al:7 bm:0 lo:0 pe:0 ua:0 ap:0 ep:1 wo:f oos:0
        [==========>.........] sync'ed: 53.1% (11606/24733)M
            finish: 1:14:16 speed: 2,644 (2,204) K/sec

Wait for the process to complete (it may take a while, depending on the
data partition's size) and run:

    $ sudo service drbd restart

High Availability clusters NFS setup
---------------------------------------------------------

We will install the NFS server from the package manager, but we do not
want it to start on its own (heartbeat will do that), so we will have to
remove from the upstart chain.

    $ sudo apt-get install nfs-kernel-server
    $ sudo service nfs-kernel-server stop
    $ sudo service nfs-common stop
    $ sudo update-rc.d -f nfs-kernel-server remove
    $ sudo update-rc.d -f nfs-common remove

The NFS exports configuration defines, based on IP, who is allowed to
mount the NFS drive. This means that there is a discrepancy on the
`/etc/exports` file between OpenStack and non-OpenStack environments.
 For OpenStack, assuming the network router's public IP is 193.166.0.1:

    /data/export 193.166.0.1/255.255.255.255(rw,no_root_squash,no_all_squash,sync,fsid=123)

For non-OpenStack environments;

    /data/export 192.168.0.0/255.255.255.0(rw,no_root_squash,no_all_squash,sync,fsid=123)

The `fsid` option ensures that the exported filesystem is identified as
the same no matter which block device it is exported from, it must have
the same value on all the nodes.

NFS stores information in `/var/lib/nfs`, we want this info to be shared
between the primary and the failover nodes so we'll make sure the info
is stored on the DRBD device.

    $ sudo mkdir /data

Only on nfs1:

    $ sudo su
    # mount /dev/drbd0 /data
    # mv /var/lib/nfs/ /data/
    # ln -s /data/nfs/ /var/lib/nfs
    # mkdir /data/export
    # chmod 777 /data/export
    # umount /data
    # exit

Only on nfs2:

    $ sudo su
    # rm -rf /var/lib/nfs/
    # ln -s /data/nfs/ /var/lib/nfs
    # exit

High Availability clusters MySQL setup
-------------------------------------------------------------

We will install the MySQL server from the package manager, but we do not
want it to start on its own (heartbeat will do that), so we will have to
remove from the upstart chain.

    $ sudo apt-get install mysql-server
    $ sudo service mysql stop
    $ sudo update-rc.d -f mysql remove

The standard MySQL installation is configured to bind to the loopback
address only. Edit the `/etc/mysql/my.cnf`, find the line:

    bind-address         = 127.0.0.1

and comment it out.

We need to tweak our filesystem so that MySQL stores its data on the
DRBD device:

    $ sudo mkdir /data

Only on mysql1:

    $ sudo su
    # mount /dev/drbd0 /data
    # mv /var/lib/mysql/ /data/
    # ln -s /data/mysql/ /var/lib/mysql
    # umount /data
    # exit

Only on mysql2:

    $ sudo su
    # rm -rf /var/lib/mysql/
    # ln -s /data/mysql/ /var/lib/mysql
    # exit

**NOTE:** On some systems, moving MySQL's data directory may cause the
server to fail to start, it is usually due to apparmor preventing access
to the new datadir. To solve this issue, edit as root the file
`/etc/apparmor.d/usr.sbin.mysqld` and add the following lines within the
`mysqld` block:

    /data/mysql/ r,
    /data/mysql/** rwk,

High Availability clusters Heartbeat setup
---------------------------------------------------------------------

Heartbeat will monitor availability on the clusters and bounce the
failover servers if necessary. It is also responsible for the allocation
of the floating IP to the appropriate instance. We will install it from
the package manager.

    $ sudo apt-get install heartbeat

The `/etc/heartbeat/ha.cf` file configures the HA cluster.
 On nfs1/mysql1 it reads:

    logfacility    local0
    keepalive      2
    deadtime       10
    auto_failback  on
    ucast          eth0  192.168.0.12    # Peer IP address, replace with 192.168.0.22 on mysql1
    node           nfs1                  # Replace with mysql1 on mysql nodes
    node           nfs2                  # Replace with mysql2 on mysql nodes

On nfs2/mysql2 it reads:

    logfacility    local0
    keepalive      2
    deadtime       10
    auto_failback  on
    ucast          eth0  192.168.0.11    # Peer IP address, replace with 192.168.0.21 on mysql1
    node           nfs1                  # Replace with mysql1 on mysql nodes
    node           nfs2                  # Replace with mysql2 on mysql nodes

The file `/etc/heartbeat/authkeys` controls the node authentication on
the cluster, it reads:

    auth 3
    3 md5 <some-random-string>

It should be readable by root only, so we make sure to set the proper
permissions:

    $ sudo chmod 600 /etc/heartbeat/authkeys

Lastly, the file `/etc/heartbeat/haresources` defines the heartbeat
tasks. Due to the handling of floating IPs there is a discrepancy
between OpenStack and non-OpenStack environments.

### On OpenStack environments

On the NFS cluster the file reads:

    nfs1 FloatingIP::/etc/openstack/nova.conf drbddisk::nfs Filesystem::/dev/drbd0::/data::ext4 nfs-kernel-server

On the MySQL cluster it reads:

    mysql1 FloatingIP::/etc/openstack/nova.conf drbddisk::mysql Filesystem::/dev/drbd0::/data::ext4 mysql

For this to work, the files from [this
module](https://git.forgeservicelab.fi/heartbeat-openstack/floatingip)
are needed, make sure that the `FloatingIP*` files are executable. You
will also need to modify `nova.conf` to reflect the appropriate floating
IP, so it will read like:

    OS_USERNAME=username
    OS_PASSWORD=password
    OS_PROJECT=projectid
    OS_AUTHURL=https://cloud.forgeservicelab.fi:5001/v2.0
    OS_FLOATIP=193.166.0.10

Remember that `OS_FLOATIP=193.166.0.20` on the MySQL cluster.

The openstack scripts have a dependency on OpenStack's novaclient python
package:

    $ sudo apt-get install python-dev python-pip
    $ sudo pip install python-novaclient

You will need this before you restart heartbeat, otherwise it will exit
with an error.

### On non-Openstack environments

On the NFS cluster the file reads:

    nfs1 IPaddr::192.168.0.10/24/eth0 drbddisk::nfs Filesystem::/dev/drbd0::/data::ext4 nfs-kernel-server

On the MySQL cluster it reads:

    mysql1 IPaddr::192.168.0.20/24/eth0 drbddisk::mysql Filesystem::/dev/drbd0::/data::ext4 mysql

The last thing left to do is to restart the services to pick up the new
configurations:

    $ sudo service heartbeat restart

Generic service setup
---------------------------------------------------------------------------------

As can be seen on the previous sections, it is fairly easy to replicate
this setup for any given service that we might want to provide on a
highly available manner, the steps are:

-   Install the service
-   Make sure the service is stopped
-   Remove the service from the upstart chain
-   Make sure to move the service's data over to the DRBD device
-   Configure heartbeat to manage the service by modifying
    `/etc/heartbeat/haresources` to look like

<!-- -->

    hostname IPaddr::192.168.0.250/24/eth0 drbddisk::r0 Filesystem::/dev/drbd0::/data::ext4 servicename

Where hostname is the output of `uname -n`, r0 is the name of the DRBD
device as configured on `/etc/drbd.conf` and servicename is the name of
the service's startup script as it appears on `/etc/init.d/`.

------------------------------------------------------------------------

How to partition a block device and set up LVM for DRBD
==================================================================================================================================================================================

This guide assumes that the block device to be partitioned is attached
to the computing instance, e.g. as per the [instructions for Cinder
volume storage](3_OpenStackIaaSplatform.md#persistent-storage). For reference, we'll say
that this block device appears as `/dev/vdb` to the instance's operating
system.

A newly attached volume will not have a valid partition table, so we'll
need to create a new one

    $ sudo fdisk /dev/vdb

Once on fdisk's interactive shell, we'll issue the following commands:

    n        # Create a new partition
    p        # Make it primary
    1        # First partition on disk
    [Enter]  # Use the default value for first sector
    +150M    # Set partition size to 150 MB
    n        # Create a new partition
    p        # Make it primary
    2        # Second partition on disk
    [Enter]  # Use the default value for first sector
    [Enter]  # Use the default value for last sector (Use all of the remaining disk space)
    t        # Change the type of a partition
    2        # Select the second partition
    8e       # Set the type to Linux LVM
    w        # Write-out and exit fdisk

The output from `sudo fdisk -l /dev/vdb` should look similar to

    Disk /dev/vdb: 10.7 GB, 10742661120 bytes
    16 heads, 63 sectors/track, 20815 cylinders, total 20981760 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disk identifier: 0x8b6056d1

       Device Boot      Start         End      Blocks   Id  System
    /dev/vdb1            2048      309247      153600   83  Linux
    /dev/vdb2          309248    20981759    10336256   8e  Linux LVM

With the disk properly partitioned, we'll need to set up LVM

    $ sudo apt-get install lvm2
    $ sudo pvcreate /dev/vdb2              # Create the physical volume on the partition we set up for it.
    $ sudo vgcreate data /dev/vdb2         # Create the volume group on the physical disk, note that 'data' is the volume group name, it can be anything relevant to you.
    $ sudo lvcreate -n nfs -l 100%VG data  # Create the logical volume on the volume group, 'nfs' is the logical volume name. The -l flag sets it to use all of the available space.

We have created a new logical volume that will reside under
`/dev/mapper/data-nfs` but there is no filesystem on it, we will need to
create one

    $ sudo mkfs.ext4 /dev/mapper/data-nfs

With this, the disk is ready to be used with DRBD with the added value
that the data partition can be resized in the future, in case extra
storage is needed.
 Remember when moving to other guides that with this setup DRBD's
metadata partition is `/dev/vdb1` while the data partition will be the
logical volume on `/dev/mapper/data-nfs`

Identity backend
=============================================================

Identity backend is a server setup with directory service (user
accounts, groups, roles, potentially hosts) and some interface to manage
the directory. In case of this howto, those are OpenLDAP and
phpldapadmin. In addition, we will install CASino for Single Sign-On.

Directory service
---------------------------------------------------------------

LDAP is the most popular directory protocol. There are several
implementation. I chose OpenLDAP, it is one of the more popular ones.

OpenLDAP has two modes of configuration - it can be controlled with text
config from the filesystem (/etc/openldap/sladp.conf), or with
equivalent items in the LDAP tree with root in cn=config. Although the
latter is recommended, I will stick to the text configuration as that is
better supported, and more easily automated with ansible.

Web interface
-------------------------------------------------------

It would be nice to have a web interface to add, remove and modify items
in the LDAP tree. There are a few projects and they need to be
investigated and one picked. I tried ldap-account-manager and that seems
to be quite limited. It does not have service for self-change of
password, and it can not handle groupOfNames as a group class.

I picked phpldapadmin for its simplicity.

Single Sing-On
---------------------------------------------------------

CAS is a protocol for Single Sing-On, and CASino is one of its
implementations. It's a Ruby on Rails project and it's quite simple to
setup and configure.

Installing with Ansible
---------------------------------------------------------------------------

In the following text, I will show how to install the identity backend
server with Ansible.

### Requirements

You will need to have git and ansible &gt; 1.8 installed. You will also
need OpenStack client tools, in particular nova.

### Virtual machine

You will need a virtual machine. Pick a CentOS 6.x or 7.x image and
launch it. Don't forget to open ports 443 (https for CASino SSO), 636
(ldaps) and 8443 (phpldapadmin interface) in the relevant security
group. To launch a Linux image, you can follow [image launch
guide](3_OpenStackIaaSplatform.md#launch-linux-instance). Assign a public Floating IP to the
image and try to ssh there.

### Ansible setup

You need to set up your Ansible inventory. Please follow [this
guide](4_Continuousdelivery.md#inventory-setup-for-the-forge-openstack). Once your
inventory is set up, try

    $ ansible <your_ip> -m ping 

### Ansible playbook and roles setup

Get the ansible playbook for the Identity Backend, and go to its
directory:

    $ git clone https://git.forgeservicelab.fi/ansible/identity-backend.git
    $ cd identity-backend

See the identity.yml (also here
<https://git.forgeservicelab.fi/ansible/identity-backend/blob/master/identity.yml>).
You will need to modify ldap\_dn to the DN of the root of your LDAP
tree. Also, you can modify parameters of the self-signed certificate for
the OpenLDAP server.

You will also need to create file secrets.yml with the
ldap\_admin\_password and binder\_password. The ldap password is for
admin user, and the binder password is for binder account for e.g.
casino. It can look for example as:

    ---
    ldap_admin_password: 'p4ssW0rD'
    binder_password: 'fc284f928323f0@#%fsde'

Then, run ansible-galaxy to get necessary roles:

    $ ansible-galaxy install -p roles -r requirements.yml -f

### Customizations

#### Hostname

If you have your own hostname, you might want to remove the
forge\_hostname role call, and put `- hostname: <your_hostname>` to
pre\_tasks.

### Ansible run

You are ready to roll. From the identity-backend directory, run:

    $ ansible-playbook -u cloud-user -s -e h=<your_vms_ip> identity.yml

if you are using CentOS 7 or newer, the username is "centos", not
"cloud-user".

You will watch a lot of ansible output. In the end, there should be

    TASK: [debug ] **************************************************************** 
    ok: [193.166.24.142] => {
        "msg": "visit https://ip-[...].hosts.forgeservicelab.fi:8443/phpldapadmin to add users"
    }

    TASK: [debug ] **************************************************************** 
    ok: [193.166.24.142] => {
        "msg": "visit https://ip-[...].hosts.forgeservicelab.fi:443 to see the CASino interface"
    }

Point your browser to
`https://ip-[...].hosts.forgeservicelab.fi:8443/phpldapadmin` and login
as "admin" with password that you put to secrets.yml. Then, create a
testing user and log in with his credentials at
`https://ip-[...].hosts.forgeservicelab.fi`.

LDAP administration
-------------------------------------------------------------------

In the web interface, you can add users, groups and roles. The ACL of
the OpenLDAP is set that users who are in the admin role can do
everything in the tree. Users not in the admin role can modify their own
attributes.

If you want to do some more modifications, you might want to ssh to the
machine and tune details yourself.

LDAP over SSL is available on port 636 on the machine.

SAML Identity Provider
=============================================================================


FORGE SAML Identity Provider serving the FORGE accounts is available in
<https://idp.forgeservicelab.fi>. Clicking the "Federation" tab will
provide you the metadata that you can use in the service provider to
connect your application. To test your SAML Service Provider against our
Identity Provider, contact FORGE support to list your SP metadata in the
IDP. In order to have your SP valid in FORGE IdP for a longer period of
time than 24 hours, please remove "ValidUntil=2015-05-05..." entry from
XML.

About
-------------------------------------------

SAML is a standard for exchanging authentication and authorization data
between more domains. It is using extensively XML for data and metadata
representation. It is capable of Single-Sign On and identity federation.
It is an alternative to standards like OpenID Connect (used for Google
Plus login) and the social network logins.

SAML is popular among Finnish public institutions
(<https://confluence.csc.fi/display/VIRTU/Palvelulista>). It allows to
authenticate and authorize an employee from finance ministry in some
TEKES web application, etc. The SAML identity providers of various
Finnish public institutions are aggregated in Virtu -
<https://confluence.csc.fi/display/VIRTU/Virtu>.

Virtu is a listing of verified Identity Providers from Finnish public
institutions. You can set the Discovery Service URL
(<https://virtu-ds.csc.fi/DS>) in your web application (aka service
provider) and it will set the preferred "home" IDP for future logins.

Some links:
 \* Explaining what are the identity provider and service provider in
SAML: <http://en.wikipedia.org/wiki/Identity_provider>\
 \* Anatomy of the SAML in great detail:
<https://en.wikipedia.org/wiki/SAML_2.0>\
 \* SimpleSamlPHP, the most simple and straightforward implementation of
both Service Provider and Identity Provider:
<https://simplesamlphp.org/>\
 \* Setup of SimpleSamlPHP as service provider, i.e. as a web
application forwarding logins to an Identity Provider:
<https://simplesamlphp.org/docs/stable/simplesamlphp-sp>\
 \* OpenAM, the more robust and feature-rich SSO (SAML including)
implementation: <http://openam.forgerock.org/>

Run your own Identity Provider
---------------------------------------------------------------------------------------------

We provide playbook and role for installing you own SAML Identity
Provider which you can customize for your needs.

Clone repo <https://git.forgeservicelab.fi/ansible/idp> , customize the
playbook (remove roles that you don't need), fill the secrets and run it
on your test host. The playbook is used to instantiate IdP for our SAML
FORGE identity gateway.

You probably do not need more than the simplesamlphp role
<https://git.forgeservicelab.fi/ansible-roles/simplesamlphp/tree/master>.

Port forwarding proxy
==========================================================================

This article describes how to create a general port forwarding proxy for
a single service. You might want to set such proxy when you have a
service with restricted access and you want to avoid whitelisting too
many locations in the service itself. With the proxy, you can just
whitelist the proxy on the restricted service, and then you delegate
further access control to the proxy.

The proxy can also work to access a service in unreachable networks -
you have a private network of hosts where only one host have IP address
accessible from the Internet.

The setup is using iptables. The limitation of this setup is that you
can specify only one location (IP:port) in the proxy. In other words,
the proxy in the setup will not work as a gateway. I also consider only
IPv4.

Scheme
============================================

![Scheme](/files/portforw.png)

External firewall rules
==============================================================================

Access control on firewalls placed between any of the components on the
scheme should be set so that relevant hosts can access the proxy, and
only proxy can access the restricted service.

Set up on the proxy
======================================================================

Assuming the IP address of the restricted service is 192.168.0.2 and
it's running on port 443, we should do following on the proxy. The setup
is using the "nat" table of iptables, so if you are using iptables for
something else, you should pay attention to eventual conflicts. The
proxy will forward from local port 10443.

    # enable IP forwarding
    echo "1" > /proc/sys/net/ipv4/ip_forward

    # add masquerade rule to postrouting
    iptables -t nat -A POSTROUTING -j MASQUERADE
    iptables -t nat -A PREROUTING -p tcp --dport 10443 -j DNAT --to 192.168.0.2 443

That should be all. Verify that

    telnet proxy 10444

will get you to the machine with restricted access.

Hadoop Cluster setup
=================================================================

Hadoop is an open source software framework for storing and processing
big data in a distributed fashion on large clusters of commodity
hardware. Essentially, it accomplishes 2 tasks: massive data storage and
fast processing.

FORGE ServiceLab's [dedicated
playbook](https://git.forgeservicelab.fi/ansible/cdh5-hadoop/tree/master)
sets up what we've called a 12+1 node cluster. This type of cluster is
composed of:

-   1 monitor node, with hostname monitor01
-   2 hadoop name nodes, with hostnames hmaster\[01:02\]
-   10 hadoop data nodes, with hostnames hslave\[01:10\]

The playbook takes care of the instantiation of the machines needed to
set up the cluster.
 After running the playbook, an `etc/hosts` file fragment is generated
on the user's `HOME`; this matches the above hostnames with the
associated floating IPs.

Playbook caveats
---------------------------------------------------------

The Ansible modules dealing with associating floating IPs to OpenStack
instances do so by **allocating a new** floating IP to the OpenStack
tenant and then associating it to the instance, because of this it is
necessary to ensure that the OpenStack tenant has enough (13)
unallocated floating IPs. The modules will **not** use allocated but
disassociated floating IPs.

Playbook requirements
-------------------------------------------------------------------

Besides the usual username, password, tenant identification parameters
needed to interact with OpenStack, the playbook needs a number of other
bits of OpenStack information:

-   `Network ID` - This is the UUID of the OpenStack tenant's private
    network (VLAN) to which the cluster will be connected

        $ nova network-list
        +--------------------------------------+----------------+------+
        | ID                                   | Label          | Cidr |
        +--------------------------------------+----------------+------+
        | 462fafa9-1c4a-41da-b3a2-3a063f4457dc | public         | None |
        | 6b99ac24-189d-4182-ad08-1237719e8c91 | digile-testing | None |
        +--------------------------------------+----------------+------+

-   `Image ID` - This is the ID of the image to be used to boot the
    instances from

        $ nova image-list
        +--------------------------------------+------------------------------------+--------+--------+
        | ID                                   | Name                               | Status | Server |
        +--------------------------------------+------------------------------------+--------+--------+
        | e9734856-5e92-4ac8-aa6b-b3164e845f7e | CentOS-6.5-server-x86_64           | ACTIVE |        |
        | 8da13f00-1375-4e97-88f9-35be9877617e | Debian-7.3-server-amd64-DEPRECATED | ACTIVE |        |
        | d732a152-04f7-4cc0-938b-879705c1d963 | Debian-7.4-server-amd64-DEPRECATED | ACTIVE |        |
        | 6ff87365-ef2d-4b31-8e06-46d443e94d34 | Debian-7.5-server-amd64_DEPRECATED | ACTIVE |        |
        | 8fdcd873-168f-4d1f-9236-7ba3d8f88cbd | Debian-7.5-server-amd64_DEPRECATED | ACTIVE |        |
        | 9ee35702-87d5-4216-a9fe-9e02bdad73a9 | Debian-7.6-server-amd64            | ACTIVE |        |
        | 47ebe70b-7876-4391-a648-07abbacb4da4 | Debian-7.6-server-amd64_DEPRECATED | ACTIVE |        |
        | dc615573-7134-4b56-a152-262b92904067 | Ubuntu-12.04-server-amd64          | ACTIVE |        |
        | 70c1723b-ef3f-4056-adee-aea3e5b3b4a2 | Ubuntu-14.04-server-amd64          | ACTIVE |        |
        +--------------------------------------+------------------------------------+--------+--------+

-   `Flavor ID` - This is the ID of the OpenStack flavor to be used on
    the instances

        $ nova flavor-list
        +----+------------+-----------+------+-----------+------+-------+-------------+-----------+
        | ID | Name       | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor | Is_Public |
        +----+------------+-----------+------+-----------+------+-------+-------------+-----------+
        | 1  | m1.tiny    | 1024      | 10   | 0         |      | 1     | 1.0         | True      |
        | 2  | m1.small   | 2048      | 10   | 0         |      | 1     | 1.0         | True      |
        | 3  | m1.medium  | 4096      | 20   | 0         |      | 2     | 1.0         | True      |
        | 4  | m1.large   | 8192      | 40   | 0         |      | 4     | 1.0         | True      |
        | 5  | m1.x-large | 16384     | 80   | 0         |      | 8     | 1.0         | True      |
        +----+------------+-----------+------+-----------+------+-------+-------------+-----------+

Flavor setup
-------------------------------------------------

The FORGE OpenStack hadoop flavors are mandatory for the cluster
namenodes and datanodes, these flavors ensure that each of the cluster
nodes resides on a different hardware host in addition to be the best
possible fit for hadoop demands. These are the guidelines for assigning
flavors to the different roles in the cluster:

-   `monitor01` - *Minimum* and recommended `m1.tiny`, could grow up to
    `m1.medium` depending on usage demands.
-   `hmaster[01:02]` - *Always* `hadoop.small`.
-   `hslave[01:10]` - *Any* of `hadoop.small`, `hadoop.medium` or
    `hadoop.large` depending on usage demands.

Playbook run
-------------------------------------------------

Be sure to set all required variables in the `host_vars/localhost` and
`group_vars/all` files, then:

    $ ansible-playbook -i hosts cdh.yml

For more information on the playbook, read [its
documentation](https://git.forgeservicelab.fi/ansible/cdh5-hadoop/blob/master/README.md)

------------------------------------------------------------------------

SAML Service Provider
==================================================================================

SAML Service Provider is the part of SAML authentication that resides on
the side of a web application. A web app will delegate the login process
to SAML SP and SAML SP will redirect to one or more configured SAML
Identity Providers. You will then be able to authenticate using the
FORGE credentials.

We prepared a demo playbook at
<https://git.forgeservicelab.fi/ansible/django_saml_demo/tree/master>
which installs a Django app with SAML service provider set up with
djangosaml2. To set up, you must:

-   launch an instance of Ubuntu 14.04 and assign it a floating ip
-   put the vm in your Ansible inventory, so that
    `ansible -m ping <your_floating_ip>` works
-   `git clone https://git.forgeservicelab.fi/ansible/django_saml_demo.git`
-   `cd django_saml_demo`
-   `ansible-playbook -s -e h=<your_floating_ip> dj.yml`

Then ask forge support to add the hostname of your SP to
/var/simplesamlphp/metadata/saml20-sp-remote.php on
idp.forgeservicelab.fi.

After your SP is added to IDP listing, visit `http://<your_hostname>`
and follow the /test link. The Django app will show the attributes it
gets from the Service Provider for the logged in user.

Links
------------------------------------------

-   role settign up the app:
    <https://git.forgeservicelab.fi/ansible-roles/django_saml_app>
-   how to set up SAML Identity Provider:
    [SAML Identity Provider](#saml-identity-provider)

------------------------------------------------------------------------

KaPA test service
==============================================================

FORGE Service Lab is running a KaPA compliant test service which can be
used to have a quick start in developing and testing your own service.
You can start using FORGE's KaPA test services right away without any
bureaucracy.

FORGE Service Lab is also running a "co-operative" secure server that is
connected to KaPA development environment. We'll offer that for your use
in case you don't want to run a secure server by yourself. You will find
more information at the end of this page about how you can connect your
service to development KaPA of CSC by using FORGE Service Lab secure
server.

This document outlines the process of defining and publishing a KaPA
(Kansallinen Palveluväylä) compatible test service in the FORGE
environment. This will provide a starting point for further service
development and running tests against a baseline service that is known
to work.

Requirements and assumptions
------------------------------------------------------------------------------------

-   (Dummy) Service Developer Organization identifier
-   (Dummy) Service Developer Subsystem identifier for test service
-   (Dummy) Service Developer Subsystem identifier for test client
-   Linux host for running the test service
-   Linux host for running the test client

When calls are made directly to the host running the service, dummy
identifiers can be used. If service is migrated to
development/production KaPA, the Organization and Subsystem identifiers
need to be added to the central directory by KaPA administration.

Communication is plaintext HTTP or HTTPS with self-signed certificates.

Software dependencies
----------------------------------------------------------------------

Latest information about SW dependencies is available in
<https://github.com/petkivim/x-road-adapter-example/wiki/Setting-up-Development-Environment>

Checkout and build
----------------------------------------------------------------

First step is to check out the source code for the test service.

`git clone https://github.com/petkivim/x-road-adapter-example.git`

To identify that the test service is indeed provided by your
organization, the following modifications need to be done:

`src/main/webapp/WEB-INF/classes/example.wsdl`

-   the default namespace entries (`http://test.x-road.fi/producer`)
    need to be changed so the namespace is unique - for example the
    FORGE test service uses `http://forge-test.x-road.fi/producer`

-   the `wsdl:service` component is changed to contain proper address of
    the service, for example
    `<soap:address location="http://testservice.forgeservicelab.fi:8080/TestService/Endpoint" />`

    -   In case HTTPS protocol or for example some other port than
        Tomcat default of 8080 is used, the address needs to be
        modified accordingly.

`src/main/webapp/WEB-INF/classes/xrd-servlet.properties`

-   the serialize/deserialize elements are changed to contain the new
    namespace defined in aforementioned `example.wsdl`

Building is done by descending to the `src` directory and running:

`mvn clean install`

If the build was successful, the file
`target/example-adapter-x.x.x-SNAPSHOT.war` is present, where x.x.x is
current version number of the adapter.

Deploying
----------------------------------------------

Once the build has been successfully completed, the app needs to be
deployed. In case of Tomcat 6, this is most easily done as follows:

-   Copy `example-adapter-x.x.x-SNAPSHOT.war` to
    `/var/lib/tomcat6/webapps`
    -   The package can also be renamed for a more streamlined
        application path, for example
        `cp example-adapter-x.x.x-SNAPSHOT.war /var/lib/tomcat6/webapps/TestService.war`
    -   Alternatively, Tomcat server paths can be reconfigured.
-   Restart tomcat

After these steps, your application should now be ready to respond to
incoming requests.

Testing the service
==================================================================

Before external applications or systems can access the service, it must
be ensured that the firewall is open for requests. In FORGE environment
this means checking that the Instance is bound to a Security Group that
allows traffic to pass via the respective TCP port. In our example the
port is 8080.

Once firewall is open, one can proceed to check out the test script from
`https://git.forgeservicelab.fi/ansible/kapa-testapp`. The test script
is ran as follows (run without arguments for help):

    $ python files/kapa-testapp.py -i FI-DEV -l COM -c 0785944-0 -s FORGEDemo -t http://testservice.forgeservicelab.fi:8080/TestService/Endpoint \
                                   -m COM -e 0785944-0 -y TestService -n http://forge-test.x-road.fi/producer
    Received response: Hello test_string! Greetings from adapter server!
    $ 

If failed events don't occur, the test service responded to the request
and the test was successful. You have now made your first KaPA
compatible request into your test service!

Message format (v6 beta)
--------------------------------------------------------------------------

The following outlines the basic message format used in this test and in
KaPA SOAP messages in general. The format conforms to X-Road protocol v6
beta.

    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:id="http://x-road.eu/xsd/identifiers" xmlns:sdsb="http://x-road.eu/xsd/sdsb.xsd">
        <SOAP-ENV:Header>
            <sdsb:client id:objectType="SUBSYSTEM">
                <id:sdsbInstance>FI-DEV</id:sdsbInstance>
                <id:memberClass>XXX</id:memberClass>
                <id:memberCode>XXXXXXXX</id:memberCode>
                <id:subsystemCode>XXXXXXXX</id:subsystemCode>
            </sdsb:client>
            <sdsb:service id:objectType="SERVICE">
                <id:sdsbInstance>FI-DEV</id:sdsbInstance>
                <id:memberClass>YYY</id:memberClass>
                <id:memberCode>YYYYYYYYY</id:memberCode>
                <id:subsystemCode>TestService</id:subsystemCode>
                <id:serviceCode>getRandom</id:serviceCode>
                <id:serviceVersion>v1</id:serviceVersion>
            </sdsb:service>
            <sdsb:userId>EE1234567890</sdsb:userId>
            <sdsb:id>ID11234</sdsb:id>
        </SOAP-ENV:Header>
        <SOAP-ENV:Body>
            <ns1:getRandom xmlns:ns1="http://forge-test.x-road.fi/producer">
                <request/>
            </ns1:getRandom>
        </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>

The Client, Service and User identifiers are defined in the SOAP message
header. If the service does not utilize user ID's, a dummy one must be
used.

        <SOAP-ENV:Header>
            <sdsb:client id:objectType="SUBSYSTEM">
                [...]
            </sdsb:client>
            <sdsb:service id:objectType="SERVICE">
                [...]
            </sdsb:service>
            <sdsb:userId>EE1234567890</sdsb:userId>
            <sdsb:id>ID11234</sdsb:id>
        </SOAP-ENV:Header>

The call to the service is transported in the SOAP message body.

        <SOAP-ENV:Body>
            <ns1:getRandom xmlns:ns1="http://forge-test.x-road.fi/producer">
                <request/>
            </ns1:getRandom>
        </SOAP-ENV:Body>

Adding test service to development KaPA
==========================================================================================================

Registration
----------------------------------------------------

After you have developed and verified that your service is able to
communicate with FORGE Service Lab KaPA test services you may consider
joining KaPA development environment and using FORGE's secure server as
a gateway to KaPA. This is achieved with the following steps.

1.  Register your organization to KaPA - for more instructions see
    [https://confluence.csc.fi/pages/viewpage.action?pageId=50177427\#V6kehitysympäristöönliittyminen-Liityntäpalvelimenyhteiskäyttö](https://confluence.csc.fi/pages/viewpage.action?pageId=50177427#V6kehitysymp%C3%A4rist%C3%B6%C3%B6nliittyminen-Liitynt%C3%A4palvelimenyhteisk%C3%A4ytt%C3%B6)
    -   For commercial entities, the organization ID is the same as
        business ID (Y-tunnus)
    -   The named secure server is forgess00.forgeservicelab.fi
    -   The subsystem ID is the one you have used while developing your
        test service unless otherwise desired
    -   The responsible admin for the secure server is NN
2.  Once registration is complete, please notify FORGE Support
    -   FORGE Support will then generate a Certificate Signing
        Request (CSR) for you
    -   This CSR needs to be sent to KaPA administration from your
        organization

3.  Once you have obtained the Sign Certificate corresponding to the
    CSR, please send it to FORGE Support
    -   FORGE Support will notify you once the Sign Certificate has been
        added to the Secure Server.

The Secure Server uses the Sign Certificate to sign requests or
responses carrying your IDs.

Adding test service to FORGE Secure Server
----------------------------------------------------------------------------------------------------------------

Once the registration is complete, please contact FORGE support for
getting service description WSDL added to FORGE Secure Server. This will
require you to add a similar type of firewall rule as above to your
OpenStack Instance, with respect to FORGE secure server
(forgess00.forgeservicelab.fi).

Testing the test service in development KaPA
--------------------------------------------------------------------------------------------------------------------

The same test application used previously can be used to verify the
end-to-end path from client, to secure server, to service. The main
difference is that the request is made to the secure server instead of
the test service directly. Further the end service details (port,
application path) are now masked by the Secure Server. The example here
is based on self-signed certificate on the server side, which the test
app ignores (python request is POSTed with a verify=False flag). The use
of client-side certificates may be required in future/production
versions of KaPA.

    $ python files/kapa-testapp.py -i FI-DEV -l COM -c 0785944-0 -s FORGEDemo -t https://forgess00.forgeservicelab.fi \
                                   -m COM -e 0785944-0 -y TestService -n http://forge-test.x-road.fi/producer
    Received response: Hello test_string! Greetings from adapter server!
    $
