OpenStack Command Line Tools
==========================

## Introduction

This training is going to introduce the process to create a live service using OpenStack’s CLI tools. These are the steps to follow:

* openrc file setup
* Control machine setup
- configure the control machine
- image upload from URL
- launch an instance
- Assign a floating IP address to an instance
- Volume creation and attaching
- Allow service access to instance
- Resource verification
- Resource cleanup

OpenStack consists of several components:

- Dashboard ("Horizon") provides a web front end to the other OpenStack services 
- Compute ("Nova") stores and retrieves virtual disks ("images") and associated metadata in Image ("Glance")
- Network ("Neutron") provides virtual networking for Compute.
- Block Storage ("Cinder") provides storage volumes for Compute.
- Image ("Glance") can store the actual virtual disk files in the Object Store("Swift")
- All the services authenticate with Identity ("Keystone")

All of these components except Horizon have a CLI tool available for use. We will cover only a subset during this training session.

### OpenStack - CLI tools
It is handy to control resources in OpenStack from command line, also CLI tools are useful for simple automation.
Tools are written in Python, one tool per component, one tool per distribution package (e.g “nova” in python-novaclient, “glance” in python-glanceclient); the tools are interacting with the cloud controller via the OpenStack REST API. Similarly to Horizon, they abstract the REST cloud API from the user.

## Preparations

### Openrc file introduction
The CLI tools need you to authenticate to the OpenStack API.
Your credentials are passed in environment variables.
You can download a shell script (`openrc.sh`) from Horizon that will export your credentials to the environment. After you source the script, you can use the tools to control your resources.
You can download the openrc.sh at https://cloud.forgeservicelab.fi/dashboard/project/access_and_security/api_access/openrc/
If you have access to more than one tenant, you can reuse the script, just change the values of the OS_TENANT_NAME and OS_TENANT_ID variables

### Control machine
For training purposes, it’s good to have a specific environment where to install and try out the CLI tools.
We assume you have access to Ubuntu 14.04 instance which you can use as a control machine; you can use an instance in OpenStack, just launch one from the Ubuntu 14.04 image, as described in the OpenStack basics module.

## Exercises

### Configure the control machine

Connect to the control machine and install first the packages the virtual environment needs and then set up a python virtual environment:

```
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
```

```
virtualenv cli-tools
source cli-tools/bin/activate
```

Install nova and glance client tools for the icehouse OpenStack release. **Note! Using these exact versions is recommended, as they have been tested & verified to work:**

```
pip install python-novaclient==2.20.0 python-neutronclient==2.3.6 python-glanceclient==0.13.1 python-cinderclient==1.0.9 python-keystoneclient==0.11.2 httplib2.system-ca-certs-locater ndg-httpsclient
```

Next, get your `openrc.sh` from Horizon and upload it to the control machine.  Export the variable from the shell script to your interactive shell environment:

```
source openrc.sh
```

It will ask you for your OpenStack/FORGE password. Once you sourced the script, check if "`nova list`" and "`glance image-list`" are working.

You have configured your control machine and you can now use it instead of Horizon.

### Image upload from URL

*This exercise should take place in the controlling machine.*

OpenStack has a component - Glance - for storing virtual disk images from which you launch instances. You can upload a disk image and then create instances and volumes out of it. The easiest way to obtain images is to upload them from project websites.

You can upload freshly built tested Ubuntu trusty image from https://cloud-images.ubuntu.com/releases/trusty/release/

as 

````
$ glance image-create --name "<your initials> Ubuntu 14.04"  --disk-format qcow2 --container bare --location https://cloud-images.ubuntu.com/releases/trusty/release/ubuntu-14.04-server-cloudimg-amd64-disk1.img
````

When you create an image, you have to specify its name. The name does not need to be unique. Glance will pick an UUID for the new image. When you refer to the image in the CLI commands, you can use either the name (provided it’s unique) or the UUID. You can find out the UUIDs and name of images available within a tenant with commands:

