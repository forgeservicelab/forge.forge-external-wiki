![](/files/openstack.png)

OpenStack IaaS platform
==================================================

-------------------------------------------------------------------------------

Getting started with OpenStack
=====================================================================================================

This document assumes the OpenStack IaaS platform is availabe at https://could.forgeservicelab.fi.

This document gives the basic OpenStack usage instruction to get started
after you have credentials to OpenStack IaaS.

 After reading these instructions you can proceed to other FORGE
instructions such as:

-   [security guidelines](#security-guidelines)
-   [launch an instance](#launch-linux-instance)
-   [save a running instance to a
    snapshot](#take-a-snapshot-of-the-instance) which you can use
    to create new instances
-   [creating and registering own image](#create-linux-image)
-   [using block storage](#persistent-storage) i.e. Volumes

Quick overview of the initial steps to use OpenStack
=================================================================================================================================================

OpenStack is the cloud middleware for administration. For the
administration it is possible to use:

 1. [Web user interface](#horizon) called Horizon
 2. [Command line tools](#command-line-tools)

-   Login at least once to the web user interface to get your
    credentials which are also needed for the command line tools.
-   At the same time you can

    -   configure your personal ssh key to login to the virtual machines
    -   check that a suitable security group configuration (firewall)
        exists
-   Then you are ready to start managing virtual machines either with
    web user interface or the command line tools.

    -   Install command line tools if wanted.
    -   If appropriate image is not available then you need to add one.
    -   Launch a virtual machine with wished configuration.
    -   Optionally add a block storage for the Instance and mount it to
        the virtual machine.

Basic concepts
=====================================================================

-   Infrastructure as as Service (IaaS) is a type of cloud computing
    that allows users to quickly setup virtual machines with a set
    amount of resources, attach various types of storage to the machines
    and connect them using virtual networks.

-   **OpenStack**: is the cloud management middleware. It consists of
    several components for managing virtual machines (Nova), networks
    (Quantum), identity (Keystone), virtual machine images (Glance) and
    persistent volume storage (Cinder). There is also a web interface
    for managing most of the other components (Horizon).

-   **Virtual machine** (called also as an **Instance**): a virtual
    machine runs as a process on a physical host server through a
    virtualisation layer. Thus, the physical server resources is divided
    among isolated smaller virtual machines.

    -   Virtual machine runs a guest operating system which can be
        chosen by choosing an Image file when launching an Instance.
    -   Virtual machines can be connected to external IP addresses and
        accessed directly from the Internet.
    -   It is important to take care to security of the virtual machine
        as it would be physical server. Owner of the virtual machine is
        also responsible of the licenses of the virtual machine system.
    -   User is responsible to back-up data. Images and Volumes are
        stored on hardware which has RAID configuration to protect
        against disk breaks.
-   **Virtual network**: One or more virtual networks can run on the
    same physical network. Each project on OpenStack has own
    virtual network.

-   **Image** file: Virtual machine images are the starting point for
    creating new virtual machines.

-   **Snapshot**: A running instance can be saved as a Snapshot which
    can be used as an image to launch new Instances.

-   **Ephemeral disk**: is like a hard drive which lives as long as
    the Instance. It is NOT saved into Snapshot so it is suitable only
    as a temporary disk space.

-   **Volume**: is like a hard drive which can be attached to a single
    virtual machine. It can be detattached and reattached to same or
    another virtual machine without losing data. Data on volume remains
    even if the virtual machine is deleted. This is not the case with
    *ephemeral disk space* which is deleted when the virtual machine
    is deleted. Volume is also faster than ephemeral disk.

-   **Security group** : contains a set of firewall rules that are used
    to control network access to public IP address. Security group is
    selected when launching an Instance.

Horizon
=======================================================

<https://cloud.forgeservicelab.fi>

is address to the FORGE OpenStack web user interface called Horizon.

There you can see for example:

-   Instances: managing your running virtual machines
-   Images and snapshots: the files which you can use to create an
    instance
-   Settings: your personal credentials.
    -   Please note: you cannot change the password via Horizon.

rc file for the nova command line tools
-----------------------------------------------------------------------------------------------------------------------

For command line usage you need to have a personal script file to set
the environment variables.

 You can download it directy in 
<https://cloud.forgeservicelab.fi/dashboard/project/access_and_security/api_access/openrc/>
or by navigating on the web interface, select *Access & Security* , then
select the *API access* tab and click the *Download OpenStack RC File*
button.

When you are going to use the command line tools run

    source openrc.sh

after that it should ask you for a password. Enter the same password as
you had for the web interface. Now you should be able to test the nova
tools by running

    nova image-list

If you see a list of images, the setup of the tools is done. If not see
instructions to install [command line tools](#command-line-tools)

ssh key
-------------------------------------------------------

-   If you are already familiar with SSH keys, you can use your existing
    SSH keys to access the virtual machines.

    -   In the web interface go to Access & Security and from Keypairs
        select Import Keypair.
    -   Name your key, and paste your public key (starts with something
        like "ssh-rsa AAFAA...." or "ssh-dss AFAFA...") into the
        other box.
-   If you have not used SSH keypairs before, you need to create one.

    -   The web interface can take care of this for you.
    -   Go to Access & Security and from Keypairs select Create Keypair.
    -   Give your key a name and click create.
    -   Now you will get a keyname.pem to save.
    -   Save it under your home directory.
    -   Then run the following commands in a shell ( keyname.pem is the
        file you downloaded):

<!-- -->

    mkdir -p .ssh
    chmod 700 .ssh
    mv keyname.pem .ssh
    chmod 400 .ssh/keyname.pem

-   Now you should have what you need to access running instances.
-   DO NOT forget that your local user account might (and most
    likely won't) match that on the computing instance, so it will be
    necessary to specify the target username on the ssh command, e.g.
    for Ubuntu images:

<!-- -->

    ssh ubuntu@<target.OpenStack.floating.IP>

-   Note that ssh keypairs are a security risk as they allow logging
    into your systems without a password. We strongly encourage users to
    add a passphrase to their key. In Linux/OS X this is done as
    follows:

<!-- -->

    ssh-keygen -p -f .ssh/keyname.pem

Security group (firewall)
-----------------------------------------------------------------------------------------

-   Security groups are sets of firewall rules which limit the access to
    your machines.

-   **Please configure firewalls carefully** not to open ports wider
    address space than necessary!

-   In the case of connectivity problems you should make sure both the
    security group and the virtual machine's internal firewall are
    correctly configured.

-   These firewall rules are made on the OpenStack layer and you may
    have additional firewall rules within your virtual machine.

-   Security groups are easiest to edit in the *Access & Security* page
    of the web interface.

    -   Please use unique names for the each group.
-   By default all non-local incoming traffic is denied. You can allow
    additional traffic by creating rules.

-   A rule opens a port range for a set of IP addresses.

-   Note: "From port" and "To port" define a range of destination ports.
    It is not possible to specify the source port.

-   For example, to open the HTTP port to everyone, select the following
    options in the web interface:

<!-- -->

        Protocol   From port   To port   Source group   CIDR
        tcp        80          80        CIDR           0.0.0.0/0

-   To enable complete communication between machines on the same
    network, they must belong to, at least, the "default"
    security group.

-   A machine can be part of one or more security groups. Once a machine
    has been launched, security groups can't be added or removed, but
    you can modify the groups.

-   If the virtual machines might have different firewall rules then it
    best to create new Security Groups as needed and not to modify the
    Default Security Group since changes to that affect on all virtual
    machines which are using that.

After going through the above steps you can continue installing the
command line tools or starting to use the web user interface to [launch
an instance](#launch-linux-instance).

Configuring a subnet
---------------------------------------------------------------------------------

-   If you have a need, you can create a subnet but it is **not
    mandatory**.
    -   Create a network (Subnet)
    -   Please note that for DNS to work you need to add a DNS server in
        Subnet details tab when creating the network. For example:
        193.166.4.24 and 193.166.4.25
    -   You can create a router and attach it to public network by
        clicking Set Gateway button and selecting public from the
        dropdown list.
    -   To associate the subnet to the router on Router tab click Add
        Interface and select your subnet from the drop down list.
    -   Note: If you want to delete what you have created first you have
        to delete the Interface of a Router.

Command line tools
=============================================================================

Installation
-----------------------------------------------------------------

### Installing OpenStack tools with pip

-   OpenStack has a set of python command line clients for each of its
    components, the package names are of the form
    `python-[component_name]client`, where component\_name is one of
    `nova`, `neutron`, `cinder`, etc.

These are the packages and versions for the icehouse release:

-   `python-glanceclient==0.13.1`
-   `python-keystoneclient==0.11.2`
-   `python-neutronclient==2.3.6`
-   `python-novaclient==2.20.0`
-   `python-swiftclient==2.3.1`
-   `python-cinderclient==1.0.9`

Install with:

    $ pip install python-novaclient==2.20.0
    $ pip install python-neutronclient==2.3.6
      ...

### Installation using a package manager

-   Using your system's package manager is by far the easiest way to
    install these tools.
-   The installation procedure varies depending on the operating system
    you are using. Here we give instructions for Ubuntu, Red Hat and OS
    X based systems.

-   Installation under Windows is also possible, but is beyond the scope
    of this guide. Rackspace maintain a guide for Installing
    python-novaclient on Windows.

*Preparation: Ubuntu based systems*

-   The tools listed here should be available in the basic Ubuntu
    repositories, so no extra repositories need to be added. You may
    have to enable some of the repositories in case they are disabled.

*Preparation: Red Hat based systems, EPEL repository*

-   The python-pip packet can be found in the Extra Packages for
    Enterprise Linux repository maintained by the Fedora Project.

-   You can run this command as root on RHEL6 or RHEL6 based systems to
    install the EPEL repository (note! The EPEL repo packages are
    occasionally updated, so this link may not be valid at the time you
    are reading this):

<!-- -->

        rpm -Uv http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

-   Instructions for installing the EPEL repository can also be found
    here in case the command above is out of date:
    <http://fedoraproject.org/wiki/EPEL>

*Preparation: OS X systems*

-   Download the latest python setuptools.
-   Install the tools and pip:

<!-- -->

        sudo python ez_setup.py
        sudo /usr/local/bin/easy_install pip

-------------------------------------------------------------------------------

Create Linux image
=================================================================

Linux image is a virtual disk image which contains files needed to
launch an instance of it. An instance is a Linux operating system booted
up using a specific Linux image. We have created couple of plain Linux
images for your convenience which you can use to launch instances from.
You can also create your preferred Linux image by using either OpenStack
GUI (Horizon) or OpenStack CLI tools.

Using OpenStack GUI to create an image
---------------------------------------------------------------------------------------------------------

Login to the OpenStack with your credentials and go to **Images &
Snapshots tab**. Select **+ Create image** and select **Image File**
from **Image Location** .

 You can either load the image from local file system or from url.

For instance the latest Ubuntu Quantal image is available at

    http://uec-images.ubuntu.com/quantal/current/quantal-server-cloudimg-amd64-disk1.img

OpenStack document in
<http://docs.openstack.org/image-guide/content/ch_obtaining_images.html>
has more information about obtaining images. After you have successfully
created an image you can launch an instance of it as described in
[Launch Linux image](#launch-linux-instance).

Using CLI tools to create an image
-------------------------------------------------------------------------------------------------

Using CLI tools will give you more flexibility in terms of managing your
instances. In order to use OpenStack CLI tools, you have to have your
keypair set, rc file downloaded and in use and OpenStack CLI tools
installed. Follow the instructions from [Getting started with
OpenStack](#getting-started-with-openstack). You can then download an
image of your choice. An example below is using a Linux image with
WordPress set up provided by Turnkey.

    # cd /tmp
    # wget http://mirrors.gigenet.com/turnkeylinux/openstack/turnkey-wordpress-13.0-wheezy-i386-openstack.tar.gz

Then you can unpack the tar file and upload needed image files (initrd,
kernel and associated image) to OpenStack Glance.

### Unpack files

    # cd /tmp
    # tar xvzf turnkey-wordpress-13.0-wheezy-i386-openstack.tar.gz
      turnkey-wordpress-13.0-wheezy-i386/
      turnkey-wordpress-13.0-wheezy-i386/turnkey-wordpress-13.0-wheezy-i386.img
      turnkey-wordpress-13.0-wheezy-i386/turnkey-wordpress-13.0-wheezy-i386-initrd
      turnkey-wordpress-13.0-wheezy-i386/turnkey-wordpress-13.0-wheezy-i386-kernel

    # IMG=turnkey-wordpress-13.0-wheezy-i386

### Add initrd

    # glance image-create --is-public=false --container-format=ari --disk-format=ari --name="$IMG-initrd" < ./$IMG/$IMG-initrd

    +------------------+-------------------------------------------+
    | Property         | Value                                     |
    +------------------+-------------------------------------------+
    | checksum         | fa51b188b176bee5ff84b9e8446dfe3e          |
    | container_format | ari                                       |
    | created_at       | 2014-02-27T14:26:01                       |
    | deleted          | False                                     |
    | deleted_at       | None                                      |
    | disk_format      | ari                                       |
    | id               | 5b04d9ae-5485-44f2-88df-87df41cfa5f9      |
    ...
    ...


    # RAMDISK_ID=5b04d9ae-5485-44f2-88df-87df41cfa5f9

### Add kernel

    # glance image-create --is-public=false --container-format=aki --disk-format=aki --name="$IMG-kernel" < ./$IMG/$IMG-kernel

    +------------------+-------------------------------------------+
    | Property         | Value                                     |
    +------------------+-------------------------------------------+
    | checksum         | 229e87089b2856370bcaed81b77f7ada          |
    | container_format | aki                                       |
    | created_at       | 2014-02-27T14:29:49                       |
    | deleted          | False                                     |
    | deleted_at       | None                                      |
    | disk_format      | aki                                       |
    | id               | 87e8beeb-aa44-4739-9e0d-1d38e2eeaa5f      |
    ...
    ...

    # KERNEL_ID=87e8beeb-aa44-4739-9e0d-1d38e2eeaa5f

### Add image and associate it with initrd and kernel

    # glance image-create --is-public=false --container-format=ami --disk-format=ami --prop ramdisk_id=$RAMDISK_ID --prop kernel_id=$KERNEL_ID --name="$IMG" < ./$IMG/$IMG.img

    +-----------------------+--------------------------------------+
    | Property              | Value                                |
    +-----------------------+--------------------------------------+
    | Property 'kernel_id'  | 87e8beeb-aa44-4739-9e0d-1d38e2eeaa5f |
    | Property 'ramdisk_id' | 5b04d9ae-5485-44f2-88df-87df41cfa5f9 |
    | checksum              | fd172a01631afcdd22d390c07b848849     |
    | container_format      | ami                                  |
    | created_at            | 2014-02-27T14:36:20                  |
    | deleted               | False                                |
    | deleted_at            | None                                 |
    | disk_format           | ami                                  |
    | id                    | 6ab6f083-a563-481d-a8ef-ef1b90d20116 |
    | is_public             | False                                |
    | min_disk              | 0                                    |
    | min_ram               | 0                                    |
    | name                  | turnkey-wordpress-13.0-wheezy-i386   |
    | owner                 | digile                               |
    | protected             | False                                |
    | size                  | 1005404160                           |
    | status                | active                               |
    | updated_at            | 2014-02-27T14:36:46                  |
    +-----------------------+--------------------------------------+

Uploading a ready image
---------------------------------------------------------------------------

If you have an image file readily available, which you do not need to
modify by yourself as above, you can upload it in simpler way:\

` glance image-create --is-public false --container-format bare --disk-format qcow2 --name "TunedCentOS65" < ./some_image_file.iso`

After you have successfully created an image you can launch an instance
of it as described in [Launch Linux image](#launch-linux-instance).

-------------------------------------------------------------------------------

Image update and retention policy
================================================================================================================

Following is a list of the cloud image distributions fully supported by
the Forge Service Lab team. Supported images will be available on
OpenStack and backed by Forge Service Lab team. Images not listed under
the Supported images heading will not have any kind of support in any
way.

Supported images
------------------------------------------------------------------------------

At the time of this writing, the following distribution cloud images are
fully supported on Forge ServiceLab:

-   **Ubuntu LTS:** Version 12.04 (Precise Pangolin) and newer LTS
    releases
-   **Debian:** Version 7.3 (Wheezy) and newer
-   **CentOS:** Version 6.5 and newer

Update policy
------------------------------------------------------------------------

Images are automatically built with latest upgrades and security
advisories **twice a month**. A {DEPRECATED}- prefix is added to the
name of images which have been superseded by a newer build.

### Ubuntu

Ubuntu images will be maintained according to Ubuntu's Long Term Support
release cycle.

### Debian

Debian images will be maintained according to Debian's revision release
cycle.

### CentOS

CentOS images will be maintained according to CentOS' release cycle.

Retention policy
------------------------------------------------------------------------------

In general, images will be retained until they reach their scheduled End
Of Life.

### Ubuntu

Ubuntu Long Term Support images will be kept available until support
from Canonical is dropped. Version 12.04 (Precise Pangolin) will be
retained during its lifespan and side by side with 14.04 LTS (Trusty
Tahr). When Canonical releases 16.04 LTS in the future, they will drop
support for 12.04 and so will we.

### Debian

Debian images will be kept available until they are dropped from
oldstable status. Version 7 (Wheezy) will be retained during its
lifespan and oldstable status side by side with Debian 8 (Jessie). When
debian releases Debian 9 as stable and Debian 8 (Jessie) is moved to
oldstable, support for Debian 7 (Wheezy) will be dropped.

### CentOS

CentOS images will be kept available until their maintenance support is
discontinued. CentOS 6 will be retained during its lifespan side by side
with CentOS 7.

Other Sources
------------------------------------------------------------------------

This is a convenience link to OpenStack's documentation on cloud image
repositories. The images listed on this resource are not supported by
the Forge Servicelab team in any way and you use them at your own risk.

-   <http://docs.openstack.org/image-guide/content/ch_obtaining_images.html>

-------------------------------------------------------------------------------

Create CentOS image
======================================================================

The purpose of this document is to cross the t's and dot the i's from
[This CentOS image creation example from OpenStack's
documentation](http://docs.openstack.org/image-guide/content/centos-image.html).

While following the guide, note that on the step regarding disk
partitioning you really **do want** to take the alternative route and
**create a single ext4 partition, mounted to "/"** otherwise the root
partition will fail to grow according to flavour.

We'll take over the
[guide](http://docs.openstack.org/image-guide/content/centos-image.html)
after rebooting the instance and logging in for the first time.

### Enabling the EPEL repositories

Some of the packages needed for interaction with the cloud
infrastructure are only available from the EPEL repos, enable them by
running

    # rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

### Installing the growroot module and enabling resizing

The growroot binaries fromt the
[cloud-initramfs-tools](https://launchpad.net/ubuntu/+source/cloud-initramfs-tools)
package have been backported to EPEL into the
[dracut-modules-growroot](https://apps.fedoraproject.org/packages/dracut-modules-growroot)
which is a module for the dracut initramfs system, this means we'll have
to recreate the initial ramdisk.

    # yum install dracut-modules-growroot
    # dracut -f -m all

### Installing cloud-init

The [cloud-init](https://apps.fedoraproject.org/packages/cloud-init)
package available on the EPEL repositories is, as of this writing, a bit
outdated and doesn't quite work with OpenStack (although version
0.7.4-2.el6 is in testing and should work fine once it's released). It
is recommended then to install the [updated
version](http://repos.fedorapeople.org/repos/openstack/cloud-init/epel-6/)
provided by fedorapeople.

    # rpm -Uvh http://repos.fedorapeople.org/repos/openstack/cloud-init/epel-6/python-boto-2.6.0-1.el6.noarch.rpm
    # rpm -Uvh http://repos.fedorapeople.org/repos/openstack/cloud-init/epel-6/cloud-init-0.7.2-2.el6.noarch.rpm

Note that this last command will fail due to missing dependencies. Make
sure to install them via `yum` and retry.

### Disable the zeroconf route

In order for the instance to access the metadata service, disable the
default zeroconf route:

    # echo "NOZEROCONF=yes" >> /etc/sysconfig/network

### Configure console

In order for nova console-log to work properly on CentOS 6.x, guests you
may need to add the following lines to `/boot/grub/menu.lst`

    serial --unit=0 --speed=115200
    terminal --timeout=10 console serial
    # Edit the kernel line to add the console entries
    kernel ... console=tty0 console=ttyS0,115200

### Cleanup MAC address details

First remove udev rules:

    # rm /etc/udev/rules.d/70-persistent-net.rules

Then edit the `/etc/sysconfig/network-scripts/ifcf-eth0` file and remove
the lines starting with `HWADDR` and `UUID`, additionally append the
following line:

    PERSISTENT_DHCLIENT=yes

### Add the cloud-user account and grant its permissions

The installed cloud-init package uses a default user named `cloud-user`,
we need to create this account and add it to the `wheel` group to make
it management-capable.

    # useradd cloud-user
    # usermod -a -G wheel cloud-user

Now we'll want to ensure that members of the `wheel` group have
execution rights on all commands, with no password, run `visudo` and
ensure the following line is not commented out:

    %wheel        ALL=(ALL)       NOPASSWD: ALL

We don't need to explicitly set a password for the `cloud-user` account
as console login will be disabled by cloud init.

### Clean Up

Remove install log files:

    # rm -f /root/*

Remove system logs from first run:

    # find /var/log -type f -delete

Lock the root account:

    # passwd -l root

Clear the command history and shut down the instance:

    # history -c
    # halt

The image is now ready and you can continue to upload it to glance.

-------------------------------------------------------------------------------

Launch Linux instance
==========================================================================

Readily Available images
--------------------------------------------------------------------------------

Following is the list of images made available and fully supported by
the Forge Servicelab team. The list of available images will be
evolving, please see the [Image update and retention
policy](#image-update-and-retention-policy) for more information.

  ID                                     Name                        Disk Format
  -------------------------------------- --------------------------- -------------
  70c1723b-ef3f-4056-adee-aea3e5b3b4a2   Ubuntu-14.04-server-amd64   qcow2
  dc615573-7134-4b56-a152-262b92904067   Ubuntu-12.04-server-amd64   qcow2
  99077ebd-978b-40a7-9787-f44f0fbafdcf   Debian-7.7-server-amd64     qcow2
  e9734856-5e92-4ac8-aa6b-b3164e845f7e   CentOS-6.5-server-x86\_64   qcow2
  b359649f-e61c-4fc8-85de-3ec923eeff9c   CentOS-7                    qcow2

Using OpenStack GUI to launch an instance
------------------------------------------------------------------------------------------------------------------

Login to the OpenStack with your credentials and go to **Images &
Snapshots** tab. Select the image (to be used for launching an instance)
from the list of existing images or create a new image according to
instructions in [Create Linux image](#create-linux-image) first. Press
**Launch** and then provide following parameters when asked

    - Details: The name for the new instance and other parameters. 
      - Please note that
        - the "Boot from image (creates a new volume)" is not supported. You can create the Volume separately in normal manner and to associate it to the instance.
    - Access & Security: SSH keypair and security group
    - Networking: Select the network to be used
    - Post-Creation: You can define the customization script that runs after you instance launches

Launch the instance and wait for it to load and then make your instance
accessible by using GUI tools.

Using CLI tools to launch an instance
----------------------------------------------------------------------------------------------------------

After you have your credentials set and CLI tools installed you can list
available images and instance flavors and other information you might
want to specify by using CLI tools:

    $ nova image-list
    $ nova flavor-list
    $ nova keypair-list
    $ nova secgroup-list

Then you can launch your instance using the desired image and flavor by
issuing the following command.

    $ nova boot --flavor FLAVOR_ID --image IMAGE_ID --key_name KEY_NAME \
      --security_group SEC_GROUP NAME_FOR_INSTANCE  SERVER_NAME

However, if you have several networks, you have to find the correct ID
of the network and add it as a boot parameter as well:

    $ nova network-list
    $ nova boot --flavor FLAVOR_ID --image IMAGE_ID --nic net-id=NW_ID --key_name KEY_NAME \
      --security_group SEC_GROUP NAME_FOR_INSTANCE  SERVER_NAME

For more options please see

    nova help boot

Adding an Internet IP address
------------------------------------------------------------------------------------------

To access to the launched instance with SSH you have to

-   associate the instance with an IP (so called Floating IP)
-   configure a security group i.e. firewall as discussed in [Getting
    Started](#getting-started-with-openstack) page.

### OpenStack web user interface

-   click More button on the Instance row and there select Associate
    Floating IP.
-   select an IP address from the dropdown list if there is any.
-   if the list does not yet contain any IP, then click +-button to
    allocate a new IP. There opens a pop up where you can allocate
    an IP.

Please note: it may take a moment that the address gets associated. You
might also need to refresh the Instance web page to see the newly
associated address.

### Command line

To add an already allocated IP:

    $ nova list
    $ nova floating-ip-list
    $ nova add-floating-ip INSTANCE_NAME_OR_ID FLOATING_IP

If the floating-ip-list does not show any IPs which are not associated
to an Instance, then you can allocate more IPs from the pool assuming
the pool has still some left.

    $ nova floating-ip-pool-list
    $ nova floating-ip-create <name of the pool given by the previous command>

Logging in via ssh
--------------------------------------------------------------------

Image vendors have typically set the default username and password to be
used when logging in with SSH. "root" account is commonly disabled for
SSH logins.

  Vendor             ssh login
  ----------------- ------------
  ubuntu            ubuntu
  CentOS &lt; 6.5   cloud-user
  CentOS &gt; 7     centos
  debian            debian

OpenStack injects the SSH key you selected during instance definition
for the "ubuntu" account, therefore you are able to login as a "ubuntu"
user. Anyhow, if you need to have "root" account enabled (e.g. for
provisioning needs) for ubuntu images then you could enable SSH for
"root" by writing a following script into the file mydata.file and. You
can then use this file as an argument to the --user-data parameter when
issuing "nova boot" command as described earlier.

    #!/bin/sh
    LOG_FILE=/var/log/userdata-script.log

    # Close STDOUT file descriptor
    exec 1<&-
    # Close STDERR FD
    exec 2<&-

    # Open STDOUT as $LOG_FILE file for read and write.
    exec 1<>$LOG_FILE

    # Redirect STDERR to STDOUT
    exec 2>&1

    sed -i 's/.*\(ssh-dss.*\)/\1/' /root/.ssh/authorized_keys   # in case use use dss keys
    sed -i 's/.*\(ssh-rsa.*\)/\1/' /root/.ssh/authorized_keys   # in case you use rsa keys

Updating software in Linux instance 
-------------------------------------------------------------------------------------------------------

Linux distributions evolve in time and it's probable that there are
already upgrades available for your Linux instance after you have
launched it. It's recommended to upgrade the software in your Linux
instance frequently.

For Ubuntu based instances, you can issue a command inside the instance

    $sudo apt-get update; apt-get upgrade

Provisioning the instance with your application
------------------------------------------------------------------------------------------------------------------------------

Finally is should be possible to provision your instance with wanted
applications and features (e.g. by using
[Ansible](4_Continuousdelivery.md#ansible)
and finally provide others access to the instance by reconfiguring the
security group rules.

-------------------------------------------------------------------------------

Using storage
==========================================================

-------------------------------------------------------------------------------

Root disk
====================================================

Some instance storage (a.k.a. root disk) is available after you have
launched an instance. The size of the storage depends on the flavor you
are using. The instance storage concept is similar to a root disk and it
typically contains at least an operating system and applications. You
might want to store some temporary data on to the instance storage and
that data exists as long as the instance exists. After you terminate the
instance then the instance storage disappears too. You can use snapshots
to make
[backups](#take-a-snapshot-of-the-instance)
of the instance storage.

The size of the instance storage is typically pretty limited and you
might need to consider other storage options (e.g. ephemeral) for big
data use cases. You might also need to consider other storage options
(e.g. persistent) for the sake of data persistence.

------------------------------------------------------------------------

Ephemeral storage
============================================================================

Depending on the flavors that are available for you, there might be
ephemeral storage which you can take into use. It is like a hard drive
which lives as long as the instance and therefore it's not persistent.
Also, it is not saved along with the snapshot so it is suitable only as
a temporary disk space e.g. for big data computational use cases. If you
terminate the instance, the ephemeral storage disappears too.

Ephemeral storage becomes available during instance boot time as a
/dev/vd{b} device node and it can be mounted similarly to a block
device. Some Linux images (e.g. Debian) are configured to mount it on
/mnt. By default ephemeral disks are configured as XFS partitions
because ext4 has issues with over 16TB partitions. Please have xfsprogs
package installed in your operating system image so that XFS partitions
can be mounted and modified. Before you can start using the ephemeral
storage, you have to mount it if it's not automatically mounted by your
operating system.

------------------------------------------------------------------------

Persistent storage
===================================================================

Introduction
-------------------------------------------------------

-   Volumes are block storage capacity, which is like a hard drive
    attached to you server.
-   A new Volume needs a file system that it can be mounted to a
    virtual machine. That is done on the virtual machine.

-   A volume can be attached to a single instance at a time.

-   It is possible to detach a Volume and attach it to another instance.
    The data remains on the volume.

-   You can have multiple volumes.

-   You can delete the unnecessary Volumes.

*Please note* that taking snapshot of a volume is not possible despite
there being such function on the web user interface.

Creating a Volume
-----------------------------------------------------------------

-   You can specify the size of the volume and name for it.
-   A brand new volume does not even have a file system so you need to
    create that first. Then it is possible to mount to an instance.
-   If you get an error, it usually means that the device is already
    used so you need to write another one.
    -   Please note: the operating system might use different device
        that what cloud middleware shows.

### Horizon

-   It also asks a device name which you need to give such as `/dev/vdc`
    but it does not really matter. The new device will be visible as the
    first free virtual block device on the instance. Usually this is
    `/dev/vdb` or `/dev/vdc`.

### Command line tools

-   nova help : to see the all parameters including the volume related.
    -   Detailed help of a parameter: nova help volume-create
-   To create a Volume:
    `nova volume-create --display-name <some text> <size in GBs>`
-   To list Volumes: `nova volume-list`
-   To see your Instances and their IDs: `nova list`
-   To mount a Volume to a VM:
    `nova volume-attach <Instance ID> <Volume ID> /dev/vdc`
    -   The last parameter defines a suggested device name. Command will
        give an error the name was already in use.

### On the virtual machine

-   When you login to the virtual machine you can see the Volume with
    `sudo fdisk -l`
    -   Please note that the device e.g. `/dev/vdc` might not be the
        same as shown by the cloud middleware.
    -   In case you do not see the volume, try rebooting the
        virtual machine.
-   For a new Volume you need to create a file system for example:
    `mkfs.ext3 /dev/vdc`
-   Then you can mount it to a directory for example:
    `mount /dev/vdc /mnt/datadir`

Mount volume partition automatically on boot
-----------------------------------------------------------------------------------------------------------------------

-   first create and format a partition on a cinder volume
-   add label to your partition

<!-- -->

    # in case you use ext{n} fs
    $ sudo e2label /dev/vbd1 my_partition_label

-   or find out UUID of your partition:

<!-- -->

    $ blkid | grep vdc1
    /dev/vdc1: UUID="e98cbc3d-d5b3-4d0e-9dc0-43da6141ea68" TYPE="ext4"

-   add a line to fstab

<!-- -->

    # Fields:
    # partition_lookup mount_path filesystem_type mount_options dump fsck
    # example attaching the above labeled partition to /data:
    LABEL=my_partition_label   /data                   ext4    defaults        0 0
    # example attaching UUID-specified partition to /scratch
    UUID=e98cbc3d-d5b3-4d0e-9dc0-43da6141ea68   /scratch                   ext4    defaults        0 0

Detaching a Volume
-------------------------------------------------------------------

### First on the virtual machine

-   First remember to unmount the volume on the virtual machine
    operating system for example: `umount /mnt/datadir`

### Horizon

-   On the Volumes choose the right volume and click **detach volume**.

### Command line tools

-   To detach the volume: `nova volume-detach <Instance ID> <Volume ID>`

Showing Volume details
---------------------------------------------------------------------------

### Horizon

-   The details are on the Volumes tab.

### Command line tools

-   `nova volume-list` : list the volumes of the project.
-   `nova volume-show <Volume ID>` : show the details of the volume.

------------------------------------------------------------------------

Object storage
=======================================================

This page is about **OpenStack Swift** Object Storage service which is
**in beta testing**.

Usage scenarios
---------------------------------------------------------

-   Data *Objects* such as images, documents are stored into a
    *Container*
    -   It is possible to store directories as well
    -   It is possible to assign *metadata* (key - value pair such
        as subject:cat) to an Object or a Container
-   It is a storage, not as a mounted work directory so the data needs
    to be downloaded to a mounted disk space before using it
    in computation.

### Security

-   Failure tolerance against disk and server breaks in done
    automatically with replication. Also in this storage there is no
    liability of data losses so back up your important data. If data is
    deleted it cannot be recovered.

-   Owner of the data can control read and write access permissions.

-   Containers and their content are accessible inside the Project

Usage via Horizon web user interface
---------------------------------------------------------------------------------------------------

-   On Horizon there is Object Storage section with Containers tab.
-   There you can

    -   *create* and *delete* Containers
    -   *delete* an Object. It is not possible to delete a Container if
        it contains objects.
    -   *upload* an Object. Unfortunately it is not possible to upload a
        file keeping its name automatically without retyping it. If you
        want to store it under a folder you can define it in the name
        field e.g. /cars/image1.jpg
    -   *download* an Object. Depending on you operating system and
        browser it might be able to open a known format directly without
        need to save it to the disk first.
    -   DO NOT USE COPY functionality. It does not seem to
        work properly.
-   It is *not* possible to

    -   rename and existing Container or Object. It is easy to make a
        copy of an Object though.
    -   copy a Container or to copy multiple files at once
    -   set access control limitations or metadata

Usage with command line tools
-------------------------------------------------------------------------------------

-   For command line there is swift client. For example via pip system:
    `pip install python-swiftclient`
    -   When using `swift` if you get
        `Auth version 2.0 requires python-keystoneclient` then run
        `pip install python-keystoneclient`
-   upload file or directory or several separated by space: swift upload
    -   if container is not yet existing it will be created.
-   show information e.g. bytes and metadata of a container or an
    Object:
    -   `swift stat [container [object]]`
-   list the containers: swift list
-   list the objects in container: `swift list <container>`
-   add a metadata to an object or container:
    `swift post -m <key>:<value> <container> <object>`
-   delete container or object: `swift delete <container> [<object>]`
-   Containers can have read and write permissions for all. This feature
    needs still testing and documentation ( ref.
    <http://blog.fsquat.net/?p=40> ).

API access
-----------------------------------------------

-   For software development have a look at
    <http://docs.openstack.org/api/openstack-object-storage/1.0/content/>

-------------------------------------------------------------------------------

Take a snapshot of the instance
========================================================================================================

Backup your running Linux instance
--------------------------------------------------------------------------------------------------------------

If you want the make a backup of your running Linux instance then you
can use OpenStack's snapshot feature. You can see the list of instances
from OpenStack GUI when you select **Instances** menu. For each instance
you can also see the option to **Create Snapshot**. You can use either
GUI or CLI tools to take the snapshot. If you use CLI tools, then you
can list your instances by issuing following command.

Please note! The snapshot feature makes a snapshot of the rootdisk only
and e.g. ephemeral storage and persistent storage won't become a part of
the snapshot.

    # nova list

Freeze the instance before creating a snapshot
--------------------------------------------------------------------------------------------------------------------------------------

A snapshot captures the state of the file system, but not the state of
the memory. Therefore, to ensure your snapshot contains the data that
you want you might want to flush buffers and freeze the file system
state. Please read carefully from OpenStack documents
<http://docs.openstack.org/trunk/openstack-ops/content/snapshots.html>
how to take snapshots safely. You can freeze your selected instance by
issuing following command **inside the instance**

    # sync
    # apt-get install util-linux 
    # fsfreeze -f /mnt (assuming your persistent block storage /dev/vdb is mounted on /mnt inside your instance)

Using OpenStack GUI to take a snapshot
----------------------------------------------------------------------------------------------------------------------

After you have frozen your instance, you can use select **Create
Snapshot** from OpenStack GUI to create actual snapshot. You have to
provide the name for the new snapshot.

Using CLI tools to take a snapshot
--------------------------------------------------------------------------------------------------------------

After you have frozen your instance, you can create actual snapshot
using CLI tools.

    # nova image-create [instance name or uuid] [name of new image]

Unfreeze the instance after the snapshot was created
--------------------------------------------------------------------------------------------------------------------------------------------------

Finally after the snapshot is taken, you can unfreeze your instance back
to normal by issuing the following command **inside the instance**

    # fsfreeze -u /mnt

Make a snapshot of your customized Linux image
--------------------------------------------------------------------------------------------------------------------------------------

It's possible to customize Linux images according to your own needs and
then utilize these images later by launching instances out of customized
images. Follow instructions in
[Customize\_Linux\_image\_using\_Puppet](#customize-linux-image-using-puppet)
in order to create your customized Linux image. Then follow steps above
to "Backup your running Linux instance". You will get the image snapshot
of your customized Linux image which you can use in order to launch
instances of it.

Note! During first run, the instance may run some initial configuration
scripts provided by the image vendor. Typically these scripts are
executed only once during first run. You should take these potentially
already made configurations into account and think if you need to
reconfigure something or reset certain configurations back to how they
were before first run. E.g. if you are going to make a snapshot of
CentOS images, then it's advised to follow steps below.

Making Snapshot of your CentOS instance
------------------------------------------------------------------------------------------------------------------------

Before taking snapshot of your CentOS instance following steps should be
executed.

1 Modify root authorized\_keys file so that you can ssh with root

    >sudo su
    >vi /root/.ssh/authorized_keys
     Remove no-port-forwarding,no-agent-forwarding,no-X11-forwarding,command="echo 'Please login as the user \"cloud-user\" rather than the user \"root\".';echo;sleep 10"
     so that line starts with ssh-rsa

2 Login with root and make modifications to instance. The cloud-user
deletion is **not** mandatory but if snapshot will be launched by other
users your ssh key will be left in authorized\_keys file and you are
also able to login in than instance. In some cases this might be even
wanted behaviour. Please remember that the same issue is with root users
authorized\_keys file.

    >vi /etc/sudoers
     add following line that allows cloud-user to sudo su without password
       cloud-user   ALL=(ALL)       NOPASSWD:ALL
    >userdel cloud-user      #make a copy if you have data that need to saved
    >rm -rf /home/cloud-user # cloud-user will be created in cloud.init script
    >rm -r /lib/udev/write_net_rules # prevents 70-persistent-net.rules from being created
    >vi /etc/udev/rules.d/70-persistent-net.rules
     comment out
       SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="fa:16:3e:54:b6:72", ATTR{type}=="1", KERNEL=="eth*", NAME="eth0"

     Verify that the the following line exist in /etc/sysconfig/network :
     NOZEROCONF=yes

3 Now you can create snapshot from the instance

-------------------------------------------------------------------------------

Security guidelines
======================================================================

-   This page contains instructions on how to operate safely in the
    FORGE environment.
    -   Please send improvement suggestions and useful tips to be added
        to this page!

General important security instruction
------------------------------------------------------------------------------------------------------------

-   Virtual machine security is as important as the security of a
    physical server.
-   The user is responsible for the administration of the operating
    system and the applications in the virtual machine.

    -   Feel free to ask for help in security issues - especially those
        related to the cloud middleware.
-   Remember to **save the virtual machine** as a Snapshot (image) that
    you do not loose the changes made after launching the virtual
    machine if a hardware break or other incident causes losing of the
    virtual machine.

Credentials
------------------------------------------------------

-   Do not share your credentials with others.
-   If your FORGE password is compromised contact the FORGE
    helpdesk immediately.

Suspected security breach
----------------------------------------------------------------------------------

-   If you have discovered a critical security flaw in the FORGE system
    or believe your machine has been compromised, please contact the
    FORGE helpdesk immediately.

Firewall rules
------------------------------------------------------------

-   **Restrict access to the instance as much as possible.** Only allow
    connections from those IP ranges that are necessary.

    -   For example: If your instance is being used only from a single
        IP or a small subnet where your are developing a service you
        should allow access only from those IPs.
    -   For example: To allow the host 192.12.13.14 to access ssh port
        22 add a TCP rule with 192.12.13.14/32 as the source range and
        22 as the destination port.
    -   Hint: especially if your workstation is behind NAT, you can
        check your IP by surfing into <http://www.whatismyip.com/>
    -   List of typical netmasks:
        <http://en.wikipedia.org/wiki/Subnetwork#Subnet_and_host_counts>
-   Each project has its own security groups in OpenStack. A security
    group contains a set of firewall rules: port number, UDP/TCP and the
    port range to which it applies.

-   One or more security groups are associated to an instance when you
    create it.

-   It is possible to modify the rules of the security group and those
    changes will apply to the running instances using that
    security group.

    -   Warning: If you or your colleagues in your project modify the
        rules in a security group, those changes are applied directly to
        all the project's instances which use that security group.
-   If you anticipate that you will have instances with different kinds
    of firewall rules, create a new security group e.g. just for a
    single instance.

-   Do not add all of your firewall rules to the default security group
    and then use just that for all instances if some of the instances do
    not need those rules.

-   Only assign a floating IP to those instances that need it. In many
    cases, you can also access instances from your project's
    internal networks.

    -   In typical architecture only the web frontends need to be
        reachable from the Internet whereas a database server does not
        need a public IP.
-   By default your instances do not have a firewall between each other.

-   In addition to the OpenStack firewall it is also good to use the
    instance's own operating system firewall.

Running services on virtual machines
--------------------------------------------------------------------------------------------------------

-   Please consider that a misconfigured SMTP server is a good target
    for spammers. Thus, you should use external SMTP services.

Data security
----------------------------------------------------------

-   No backups are taken. The user is responsible for their data.
-   As was already mentioned above, remember to save the virtual machine
    as a snapshot that you can launch a new virtual machine by using a
    snapshot if the virtual machine dies.
-   Images, snapshots and volumes are on a RAID secured system.
    -   Please note that the human errors of administrators or project
        members can also delete data.
-   Although some components are redundant, there is always a risk that
    a running instance is lost due to a hardware error on the host.

Security inside your project
----------------------------------------------------------------------------------------

-   Inside a project the administrators need to trust each other.

    -   There are no master admin roles: all users inside a project have
        equal permissions.
    -   For example, any project member can open the console view of any
        of the project's instances.
-   **Project members can manage (delete, reboot, use etc.) all of that
    project's resources** (instances, volumes, security groups etc.).

    -   Hint: **Name your resources clearly** e.g. MattiIUbuntu so that
        you can identify your own and not delete or use another
        user's resources.
-   Resource quotas are per project and thus shared by the
    project's members.

Operating system administration
----------------------------------------------------------------------------------------------

-   It is recommended that you enable automatic updates.

    -   In all but a few special cases, Linux kernel updates always
        require a reboot. You can configure email alerts for when a
        machine needs to reboot for a kernel update. You can also set a
        machine to reboot automatically.
-   Allowing root to login through SSH is unnecessary. Disable it
    under /etc/ssh/sshd.conf.

-   Use good passwords. Pass and store them in secure manner. Always
    change default passwords.

    -   You should use SSH keys protected by a passphrase instead of
        passwords for virtual machines provisioned by OpenStack. See for
        example: <https://kimmo.suominen.com/docs/ssh/>
    -   Never store SSH private keys or any other personal credentials
        on instances.
-   Remove unneeded accounts.

-   Disable those services that you do not need.

    -   For example on RHEL / CentOS: chkconfig --list
-   There are tools like denyhosts, fail2ban etc. for banning IP
    addresses that try to connect but fail to authenticate repeatedly.

-   It is possible to send log files to a central log server.

-   General Linux checklist:
    <https://www.sans.org/score/checklists/linuxchecklist.pdf>

-   Ubuntu security guidelines:
    <https://help.ubuntu.com/community/Security>

-   Red Hat's security guide:
    <https://access.redhat.com/site/documentation/en-US/Red_Hat_Enterprise_Linux/6/pdf/Security_Guide/Red_Hat_Enterprise_Linux-6-Security_Guide-en-US.pdf>

Application level security
------------------------------------------------------------------------------------

-   Make sure that applications are configured correctly and software is
    up to date with security updates applied.
-   Apache security tips:
    <http://httpd.apache.org/docs/current/misc/security_tips.html>
-   Various checklists for auditing your software environment:
    <https://benchmarks.cisecurity.org>
-   Important security news and vulnerabilities in Finnish:
    <https://www.cert.fi/>
-   "The ultimate security vulnerability datasource":
    <http://www.cvedetails.com/index.php>
    -   Hint: Many Linux distributions have their own mailing list to
        announce available security updates. For example :
        <http://www.ubuntu.com/usn/>

Trusted web application
------------------------------------------------------------------------------

In case you want to write a trusted web application, then you might want
to consider supporting https protocol and ensure that web browsers have
a means to trust your web application. In that case you need to install
host certificates into the server.

------------------------------------------------------------------------

Security overview
================================================================

This page aims to summarise the IaaS platform level security practices.

This page is *not* a replacement or amendment of the contracts made. The
contract overrides this page in case of conflicting information.

FORGE Affiliates are responsible to administrate their virtual machines
and to obey Terms and Conditions and security guidelines of the user
documentation.

FORGE IaaS Platform Security Overview
--------------------------------------------------------------------------------------------------------

The IaaS platform for DIGILE’s FORGE service is delivered by CSC – IT
Center for Science, a company owned by the Ministry of Education and
Culture ([www.csc.fi](http://www.csc.fi)). The cloud service is a
community cloud i.e. dedicated for the FORGE users. The IaaS platform
consists of the servers, storage and networking equipment as well as
cloud middleware.

Regulatory compliance
------------------------------------------------------------------------

Although the FORGE IaaS platform is not yet officially audited and thus
does not formally conform to any particular security standards, best
security practices are followed and
[Vahti](https://www.vahtiohje.fi/c/document_library/get_file?uuid=d67d2721-38f3-4db6-a05b-a14901fb6843&groupId=10128&groupId=10229)
protection level IV is targeted (not audited). The datacenter facility
has been ISO/IEC 27001 certified.

Physical security
----------------------------------------------------------------

The datacenter is in Kajaani. In the same large building are also other
companies’ data center facilities. The hardware is located in a data
center module accessible only by CSC administrators and the
subcontractors who have signed a security contract with CSC.

Service Level Agreements
------------------------------------------------------------------------------

There is no guaranteed availability of the system but especially the
central components are designed to be robust. Problem solving is done
during office hours on weekdays.

End-user access
------------------------------------------------------------

Forge manages the users and the projects of the cloud middleware.\
 The cloud middleware uses FORGE centralized password management system
enabling to use same user name and password as for the other FORGE
services.

The virtual machines including their user accounts are administrated by
the user.

Multi-tenancy
--------------------------------------------------------

The networks of the projects are separated logically in their own
virtual local area networks (VLAN). Any access between projects must be
explicitly allowed. Access to cloud resources is restricted on a project
basis.

Network security
--------------------------------------------------------------

All interfaces to the cloud middleware use encrypted HTTPS (SSL/TLS),
and firewalls are used where applicable.

FORGE Affiliates are responsible for configuring the firewall rules on
the cloud middleware and in the virtual machines and to take care of
securing their data transfer over the Internet

System administration
------------------------------------------------------------------------

Network access to manage the cloud services is restricted, and relies on
two-factor authentication.

The administrative accounts for the service are centrally managed.
Configuration management tools are used for the whole system, and all
configuration is stored in version control services.

Security patches
--------------------------------------------------------------

CSC is responsible for monitoring available security patches and
installing them on the cloud management servers.\
\
 FORGE Affiliates are responsible for keeping their virtual machines
updated.

Storage
--------------------------------------------

There is no automatic encryption or back-up. In Volume storage and image
repository RAID protects from data loss in case of hard disk breaks and
the object storage Swift is based on replications. Liability issues are
regulated in the contract.

Security monitoring
--------------------------------------------------------------------

CSC can monitor the network traffic and scan for open ports on the
virtual machines, but it is not obliged to do that. If there is a
suspected security threat such as a virtual machine participating in a
botnet, the administrators can shut it down without advance notice.

Redundancy
--------------------------------------------------

All cloud services are designed to be redundant, and the system is
designed to avoid single points of failure. The exception to this is the
hypervisors where customer virtual machines run. A failure of a
hypervisor host causes customer virtual machines on that host to fail.
Manual recovery of the failed virtual machines might be possible, but it
is not guaranteed.

------------------------------------------------------------------------

Security groups
===================================================================

Naming convension
-------------------------------------------------------------

It is part of good practice to use common naming conventions for
security groups.\
 At forge we use following naming convention for Security Groups

     <TENANT>_<Where>_to_<Service>

For example:

Digile -tenant has rule from Digile premisis to PostgreSQL

  Name                             IP Protocol   To Port   IP Range
  -------------------------------- ------------- --------- -------------------
  DIGILE\_Digile\_to\_PostgreSQL   tcp           5432      83.150.108.249/32

------------------------------------------------------------------------

Security
==============================================

Please read carefully the [security
guidelines](#security-guidelines)
for your own safety!

We have also an [security
overview](#security-overview)
of the cloud platform.

------------------------------------------------------------------------

Registered DNS names
=======================================================================

There are pre-registered names for IPv4 addresses that we have for
Forge. Those names are in form

    ip-<ipv4_with_dashes_instead_of_dots>.hosts.forgeservicelab.fi

For example *ip-193-166-24-143.hosts.forgeservicelab.fi*.

These IPv4 addresses are assigned to instances in Openstack as "floating
IPs". Once you assign a floating IP, a NAT rule within the Openstack
routing infrastructure is created, and the address is translated to your
instance. The floating IP is not assigned to a network interface in an
instance. Rather, an instance can find out its floating IP from the
metadata service, just like in Amazon EC2. When instance knows the
floating/public IP, it's trivial to determine the hostname. Following
script illustrates the process of getting public IP and setting the
proper hostname

    PUBLIC_IP_URL=169.254.169.254/2009-04-04/meta-data/public-ipv4
    IP=$(curl $PUBLIC_IP_URL)

    DASHED_IP=$(echo $IP | tr . -)
    NAME=ip-$DASHED_IP.hosts.forgeservicelab.fi

    echo $NAME > /etc/hostname
    hostname $NAME

You can also use Ansible to set up the proper hostname.

You might use the hostnames for services that need to have proper DNS
records in place.