````
$ glance image-list
$ glance image-show <name or UUID>
`````

More general information about obtaining images can be found at http://docs.openstack.org/image-guide/content/ch_obtaining_images.html

### Generate and upload an SSH key

*This exercise should take place in the controlling machine.*

To have an SSH key injected into a newly created VM so that SSH login is possible, it is necessary to upload the public part to OpenStack first. It is very recommended that these keys are password protected; to create one run:

```
ssh-keygen -t rsa -f id_rsa
```

Remember to set a password when asked by the ssh-keygen program. At the end you should have the files `id_rsa` and `id_rsa.pub` on your current directory.

To upload the public part of your key to OpenStack you can use the "nova keypair-add" command, you will want to use the `--pub-key` optional argument to specify your public key file. By using your username within the key's name (see `nova help keypair-add`) you will avoid name collisions within OpenStack.

### Launch an instance with CLI tools

*This exercise should take place in the controlling machine.*

To launch an instance, you can use the “nova boot” command. You need certain existing resource ids to parametrize the new instance. You will need id of image from which you launch the instance, flavor id to specify size of the instance, keypair to connect to it via SSH and security group(s) controlling the access. You must have private key from the keypair in your control machine.

Gather the resource ids and names as described in http://docs.openstack.org/user-guide/content/gather_parms.html
you will need commands such as:

```
$ nova flavor-list
$ nova keypair-list
$ glance image-list
$ nova secgroup-list
```

Launch an instance (preferably the smallest flavor) with the gathered parameters via the “nova boot” command as described in http://docs.openstack.org/user-guide/content/launch_from_image.html
The `nova boot` command requires a name for the VM. To easily identify the name afterwards, it is recommended to introduce some uniqueness to the name, e.g. by adding your initials to it, as in “\<your initials> test VM”.

When you launch an instance, you have to specify its name. The name does not need to be unique. Nova will pick an UUID for the new instance. Please launch the instance with the nova boot command:

```
$ nova boot ...
```

Note! If you don't specify a security group then your instance will have a default security group, which is fine now. We'll finetune security groups later in this training to allow more access than what default provides.

When you refer to the instance in the CLI commands, you can use either the name (provided it’s unique) or the UUID. You can find out the UUID and name of instances within tenant with commands:

```
$ nova show <name or UUID>
$ nova list
```

### Assign a floating IP address to an instance

*This exercise should be done in the controlling machine.*

To access the instance from the Internet, you need to assign a floating IP address to it. Each tenant/project has a pool of floating IPs allocated. List the pool and pick one free address that you will use for your new instance. See how in http://docs.openstack.org/user-guide/content/floating_ips_proc.html


You will use the following commands:

````
$ nova floating-ip-pool-list
$ nova floating-ip-list
````

If there are no available floating IPs then it is needed to allocate one.
With the floating IP allocated, all that is left is to associate it to the computing instance.
A detailed guide can be found at http://docs.openstack.org/user-guide/content/floating_ip_allocate.html

You will need such commands as:

````
$ nova floating-ip-create ....
$ nova list
$ nova floating-ip-associate ...
````

### Volume creation and attaching

*This exercise should be done in the controlling machine.*

The newly created Virtual Machine has limited storage space constrained by the flavor’s root disk size. Volumes provide extra detachable storage capacity. See how to create and attach volumes in http://docs.openstack.org/user-guide/content/cli_manage_volumes.html

You will need commands like:

```
$ cinder [help] create
$ nova [help] volume-attach
```

Newly created volumes will appear as blank block devices to the OS of the VM they are attached to.

### Allow service access to instance

*This exercise should be done in the controlling machine.*

Security groups are named collections of network access rules. By default a very limited set of network communications are allowed. For the sake of maintainability it is recommended to create new security groups to allow needed accesses instead of modifying the rules on the default security group. You can read about how to do this in http://docs.openstack.org/user-guide/content/cli_configure_instances.html#configure_security_groups_rules

Following are the steps to carry out on this exercise:

- create security group
- modify rules to allow ssh ingress
- add security group to instance

At the moment the isntance is running sshd but you are not able to access it via the public IP. You can try:

```
$ ssh <floating ip>
```

The security group(s) must  allow SSH access from the control machine (if the control machine is in FORGE OpenStack, it falls in the CIDR 193.166.24.0/23).

You will need commands like:

````
$ nova secgroup-list
$ nova secgroup-create
$ nova secgroup-list-rules
$ nova secgroup-add-rule
$ nova add-secgroup
````

### Resource verification

SSH access to the newly created virtual machine should be possible via the VM’s private IP (granted by the default security group) and the associated floating IP (granted by the security group created above). The VM’s private IP can be found by running:

````
$ nova show <name or UUID>
````

When the Ubuntu VM boots, the public part of your key pair is added to the authorized keys of the “ubuntu” user, verify that you can access the VM via both the public and private IPs

````
$ ssh ubuntu@<private ip>
$ ssh ubuntu@<public ip>
````

Once logged in to the VM, we can verify that all the requested resources are present. Flavor characteristics can be checked e.g. on `/proc` filesystem, attached block devices can be listed with `lsblk`: 

```
$ lsblk
```

You may want to further verify the attached volume by creating a filesystem and mounting it.

### Resource cleanup

This exercise should be done in the controlling machine.

Resources created up to now in this exercise:

- One Image
- One VM
- One Floating IP
- One Volume
- One Security Group

We will now release these resources in this order:

- Detach Volume
- Delete Volume
- Disassociate Floating IP
- Deallocate Floating IP
- Terminate Instance
- Remove Security Group
- Delete Image

You will need the following commands:

````
$ nova secgroup-delete
$ nova floating-ip-disassociate
$ nova floating-ip-delete
$ nova volume-detach
$ cinder delete
$ nova delete
$ glance image-delete
````

You can get more information about these commands via the help utility, in the form <tool> help <command>, e.g.:

````
$ nova help volume-detach
````
