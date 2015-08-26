
Continuous delivery
======================================================================

Continuous Delivery (CD) is a design practice used in software
development to automate and improve the process of software delivery.
Techniques such as automated testing, continuous integration and
continuous deployment allow software to be developed to a high standard
and easily packaged and deployed to test environments, resulting in the
ability to rapidly, reliably and repeatedly push out enhancements and
bug fixes to customers at low risk and with minimal manual overhead.\
 Read more about CD from
[Wikipedia](http://en.wikipedia.org/wiki/Continuous_delivery)

Deployment pipeline
====================================================================

Define your deployment pipeline
--------------------------------------------------------------------------------------------

A deployment pipeline is, in essence, an automated implementation of
your application’s build, deploy, test, and release process. Every
organization will have differences in the implementation of their
deployment pipelines, depending on their value stream for releasing
software , but the principles that govern them do not vary. The aim of
the deployment pipeline is threefold. First, it makes every part of the
process of building, deploying, testing, and releasing software visible
to everybody involved, aiding collaboration. Second, it improves
feedback so that problems are identified, and so resolved, as early in
the process as possible. Finally, it enables teams to deploy and release
any version of their software to any environment at will through a fully
automated process.

An example of a deployment pipeline is given below.

![Deployment
pipeline](/files/deploymentpipeline.png "Deployment pipeline")
 Deployment pipeline example

Select your tools
----------------------------------------------------------------

### Configuration management

Ansible is an open-source software platform for configuring and managing
computers. It combines multi-node software deployment, ad hoc task
execution, and configuration management. It manages nodes over SSH and
does not require any additional remote software (except Python 2.4 or
later) to be installed on them.

Read more about Ansible from [Ansible](#ansible)

### CI server

Jenkins provides continuous integration services for software
development. It is a server-based system running in a servlet container
such as Apache Tomcat. It supports SCM tools including AccuRev, CVS,
Subversion, Git, Mercurial, Perforce, Clearcase and RTC, and can execute
Apache Ant and Apache Maven based projects as well as arbitrary shell
scripts and Windows batch commands.

 Read more about Jenkins from
[Continuous integration server with Jenkins](#continuous-integration-server-with-jenkins)

### test automation

Robot Framework is a generic test automation framework for acceptance
testing and acceptance test-driven development (ATDD).

 Read more about Robot Framework from
[Test automation](#test-automation)

Setup your deployment pipeline
------------------------------------------------------------------------------------------

Once you have setup a continuous integration (CI) server as described in
[Continuous integration server with Jenkins](#continuous-integration-server-with-jenkins)
you could start utilizing the Jenkins features to setup your deployment
pipeline. Depending on your needs, you might want to install various
plugins for Jenkins. E.g. Git plugin to pull code from GitLab, Robot
Framework plugin to support test automation with Robot tool.

Consider the separating the Jenkins jobs based on the concern and
according to how you have defined your deployment pipeline. You might
want to setup Jenkins jobs like in the example below.

1.  Build job (triggered automatically by the GitLab web hook)
    -   Clone the code from GitLab release/master branch
    -   Run unit tests
    -   Check coding style
    -   Initiate the subsequent "Deploy to testing job"
    -   In case subsequent jobs are ok, then tag the build in GitLab
    -   Note! you might want to have a web hook from GitLab to notify
        this job in case of a commit and push in GitLab. That way each
        push would automatically trigger a build job.

2.  Deploy to testing job (triggered automatically)
    -   Clone Ansible playbook from GitLab release/master branch
    -   Run Ansible playbook to make a deployment to testing environment
    -   Prepare to revert testing environment back to previous known
        good in case of a failure
    -   Initiate the subsequent "Test job"

3.  Test job (triggered automatically)
    -   Clone your test asset from Gitlab release/master
    -   Run automated tests e.g. Robot framework tests
    -   Tag good builds in GitLab
    -   Note! Run manual tests against testing environment and promote
        the build manually if it's good

4.  Deploy to production job (manual step)
    -   Clone Ansible playbook from GitLab release/master branch
    -   Run this job manually to deploy desired (and promoted) build to
        production env
    -   Prepare to revert production environment back to previous known
        good in case of a failure

Provisioning concepts
===============================================================================

Provisioning is a set of actions to prepare a node with appropriate
configuration so that is ready for operation. In case of physical
hardware, it includes hardware allocation, hardware installation,
operating system installation and additional software installation and
configuration. Optionally, a provisioned node may also need to be
registered in an inventory. The provisioning process contains many
repetitive tasks. It should be, at least to some extent, automated. More
information on the concept at \[1\].

In FORGE, we don't deal with hardware machines but rather with virtual
machines. We use OpenStack as an infrastructure layer for creation and
power state management of virtual nodes. Due to that, the hardware
allocation and the hardware installation disappears from the process.
The complexity and effort of the two actions are transformed into
OpenStack installation and operations.

OpenStack allows to store operating system images. Those are virtual
disk images with an operating system pre-installed, which are set to
fetch and evaluate configuration from cloud environment on the first
run. When a virtual machine instance is created in OpenStack, it runs
from such pre-installed disk image (rather than installing the operating
system from PXE or ISO image), and it performs basic configuration on
the first run. Most Linux distribution provide "cloud" images which can
be used in OpenStack in such manner. With some more effort, we can
create operating system images on our own. The installation of operating
system is thus independent on the provisioning process.

As OpenStack needs to keep track of the virtual machines, we can get
essential inventory information about a node from it - IP addresses,
power state, to which organization it belongs, and several more. The
meta-data of an instance are extend-able. The inventory can be queried
with command line utilities (nova list/show/...), Python library
(python-novaclient) or Ruby library (Fog). In addition, OpenStack
includes a "web dashboard" (Horizon) where the inventory is displayed.
Provisioning systems usually have concept of roles and/or hostgroups for
nodes, in order to logically fragment inventory to groups of nodes with
similar configuration. This can be achieved independently on OpenStack,
or with the additional meta-data.

Goals of provisioning in FORGE
-------------------------------------------------------------------------------------------------

I compiled following set of criteria for provisioning tool in FORGE.

1.  allow to provision high variety of server configurations
    -   There should be modules available for popular tools
        and services. There should be good community support.

2.  make the provisioning independent on cloud environment
    -   At least in theory, there should be no prerequisites on the
        IaaS layer.

3.  make it simple for service designers to understand and use, and for
    administrators to maintain
    -   Provisioning and orchestration are aspects that support service
        deployment and maintenance. It should not be overly complicated
        to accommodate a provisioning tool.

4.  keep the number of disk images low
    -   Image creation and customization is expensive and non-trivial.
        Configuration should take place during the first run, rather
        than during image creation. It is easier to maintain a small set
        of generic images, than a large set of custom-built images.

5.  allow to collaborate on recipes
    -   It should be possible to collaborate on, and re-use, the
        configuration recipes.

Why do we need (to automate) provisioning
=====================================================================================================================

In cloud environments, provisioning can be automated to large extent.
The virtual nodes can easily be allocated and let. Development of
configuration templates can be well iterated, and lot of effort can be
saved for node configuration. Further in the process, infrastructure
capacity can be increased and decreased based on demand, which leads to
more effective hardware utilization and cost saving.

How shall we provide provisioning
=======================================================================================================

I identify two kinds of support which we can provide: documentation and
platform. By documentation I mean set of written or recorded guides. By
platform I mean a software platform which will support the process of
recipes creation, and will be taking advantage of other systems in FORGE
(namely OpenStack and git).

Documentation support
-------------------------------------------------------------------------------

We create a set of guides on how to create and use configuration
templates to provision service nodes. We can provide scripts for
configuration client installation and emphasize using modules. If there
is no server component, it's difficult to manage state. We explain that
unless there is the server component, the orchestration functionality is
dropped.

Platform support
---------------------------------------------------------------------

We can also provide FORGE users with the server component of the
provision system. The three systems (sans Ansible) offer an enterprise
version and open-source version (or "community edition"). We would be
most likely installing the open-source version. We would install one
instance of server component per organization. With the server
component, we also get orchestration functionality, e.g. remote
execution. In case of Ansible, we can provide configuration files and
inventory plugin. We should also provide documentation or script for
bootstrapping the client part of the configuration management software
in a virtual machine.

Implementations
===================================================================

There are provisioning systems which are quite specific to a platform:
OpenStack Heat, Amazon CloudFormation, or Canonical Juju. They are
promising project but using them imply vendor lock-in. I don't consider
them in this document in order to keep provisioning independent on the
IaaS layer.

The four software systems that are most relevant at the moment
(01/2014). Tools were picked based on personal experience and online
resources like:

-   \[2\] where author attempts to compare trends in community sites
    (GitHub, Ohloh,...). He observes the dominance of the two behemoths
    (Puppet and Chef), the rapid development of Salt, and broad adoption
    of Ansible.
-   \[3\] practical comparison. Author sets up a simple web server with
    all the four tools. The book emphasizes the learning curve is low
    for Ansible, medium for Salt, and high for Puppet and Chef.

Puppet
-------------------------------------------------

-   written in Ruby, has its own DSL and uses ruby templates (erb)
-   the oldest of the four, lot of functionality, used for large
    infrastructures
-   complex, difficult to debug
-   server-client architecture: puppet-master and puppet-agent;
    client-only setup somehow supported with "puppet apply"
-   large community support and high number of modules, dedicated
    "Puppet Forge"
-   Configuration resources are not evaluated line-by-line but by
    explicitly specified dependencies.
-   Documentation is of questionable quality.
-   No remote execution functionality out-of-the-box, mcollective must
    be installed for that.
-   In order to configure a node, a puppet client must be installed.
    Ready packages for most distros available, but the installation is
    not straightforward.

Chef
---------------------------------------------

-   written in Ruby, has its own DSL and again, uses Ruby templates
-   complex, difficult to learn
-   a lot of components to it: chef-server, chef-client, knife,
    berkshelf
-   There is a "Hosted Chef" option, where the server component is
    delegated to Opscode Internet service.
-   The open source chef-server setup is quite complex.
-   a lot of community modules, and also official "Opscode cookbooks"
-   Configuration directives are evaluated procedurally.
-   Remote execution functionality comes almost out-of-the-box (knife
    must be installed and set up).
-   In order to configure a node, a chef-client must be installed.
    Possible to do with wget and pipe to sh.

Salt
---------------------------------------------

-   written in Python, YAML to define recipes, Jinja2 for templates,
    Python for modules
-   More complex than Ansible, less complex than Puppet and Chef
-   The concepts of pillars and grains are difficult to grasp.
-   wide variety of modules available out of the box, i.e. apache and
    nginx
-   Community support is not so large yet.
-   pre-configuration needed, salt master needs to identify valid
    minions and minions need to be configured with the master location
-   very active community, very communicative developers
-   ready made formulas for most common simple setups, not many for
    complex installations with multiple components
-   In order to configure a node, a salt minion must be installed.
    Possible to do with wget and pipe to sh.

Ansible
---------------------------------------------------

-   written in Python, Uses YAML for configuration templates, Jinja2 for
    templates, modules can be in anything which can process and print
    YAML
-   It was designed with regards to "best features of Puppet and Chef
    and simplicity" \[6\]
-   very simple, very easy to learn, easily extend-able
-   Community support is larger than for Salt but lesser than for Chef
    and Puppet.
-   Abstraction is not as thick as in Puppet of Chef (e.g. there is no
    "package" resource but rather "apt" or "yum").
-   There is no server component.
-   In order to configure a node, one doesn't have to install
    anything Ansible. Python 2.4+ and sshd must be present. The node
    must have root account over sshd accessible from the workstation.

Criteria comparison table
=======================================================================================

I summarized my opinions on the four tools into a table. The criteria
vaguely follow the "Goals of provisioning in FORGE" section of this
document. I did not include IaaS interoperability as all of the
evaluated tools are independent on cloud provider.

I assign marks per criteria as 5 for the best (ones) in the set, and 1
for the worst (ones) in the set, and 2,3,4 relatively to the best and
worst.

| *criterion*      | Ansible | Salt | Chef | Puppet |
|:-------------|:-------------:| -----:|----:|--------:|
| variety of recipes and size of community support | 3 | 1 | 5 | 5 |
| easiness to understand enough to benefit from it | 5 | 3.5 | 1 | 1 |
| easiness to bootstrap a client | 5 | 4 | 3 | 1 |
| ease of collaboration | 3  | 3 | 3 | 3 |

All the tools have modules with parameters and plugins available out of
the box, hence the same mark for the ease of collaboration. Ansible and
Salt have module installation very straighforward. Puppet and Chef less
so, but there are tools that simplify it: for Puppet librarian-puppet,
for Chef berkshelf.

Conclusion
=========================================================

Puppet and Chef are complex. If a system is being built for the sake of
configuration management and orchestration, for example to manage large
infrastructure with several groups of hosts and tens of hosts per group,
it might be beneficial to look into Puppet and Chef.

Ansible and Salt are easy to learn. If configuration management software
should be used to automate deployment of simple systems, it will pay off
to use Salt of Ansible as users will be able to learn it, and extend it,
faster.

Chef and Puppet and pull-based - clients send its values (facts) to
master and wait for configuration instructions from it. Salt is push
based - the master pushes configuration to the salt clients. Ansible is
push-based too, the Ansible tool pushes configuration to the configured
nodes where it executes it. Ansible does not need anything special
installed in the configured nodes. More on pull vs push based
architecture in \[4\].

Do Puppet and Chef scale better than Ansible and Salt? Difficult to say.
The configuration management software systems are complex, and
scalability is difficult to measure. If an organization is using Chef
for their 200 nodes infrastructure (and has relevant knowledge of Chef
in house), it's very unlikely they will try Salt just to measure
eventual speedup or more convenience. There is not enough statistics to
say which software scales best. Ansible, as the only one, uses
exclusively SSH for transport. The other tools have the possibility to
utilize message queues, which probably means speedup of change
propagation for infrastructure with hundreds of hosts (it also means
setup of a message queue). Ansible has though the accelerated mode
\[5\], and it allows to spawn more processes for the ssh client.

Of the four tools, I would recommend Ansible. It is simple and powerful
enough. It is the path of less resistance. Service developers can see
how far it gets them, and if it is not enough, they can move to other,
more complex, tool.

Links
===============================================

- \[1\] [Server Provisioning on
Wikipedia](http://en.wikipedia.org/wiki/Provisioning#Server_provisioning)
- \[2\] [Community metrics for Puppet, Chef, Ansible and Salt (Dec
2013)](http://redmonk.com/sogrady/2013/12/06/configuration-management-2013/)
- \[3\] [Book: Taste Test, Puppet vs Chef vs Salt vs Ansible (Sep
2013)](http://devopsu.com/books/taste-test-puppet-chef-salt-stack-ansible.html)
- \[4\] [Why we chose Ansible over
Puppet](http://www.bubblewrapp.com/why-we-chose-ansible-over-puppet/)
- \[5\] [Ansible Docs: Accelerated
Mode](http://docs.ansible.com/playbooks_acceleration.html)
- \[6\] [Ansible - Red
Badger](http://red-badger.com/blog/2013/06/29/ansible/)

Ansible
============================

Ansible is a confguration management tool. It can be used to configure
remote hosts automatically. We use it especially for virtual machines in
our OpenStack environment.

Ansible is run on a "control machine" and it uses ssh for configuring
remote hosts. It is using "inventory" files for listing of available
(potentially "managed") hosts. Inventory can be a static text file, or a
script that gets a list of hosts dynamically.

Ansible modules
============================================

Official resource is <http://docs.ansible.com/modules.html>

Modules are scripts which Ansible executes on remote hosts after it
connects to them. They are mostly python scripts. Theoretically, a
module can be any program which can process command line arguments, and
print to stdout. There are useful helpers available as Python modules,
which is another motivation to write a module in Python.

A module is executed, does its job (e.g. [sets
hostname](https://github.com/ansible/ansible/blob/devel/library/system/hostname)),
and then eventually prints some JSON output about how it went.

Avialable modules can be seen in the Ansible github repo:
<https://github.com/ansible/ansible/tree/devel/library>

Official resource on module development is
<http://docs.ansible.com/developing_modules.html#module-provided-facts>

Ansible playbooks
================================================

Official resource is <http://docs.ansible.com/playbooks_intro.html>

Playbook examples can be found at
<https://github.com/ansible/ansible-examples>

Example playbook which will set the hostname on all your hosts with
floating IPs to the according record in hosts.forgeservicelab.fi domain:

    ---
    - name: set_forge_hostname
      hosts: all
      tasks:
        - ec2_facts:
        - hostname: name={{ "ip-" + ansible_ec2_public_ipv4.replace('.','-') + 
                            ".hosts.forgeservicelab.fi" }}
          when: ansible_ec2_public_ipv4 is defined

Control machine setup
========================================================

You will need to install Ansible on your control machine. I presume it's
some modern GNU/Linux distribution. There are many ways to install
Ansible. For best compatibility and support across Forge, install from
pip.

Official resource is
<http://docs.ansible.com/intro_installation.html#control-machine-requirements>

Setup of managed hosts
==========================================================

Ansible does not need much on the to-be-managed hosts. One necessity is
Python &gt; 2.4., and second is public-key ssh access to a user account
on the host. The user should have sudo privileges for any operations
that requires superuser credentials. So you should ensure that the image
will boot up with sshd running, which usually works out-of-the box on
cloud images provided by Linux Distributions.

Managing Ubuntu hosts
--------------------------------------------------------

The root access might not work out-of the box on Ubuntu cloud images,
where they enforce using "cloud-user" or "ubuntu" user, and recommend to
do administrative tasks with sudo. Pros and cons of this approach are
beyond the scope of this article.

Ubuntu cloud images are using cloud-init for bootstrap and
configuration. One of the ways to use cloud-init is to pass a
shellscript as the user-data variable of the EC2 meta-data service. The
instance then gets he value of the variable over HTTP over a "magic IP"
169.254.169.254 during its startup, and runs the script. It is possible
to enable the root login (originally disabled by cloud-init) by passing
simple script as user-data:

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

    sed -i 's/.*\(ssh-rsa.*\)/\1/' /root/.ssh/authorized_keys

Inventory setup for the FORGE OpenStack
============================================================================================

It is possible to configure Ansible so that it takes the lists of hosts
from OpenStack client. Before you attempt to orchestrate your virtual
machines with Ansible, you should set up client OpenStack environment as
described at [Getting started with
OpenStack](3_OpenStackIaaSplatform.md#getting-started-with-openstack).

If you want to have your host inventory dynamic, set to all the virtual
machines in your tenant, you can download

    git clone https://git.forgeservicelab.fi/ansible/inventory.git

then create custom config file in your home. If you installed Ansible
from git, you will find it in ansible/examples/ansible.cfg rather than
in /etc/ansible/ansible.cfg

    cp /etc/ansible/ansible.cfg ~/.ansible.cfg

And edit \~/.ansible.cfg file so that there is

    [defaults]
    hostfile = ~/inventory/sources
    private_key_file = ~/keys/your_openstack_private_key.pem

Then try

    ansible all -m ping


Ansible Guidelines
=============================================================

Ansible playbooks and roles must be kept on source control in GitLab
<https://git.forgeservicelab.fi>. Playbooks should be stored
under the Ansible group <https://git.forgeservicelab.fi/groups/ansible>
while roles will have their place under the Ansible-Roles
group <https://git.forgeservicelab.fi/groups/ansible-roles>.

Arrangement according to function
-------------------------------------------------------------------------------------------

Ansible roles are meant to be pluggable and reusable, therefore no
configuration specifics should appear on a role. Roles should concern
provisioning and only provisioning, and assume all options installed on
a role will be defaults, unless a certain customization is widespread
enough to be reused and considered a de-facto default.

Ansible playbooks are deployment specific. They combine roles together
to tailor a particular purpose and they concern configuration. All plays
regarding customization of a deployment and tweaking of options should
appear on the playbook and not on the roles; as a rule of thumb if a
play alters configuration files, it should appear on a playbook.

Role management
-------------------------------------------------------

Ansible roles must be present before running the playbook that uses
them. Previously git submodules were used to manage roles. Starting from
ansible 1.8 the use of a so called Ansible Galaxy Requirements File is
recommended for all playbooks. The following shows an example structure
of the requirements file:

    $ cat requirements.yml
    # install from the galaxy service (operated by ansible)
    - src: mstrisoline.ruby-builder
      path: roles/

    # install from github
    - src: https://github.com/geerlingguy/ansible-role-repo-epel
      path: roles/

    # install from FORGE's gitlab via HTTPS
    - src: git+https://git.forgeservicelab.fi/ansible-roles/forge_hostname.git
      path: roles/

    # install from FORGE's gitlab via SSH (needs developer public key in gitlab under FORGE/ssh_keys in order to work)
    - src: git+ssh://gitlab@git.forgeservicelab.fi:10022/ansible-roles/forge_ssl.git
      path: roles/

When installing roles, the requirements file is referenced as follows:

    $ ansible-galaxy install -r requirements.yml --roles-path=./roles

Further the above command specifies explicitly installing the roles into
the roles subdirectory within the playbook directory, in contrast to for
example /etc/ansible/roles.

Once all dependent roles have been successfully installed, the playbook
is ready to run.

Role documentation
-------------------------------------------------------------

Roles should be documented following Ansible Galaxy's documentation
stub:

    Role Name
    ========

    A brief description of the role goes here.

    Requirements
    ------------

    Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, 
    if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

    Role Variables
    --------------

    A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml,
    vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles
    and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

    Dependencies
    ------------

    A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set
    for other roles, or variables that are used from other roles.

    Example Playbook
    -------------------------

    Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

        - hosts: servers
          roles:
             - { role: username.rolename, x: 42 }

    License
    -------


    Author Information
    ------------------

Retrieving playbooks for use
---------------------------------------------------------------------------------

This is a two step process:

-   Clone playbook from git

<!-- -->

    git clone ssh://gitlab@git.forgeservicelab.fi:10022/ansible-roles/forge_ssl.git

-   Install required roles with ansible-galaxy (see Role
    Management above)

The roles subdirectory under the cloned playbook directory will be
initially empty (with exception of self-contained playbooks such as
hadoop). Individual role directories will be created and populated by
ansible-galaxy install. This is also the reason why git repos for
playbooks contain an empty roles directory with .gitignore set for \*.

SSH Access
---------------------------------------------

It is not necessary or recommended to assign floating IPs to every
virtual machine on the project to have ssh access to them. It is
possible to connect to all virtual machines using their private IPs,
given that at least one of them does have a floating IP associated, by
using an SSH jump host. Let's say that we have the following setup with
the given example IPs:

    localhost  --->   public_vm   --->   private_vm_1
                    (193.166.24.1) |    (192.168.0.10)
                                   |
                                   -->   private_vm_2
                                        (192.168.0.20)

Then we can configure `public_vm` as a jump host on localhost's
`~/.ssh/config` file as such:

    Host JumpHost
      Hostname 193.166.24.1
      User username_for_public_vm

    Host 192.168.0.*
      ProxyCommand ssh JumpHost nc -q0 %h %p

And that would allow us to connect directly to the non-exposed virtual
machines using their private IPs:

    $ ssh username_for_private_vm_1@192.168.0.10
    $ ssh username_for_private_vm_2@192.168.0.20

Which will of course work for Ansible as well:

    $ ansible 192.168.0.10 -m setup -u username_for_private_vm_1

This also means that virtual machines can be referenced by their private
IP on ansible inventory files.

Provisioning with Apache Libcloud
========================================================================================

This guide helps to get started with how to automate provisioning with
the python library Apache Libcloud. Basic level python skills are
required to use this library.

Apache Libcloud
====================================================

Apache Libcloud is a python library developed by Cloudkick and
maintained by Apache Software Foundation for interacting with many of
the popular cloud service providers using a unified API. Latest
documentation can be found from Apache Libcloud homepage.

Requirements
==============================================

As a python library, libcloud has a few requirements.

-   Python (2.7 recommended)
-   pip
-   apache-libcloud (0.15 or newer)

1. Install Python
-------------------------------------------------------

    $ sudo apt-get install python2.7

2. Install pip
-------------------------------------------------

    $ sudo apt-get install python-pip

3. Install Libcloud
-----------------------------------------------------------

    $ sudo pip install apache-libcloud

If you have already installed python, check your python version using
following command:

    $ python -V

This should print something like this
 Python 2.7.6

Writing a script
======================================================

1. Simple examples
---------------------------------------------------------

Libcloud supports a lot different clouds and following simpliest example
shows how to list all instances from Rackspace cloud in a specific
region.

    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver

    # Cloud specific information
    USERNAME = 'username'
    API_KEY = 'apikey'
    RS_REGION = 'region'

    # Specify driver
    cls = get_driver(Provider.RACKSPACE)

    # Connect to cloud
    driver = cls(USERNAME, API_KEY, region=RS_REGION)

    # Get nodes
    nodes = driver.list_nodes()

    # Print nodes
    for node in nodes:
        print node

However Libcloud doesn't directly support Forge cloud so a generic
OpenStack driver and more parameters are needed.

Rest of the code stays the same.

    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver

    # Cloud specific information
    USERNAME = 'username'
    PASSWORD = 'password'
    AUTH_URL = 'https://cloud.myprovider.fi:8888/'
    AUTH_VERSION = '2.0_password'
    TENANT = 'my-tenant'
    SERVICE_REGION = 'my-region'
    SERVICE_NAME = 'service-name'
    SERVICE_TYPE = 'service-type'
    BASE_URL = 'https://cloud.myprovider.fi:8888/v2/my-tenant'

    # Specify driver
    cls = get_driver(Provider.OPENSTACK)

    # Connect to cloud
    driver = cls(
        USERNAME,
        PASSWORD,
        ex_force_auth_url=AUTH_URL,
        ex_force_auth_version=AUTH_VERSION,
        ex_tenant_name=TENANT,
        ex_service_region=SERVICE_REGION,
        ex_service_name=SERVICE_NAME,
        ex_service_type=SERVICE_TYPE,
        ex_force_base_url=BASE_URL
    )

    # Get nodes
    nodes = driver.list_nodes()

    # Print nodes
    for node in nodes
        print node

### Explaining the code

Following part makes the request (list all nodes) to the server and the
server response is stored in a list.

    nodes = driver.list_nodes()

2. Getting different information
-------------------------------------------------------------------------------------

Get all images available use following command

    images = driver.list_images()

Result

&lt;NodeImage: id=70c1723b-ef3f-4056-adee-aea3e5b3b4a2,
name=Ubuntu-14.04-server-amd64, driver=OpenStack ...&gt;&lt;NodeImage:
id=9ee35702-87d5-4216-a9fe-9e02bdad73a9, name=Debian-7.6-server-amd64,
driver=OpenStack ...&gt;&lt;NodeImage:
id=47ebe70b-7876-4391-a648-07abbacb4da4,
name=Debian-7.6-server-amd64\_DEPRECATED, driver=OpenStack
...&gt;&lt;NodeImage: id=8fdcd873-168f-4d1f-9236-7ba3d8f88cbd,
name=Debian-7.5-server-amd64\_DEPRECATED, driver=OpenStack
...&gt;&lt;NodeImage: id=e9734856-5e92-4ac8-aa6b-b3164e845f7e,
name=CentOS-6.5-server-x86\_64, driver=OpenStack ...&gt;&lt;NodeImage:
id=dc615573-7134-4b56-a152-262b92904067, name=Ubuntu-12.04-server-amd64,
driver=OpenStack ...&gt;&lt;NodeImage:
id=6ff87365-ef2d-4b31-8e06-46d443e94d34,
name=Debian-7.5-server-amd64\_DEPRECATED, driver=OpenStack
...&gt;&lt;NodeImage: id=d732a152-04f7-4cc0-938b-879705c1d963,
name=Debian-7.4-server-amd64-DEPRECATED, driver=OpenStack
...&gt;&lt;NodeImage: id=8da13f00-1375-4e97-88f9-35be9877617e,
name=Debian-7.3-server-amd64-DEPRECATED, driver=OpenStack ...&gt;

Get all machine sizes available use following command

    sizes = driver.list_sizes()

Result

&lt;OpenStackNodeSize: id=1, name=m1.tiny, ram=1024, disk=10,
bandwidth=None, price=0.0, driver=OpenStack, vcpus=1,
...&gt;&lt;OpenStackNodeSize: id=2, name=m1.small, ram=2048, disk=10,
bandwidth=None, price=0.0, driver=OpenStack, vcpus=1,
...&gt;&lt;OpenStackNodeSize: id=3, name=m1.medium, ram=4096, disk=20,
bandwidth=None, price=0.0, driver=OpenStack, vcpus=2,
...&gt;&lt;OpenStackNodeSize: id=4, name=m1.large, ram=8192, disk=40,
bandwidth=None, price=0.0, driver=OpenStack, vcpus=4,
...&gt;&lt;OpenStackNodeSize: id=5, name=m1.x-large, ram=16384, disk=80,
bandwidth=None, price=0.0, driver=OpenStack, vcpus=8, ...&gt;

Get all created storage volumes use following command

    volumes = driver.list_volumes()

Result

&lt;StorageVolume id=38804771-bfa0-435d-8c90-f0acc0f8a3c0 size=2
driver=OpenStack&gt;&lt;StorageVolume
id=a43f3613-345c-4c47-b16e-1bfb971b6e67 size=2
driver=OpenStack&gt;&lt;StorageVolume
id=50328e80-b464-47a7-8223-94160b3436aa size=2
driver=OpenStack&gt;&lt;StorageVolume
id=9432d2d7-1c9d-4096-a0bc-1167dcc26ea9 size=2 driver=OpenStack&gt;

Debugging
========================================

Libcloud provides a special debug mode that logs all outgoing HTTP
requests and incoming HTTP responses. You can debug using following
command:

    $ LIBCLOUD_DEBUG=/dev/stderr python my_script.py

**Warning**

 Debug log contains connection information including your username and
password in plain text!

And it prints something like this

 \# -------- begin 4431824872 request ----------curl -i -X GET -H 'Host:
s3.amazonaws.com' -H 'X-LC-Request-ID: 4431824872' -H 'Content-Length:
0' -H 'User-Agent: libcloud/0.6.0-beta1 (Amazon S3 (standard))'
'<https://s3.amazonaws.com:443/?AWSAccessKeyId=foo&amp;Signature=bar>'\#
-------- begin 4431824872:4431825232 response ----------HTTP/1.1 200
OKX-Amz-Id-2: 1234Server: AmazonS3Transfer-Encoding:
chunkedX-Amz-Request-Id: FFFFFFFFFFDate: Tue, 01 Nov 2011 22:29:11
GMTContent-Type: application/xml171&lt;?xml version="1.0"
encoding="UTF-8"?&gt; &lt;ListAllMyBucketsResult
xmlns="<http://s3.amazonaws.com/doc/2006-03-01/>"&gt; &lt;Owner&gt;
&lt;ID&gt;sada8932dsa8d30i&lt;/ID&gt;
&lt;DisplayName&gt;kami&lt;/DisplayName&gt; &lt;/Owner&gt;
&lt;Buckets&gt; &lt;Bucket&gt; &lt;Name&gt;test34324323&lt;/Name
&lt;CreationDate&gt;2011-11-01T22:17:23.000Z&lt;/CreationDate&gt;
&lt;/Bucket&gt; &lt;/Buckets&gt;&lt;/ListAllMyBucketsResult&gt;0\#
-------- end 4431824872:4431825232 response ----------

Errors
==================================

If you get an error like

 ImportError: No module named dateutil.parser

you need to get python module **dateutil**. You can install modules with
pip:

    $ sudo pip install python-dateutil

You can install most of the missing modules with pip packages
**"python-&lt;module name&gt;"**


Docker
==================================================

Docker is a wrapper of the Linux container subsystem. It consists of the
docker daemon which talks to linux kernel with container support, and
the online image register - Docker Hub. Containers are a less-overhead
alternative to virtual machines. Container virtualization better
utilizes physical resources.

Docker can be very simply installed on Ubuntu 14.04. Ubuntu 12.04
installation will require restart. In order to maximally utilize
resources, the operating system running the containers should be as thin
as possible, thinner than the usual server images of common Linux
distributions. If Ubuntu of CentOS is considered to thick, there are
distribution designed for running Docker images only (CoreOS,
boot2docker), those don't even have a package manager.

Docker images are union filesystem images - they consist of directory
tree layers which then merge on mount. The applications running in the
containers then see the whole merge as their root. There is an online
repository of images - the Docker Hub.

Docker in FORGE
===========================================

We unfortunately don't have any physical hardware available for running
containers. However, we can run containers in a virtual machine. First,
you must create a vanilla Ubuntu 14.04 instance and assign it a floating
IP.

Then follow the readme in Ansible playbook
<https://git.forgeservicelab.fi/ansible/docker_playbook/tree/master>.

It shows a simple scenario of installing Docker and running containers
on a virtual machine in your tenant in FORGE OpenStack. The container
will run the training/webapp image from the Docker tutorial.

Links
=======================

-   Docker installation: <http://docs.docker.com/installation/>
-   Docker on Wikipedia:
    <http://en.wikipedia.org/wiki/Docker_%28software%29>
-   Docker demo in your broswer showing basics:
    <https://www.docker.com/tryit/>
-   Docker Hub, the image registry for Docker (needs registration):
    <https://hub.docker.com/>
-   CoreOS, a modern minimal operating system: <https://coreos.com/>
-   boot2docker, a lightweight Linux distribution for running Docker
    images: <https://github.com/boot2docker/boot2docker>


Continuous integration server with Jenkins
===========================================================================================================================================

This document shows how to bootstrap a continous integration server
running Jenkins.

Jenkins role
-------------------------------------------------------------------------------

We have an ansible role for jenkins in GitLab.

 <https://git.forgeservicelab.fi/ansible-roles/jenkins>

It sets up jenkins listening on plain http on localhost and nginx with
ssl as a forward proxy.

Example playbook
---------------------------------------------------------------------------------------

You can take a look at
 <https://git.forgeservicelab.fi/ansible/ci>

You will probably want to remove the forge\_ssl and forge\_users roles.
If you have your own hostname, you might want to remove the
forge\_hostname role call too, and put `- hostname: <your_hostname>` to
pre\_tasks.

Ansible setup
---------------------------------------------------------------------------------

You need to set up your Ansible inventory. Please follow [this
guide](#inventory-setup-for-the-forge-openstack). Once your
inventory is set up, try

    $ ansible <your_ip_or_hostname> -m ping 

Instance setup
-----------------------------------------------------------------------------------

Launch an Ubuntu instance to try it with.

Ansible run
-----------------------------------------------------------------------------

You are ready to roll. From the playbook directory, run:

    $ ansible-playbook -u ubuntu -s -e h=<your_vms_ip> test.ci.yml

If everything succeeds, you should see jenkins on https://

Test automation
==========================================================

Tools
--------------------------------------

At FORGE ServiceLab we use Robot Framwork on test automation. Robot
Framework is a generic test automation framework for acceptance testing.
It has an easy-to-use tabular test data syntax and utilizes a
keyword-driven testing approach. Its testing capabilities can be
extended by test libraries implemented either with Python or Java, and
users can create new keywords from existing ones using the same syntax
that is used for creating test cases. In addition to test web services
we use Selenium2Library. Selenium2Library is a Robot Framework test
library that uses the popular Selenium web testing tool internally. It
provides a powerful combination of simple test data syntax and support
for different browsers.

-   [Robot Framwork](http://robotframework.org/)
-   [Selenium2Library](https://github.com/rtomac/robotframework-selenium2library)

For instanlling Robot Framework there is a Ansbile playbook available in
git (<https://git.forgeservicelab.fi/ansible/testautomation>). For
cloning and running it use ansible (See instructions at
[Ansible Guidelines](#retrieving-playbooks-for-use))

Usage in Forge
--------------------------------------------------------

In FORGE ServiceLab test automation is integrated as part of the
[Continuous Integration.](#continuous-integration-with-jenkins) Tests
are automatically triggered if new source code is pushed to projects
master repository or new test case is pushed to project specific test
automation repository. Test results can be seen from Jenkins.

![Test
Automation](/files/test_automation_jenkins.png)

Example
------------------------------------------

At gitlab there is a public project that can be used as an example or
start point. (<https://git.forgeservicelab.fi/testautomation/example>)

Best Practices
--------------------------------------------------------

### How to write good test cases

-   [By Robot
    Framework](https://code.google.com/p/robotframework/wiki/HowToWriteGoodTestCases)

### Parameters in scrips

Parameters should be used. Setting for example environment or user
accounts should be parametrized so that CI tools can set them. In script
you just set parameters in **Variables** block

    *** Variables ***
    ${ENV}    TEST
    ${USER}    tester
    ${PASSWORD}    somepass

After that these variables can be overwritten by command line option
(and by Jenkins)

    ~$pybot --variable ENV:PROD --variable USER:someother --variable PASSWORD:somepass .

You might want to hide these parameters from reports (at least
password). For hiding these you need to put log level to none and then
again enable logging after data is entered.

    Set Log Level    NONE
    login Auth    ${USER}      ${PASSWORD}    You are currently logged in as ${USER}
    Set Log Level    DEBUG

### Specifying what cases to run

If you have tests that you don't want to run in ie production
environment you need to speciify argument file which states the cases to
be executed. In Forge we have separate set of tests for production and
testing. Both environments have its own file and file is passed to pybot
with *--argumentfile*

    ~$pybot --argumentfile testing.args

So the full command with parameters & arguments would be something like:

    ~$pybot --variable ENV:PROD --variable USER:someother --variable PASSWORD:somepass --argumentfile testing.args

and file *testing.args* looking like:

    --name Testing Environment
    testsuite1.txt
    testsuite2.txt
    blablablaa.txt

### Running on server without display

Web tests can be executed on server machines without display. For
setting this up you need to install firefox and Xvfb (Virtual
FrameBuffer)

    ~$sudo apt-get install firefox xvfb

And then you can run virtual fram bubber with

    ~$sudo Xvfb :10 -ac

And start firefox headlessly

    ~$export DISPLAY=:10
    ~$firefox

### Run on remote client

Selenium tests can be executed on client with [Selenium
Grid](https://code.google.com/p/selenium/wiki/Grid2)

Performance testing
======================================================================

Tools
------------------------------------------

At FORGE ServiceLab we use [jmeter](http://jmeter.apache.org/) for
performance testing. Jmeter is an open source software for performance
and load testing. It can be used to simulate a heavy load on a server,
group of servers, network or object to test its strength or to analyze
overall performance under different load types. You can use it to make a
graphical analysis of performance or to test your server/script/object
behaviour under heavy concurrent load.
 Jmeter has also Jenkins
[plugin](https://wiki.jenkins-ci.org/pages/viewpage.action?pageId=51019876)
so it can be easily included into the [deployment
pipeline](#continuous-integration-with-jenkins) as part of continuous
integration process.

**Installation**

You can install jmeter with apt-get (or other package managers) but it
is recommended to download the lates release from [jmeter download
site](http://jmeter.apache.org/download_jmeter.cgi)

Usage in Forge
------------------------------------------------------------

At Forge we use jmeter for performance testing as well as load testing.
Performance tests are executed continuously (every 60 minutes). This
means that single virtual user makes certain transactions in tested
service and responce times are reported and appended to graphs. This
gives an overall picture of the services performance. Jmeter is also
used for load testing. In load testing the tested service is isolated
from any other transactions and jmeter scripts are used for generating
load to service. With load testing we try to simulate current workload
on the production as well as testing the service with estimated future
workload and possible peaks.

Example
----------------------------------------------

Example jmeter script can be downloaded from
[git](https://git.forgeservicelab.fi/testautomation/performance_example).
The script makes a login to auth.forgeservicelab.fi. Script catches
session token & lt variables and uses them in next steps. Without
catching these variables the script would fail. This is a most common
use case in jmeter scripting and thus it is shown in this example.

Below is descriped the main steps for geeting this done:

### 1. Add http request for auth.forgeservicelab.fi/login

![](/files/jmeter_login_step.png)

### 2. Add "View Results Tree" ("Add-&gt;Listeners-&gt;View Results Tree") for getting the responce data. After running script open "View Result Tree" and select "Responce data" tab

![](/files/jmeter_result_tree.png)

### 3. Add "Regular Expression Extractor" ("Add-&gt;Post Processors-&gt;Regular Expression Extractor") after login requests. Specify regular expresion for getting the wanted value.

![](/files/jmeter_regexp.png)

### 4. Now you can add the values read in previous steps to be sent in login with username and password

![](/files/jmeter_login_parameters.png)

Running scripts
--------------------------------------------------------------

To run example simple clone it and run:

    $ jmeter -n -t login_to_auth.jmx -l results.jtl

jmeter parameters:

-   -n NON\_GUI mode
-   -t test to be executed
-   -l log file

or you can open it in jmeter GUI and run it there.

Tips & Tricks
------------------------------------------------------------

-   Use test script recorder for getting knowledge what all parameters
    you need to catch in next steps
-   For load testing minimize all other traffic on testing environment

Analytics
========================================

Analytics is the discovery and communication of meaningful patterns in
data. Especially valuable in areas rich with recorded information,
analytics relies on the simultaneous application of statistics, computer
programming and operations research to quantify performance. Analytics
often favors data visualization to communicate insight.

Firms may commonly apply analytics to business data, to describe,
predict, and improve business performance. Specifically, arenas within
analytics include enterprise decision management, retail analytics,
store assortment and stock-keeping unit optimization, marketing
optimization and marketing mix modeling, web analytics, sales force
sizing and optimization, price and promotion modeling, predictive
science, credit risk analysis, and fraud analytics. Since analytics can
require extensive computation, the algorithms and software used for
analytics harness the most current methods in computer science,
statistics, and mathematics. See
[wikipedia](http://en.wikipedia.org/wiki/Analytics)

Analytics solutions
------------------------------------------------------------

You have several options for collecting web statictics and data
visualization. Among most commonly used applications are [Google
Analytics](http://www.google.com/analytics/) and [Piwik](http://piwik.org/) just to
name few. Piwik is an open analytics platform currently used by
individuals, companies and governments all over the world. Google
Analytics is a service offered by Google that generates detailed
statistics about a website's traffic and traffic sources and measures
conversions and sales. It's easy to get started with Google Analytics
because using the application doesn't require any application or server
installation but account creation only. It's also easy to migrate from
Google Analytics to Piwik if one decides later to host the analytics
server and data by herself. There is a [Python
script](http://piwik.org/blog/2011/02/exporting-google-analytics-to-piwik-google2piwik/)
that does the migration automatically.

Google Analytics
------------------------------------------------------

Google Analytics doesn't require you to install and maintain an
application in your server but the full service is offered by Google.
You just have to access Google Analytics in
<https://www.google.com/analytics/> with your google credentials and
create an account. Then you can start creating properties (urls to be
tracked). Creating a property will provide you with a short block of
javascipt code you then embed to your web page. When your web page is
loaded by users' browsers, then the code contributes to the statistics
that becomes visible in Google Analytics.

Piwik
--------------------------------

Piwik is an open alternative to Google Analytics. FORGE uses Piwik to
analyse <http://forgeservicelab.fi> web usage statistics as well as
usage of other FORGE services git and Redmine. You can host Piwik server
by yourself which will provide you flexibility in getting and storing
data. It's easy to install Piwik server into FORGE Service Lab cloud
environment by using Ansible. First you launch Ubuntu instance and they
you clone forge-piwik playbook
<https://git.forgeservicelab.fi/forge/forge-piwik>. You might want to
disable a role forge-ssl from the site.yml since that is the role which
installs FORGE server certificates for Apache web server and you
probably want to install your own server certificates. Other than that
the playbook is generic enough to install and configure Piwik for https
connections. You should follow the playbook usage instructions
documented in git.

    $ cd ~
    $ mkdir piwik; cd piwik
    $ git clone ssh://gitlab@git.forgeservicelab.fi:10022/forge/forge-piwik.git

Then edit inventory file to contain your server's ip address
aa.aa.aa.aa.

    # inventory

    [piwik]
    aa.aa.aa.aa

Comment out or remove forge-ssl from site.yml since it installs FORGE
server certificates. Instead of that you might want to install your own
server certificates and make sure that
./roles/piwik-ssl/group\_vars/all.yml has sslcert, sslkey and sslchain
variables indicate the proper location of your own certificate files
which you have stored in the target server.

    # site.yml
    ---
    - hosts: all
      sudo: True
      roles:
        - ansible-piwik
    #    - forge_ssl
        - piwik-ssl

Run the playbook with extra variable set to enable web browser access
from desired IP range bb.bb.bb.bb.

    $ ansible-playbook -i inventory site.yml --extra-vars "ip_range=bb.bb.bb.bb"

After running the playbook you should have all the necessary components
installed and running and you can finalize the configuration by opening
your web browser to your server ip address aa.aa.aa.aa.

Load testing
=================================================

Tools
-----------------------------------

At Forge Servicelab we use [JMeter](http://jmeter.apache.org/) (with
PerfMon plugin) for load testing.

**Installation**

You can download PerfMon jmeter plugin from
[Jmeter-plugins](http://jmeter-plugins.org/downloads/all/) -site. You
need to install JMeterPlugins-Standard and ServerAgent packages.
ServerAgent is java tool installed under Application Server Under Test
and JMeterPlugins-Standard is a JMeter plugin gathering information from
the ServerAgent

Usage in Forge
-----------------------------------------------------

At Forge we use jmeter for load testing as well as performance testing.
Load tests are executed regularly against testing environment to make
sure software under test meats our performance targets under load.
 In load testing the tested service is isolated from any other
transactions and jmeter scripts are used for generating load to service.
With load testing we try to simulate current workload on the production
as well as testing the service with estimated future workload and
possible peaks.

In Forge we use the following set up.
 ![](/files/jmeter.png)

Here is a short configuration for the set up. You need to have the same
jmeter versions installed on all servers and client. If you need more
details for setup you might find the [documentation by
Google](https://cloud.google.com/developers/articles/how-to-configure-ssh-port-forwarding-set-up-load-testing-on-compute-engine/)
useful.

1. Make SSH tunnels from JMeter Client to JMeter servers

		ssh -L 24000:127.0.0.1:24000 -R 25000:127.0.0.1:25000 -L
		26000:127.0.0.1:26000 user@jmeterserver0 -f -N
		 ssh -L 24001:127.0.0.1:24001 -R 25000:127.0.0.1:25000 -L
		26001:127.0.0.1:26001 user@jmeterserver1 -f -N
		 ssh -L 24002:127.0.0.1:24002 -R 25000:127.0.0.1:25000 -L
		26002:127.0.0.1:26002 user@jmeterserver2 -f -N

2. Configure JMeter Client by adding these lines to jmeter.properties
(/usr/share/jmeter/bin/jmeter.properties)

		remote\_hosts=127.0.0.1:24000,127.0.0.1:24001,127.0.0.1:24002
		 client.rmi.localport=25000
		 mode=Statistical

3. Configure JMeter Servers by adding these lines to jmeter.properties
with the correct port (24000, 24001, 24002 etc.)

		server\_port=24000
		 server.rmi.localhostname=127.0.0.1
		 server.rmi.localport=26000

4. Start the JMeter servers (Run this on every server node)

		/usr/share/jmeter/bin/jmeter-server -Djava.rmi.server.hostname=127.0.0.1

5. Start the JMeter Client (Run this on client)

		/usr/share/jmeter/bin/jmeter -Djava.rmi.server.hostname=127.0.0.1

6. Start the tests with "Run-&gt;Remote Start All"

Planning
-----------------------------------------

Load tests need to be planned thoroughly to get the most out of it.
While planning one should measure the current load in SUT (System Under
Test) as well as the future load. Load tests should also include peak
usage tests as well as stress tests. With stress tests we are able to
point out the bottle necks of the systems and find the future
development or investment needs.

**Example plans**

	 Test Plan Name                     No of VUsers    Ramp up   Duration   Time between transactions   Script actions      Note
	 --------------------------------- --------------- ---------- ---------- --------------------------- ------------------- ---------------------------------------------------------------------------------
	 Basic usage for service current   15              30 s       15 min     10 s                        Login & browsing    Current average load is 10 simultaneous users
	 Basic usage for service future    50              30 s       25 min     10 s                        Login & browsing    Estimate is that after two years the average load will be 50 simultaneous users
	 Peak usage current                20              30 s       15 min     1 s                         Login               Current peak in usage is on everyday morning when users login to system
	 Peak usage current                70              30 s       25 min     1 s                         Login               Estimate peak in usage
	 Stress it                         ??              60 s       60 min     0 s                         Login & browsing    Find out the most used services and increase VUser count to the brake limit
	 Reliability                       15              60 s        72 j      60 s                         Login & browsing   Find out possible memory leaks, log file appends etc

Example
---------------------------------------

You can use our [performance example
script](https://git.forgeservicelab.fi/testautomation/performance_example)
as an example. Just change the Thread Group variables to match your
scenario.


Production environment considerations
============================================================================================================================

Here are some issues you might want to consider when you're planning
deployment to production environment. You should deal with some of the
issues already before you start development. Main target should be to
operate and support system effectively once it's in production. You
might want to consider deployment automation tools and test automation
tools to make deployment smooth and continuous.

-   Images with bundled software are the easiest way to start
    development, but for production, use plain OS images and install
    required software packages with deployment playbooks. Keep the OS
    configuration in separate playbooks from the software deployment.

-   Avoid fixing Ansible playbooks for one Linux distribution only, you
    may want to change that later. There is variation in what Linux
    distributions are supported in commercial cloud environments and
    your choice of commercial cloud environment might not have e.g.
    Debian in the list of supported OSs.

-   Use version control for you deployment scripts. Have a git branching
    policy and e.g. have a deployment branch and make that the only
    source for the code that goes to production and ensure that you are
    aware of what is in the production servers at any time.

-   Keep development and production environment inventories separate, do
    not try to mix them.

-   Size server instances correctly according to targeted server
    purposes when deploying to production. You probably use tiny or
    micro instances during development, they might not be the best
    solution for production needs.

-   Increase storage capacity when needed, do not
    over-allocate initially.

-   Use monitoring (e.g. Nagios) to detect utilization, detect if
    something is overused or underused. Alerts can be useful to detect
    and solve small issues before they become big problems. Monitoring
    helps you also to detect if your service utilization is sky
    rocketing and you have to consider resizing.

-   Get rid of waste. Eliminate unneccessary development and test
    servers when they are no longer needed. Remove storage volumes that
    are not attached or used.

-   Update used software frequently to patch bugs and update their
    security features.

-   Check the pricing alternatives, such as discounts, Amazon AWS
    reserved instances, different support levels, etc. Longer contracts
    can make a big difference in costs.

-   Deployment to most of the production cloud environments can be made
    with Ansible since it requires ssh access only. Anyhow, check first
    that Ansible is supported by the OS of your choice and e.g.
    Microsoft Windows might be not fully supported

-   Some production environments don't offer firewall as a service and
    in that case the firewall should be configured into virtual
    machine hosts.


Production environment
=============================================================================

Provisioning phase produces the cloud service environment for
deployment. To provision is to activate virtual servers, storage
volumes, networks, access rights, and other items so that the cloud
service is available for use. Provisioning means slightly different
things in different cloud platforms as each commercial cloud platform
has different features and management tools.

These guides describe the steps that needs to be taken to provision
production cloud environment. The guidelines use Plaza Drupal-HA cluster
service environment as an example production environment. Provisioned
environment consists multiple virtual servers with scalable Drupal
webserver. See [Drupal-HA cluster
architecture](5_Exampleapplication.md#drupal-ha-cluster-architecture) for more information
about Plaza.

Provisioning phase is cloud specific and it requires different tasks
depending on target cloud platform.

-   [Provisioning to FORGE IaaS](#provisioning-to-forge-iaas)

Commercial IaaS platforms:

-   [Provisioning to Amazon AWS](#provisioning-to-amazon-aws)
-   [Provisioning to Cybercom
    Cloud](#provisioning-to-cybercom-cloud)
-   [Provisioning to Microsoft
    Azure](#provisioning-to-microsoft-azure)
-   [Provisioning to Rackspace](#provisioning-to-rackspace)


Provisioning to FORGE IaaS
===========================================================================================

The following table shows the actions to deploy Plaza (Drupal-HA
cluster) digital service to FORGE IaaS.
 Most actions depend on previous ones, so you should perform the actions
in specified order.

At this phase you will setup virtual machines with a set amount of
resources, attach various types of storage to the machines and connect
them using virtual networks.
 You will also configure SSH access to newly created virtual machine
instances.

The columns in the table define the tool/area what the action relates to
and where the action should be performed (\*

|Control machine (localhost) |  OpenStack (FORGE IaaS)  | Server Instances |
|----------------------------|--------------------------|------------------|
| [1. Install tools](#forge-iaas-install-tools) | [2. Specify keypairs](#forge-iaas-specify-keypairs) |  
|                                      | [3. Create virtual machine instances](#forge-iaas-create-virtual-machine-instances) |
|                                      | [4. Specify floating IPs](#forge-iaas-specify-floating-ips) |
|                                      | [5. Configure security groups](#forge-iaas-configure-security-groups) |
|                                      | [6. Create and attach volumes](#forge-iaas-create-and-attach-volumes) |
| [7. Configure SSH access](#forge-iaas-configure-ssh-access)| | [8. Update servers](#forge-iaas-update-servers) |

(\* The guidelines for OpenStack actions assume that you use web user
interface to perform OpenStack actions; you can also perform these with
command line tools.

FORGE IaaS Cloud Management Portal : <https://cloud.forgeservicelab.fi>

Documentation : <http://docs.openstack.org/>

FORGE IaaS install tools
======================================================================

In this task you will configure your localhost to be used as control
machine for OpenStack environment.
 You will install the following packages and tools needed for Plaza
deployment:

	tool   Description
	------ ---------------------------------------------------------
	git    Distributed revision control and source code management
	pip    Tool for installing and managing Python packages

When deploying on OpenStack environments, Plaza playbook runs some tasks
on the control machine against OpenStack.
 You need to have the following Python packages installed on the control
machine:

	Package                               Description
	------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------
	python-novaclient                     Client library for OpenStack Compute API
	python-keystoneclient                 Client Library for OpenStack Identity
	python-neutronclient                  CLI and Client Library for OpenStack Networking
	httplib2.system\_ca\_certs\_locater   This package provides a plug-in to httplib2 to tell it to use the certificate authority file from the base OS instead of the one in the httplib2 package.

Preconditions

-   You have a machine with GNU/Linux distribution to use as control
    machine
-   Your user account has the privileges to run programs with the
    security privileges of the superuser (root).

Steps

 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

### 1. Install git

    $ sudo apt-get install git

You will be prompted for your root password (enter it).

### 2. Install pip

    $ sudo apt-get install python-pip

### 3. Install python-novaclient

OpenStack has its own python client, which can be used for most tasks.
The package is called python-novaclient.

    $ sudo pip install python-novaclient

### 4. Install python-keystoneclient

    $ sudo pip install python-keystoneclient

### 5. Install python-neutronclient

    $ sudo pip install python-neutronclient

### 6. Install httplib2.system\_ca\_certs\_locater

    $ sudo pip install httplib2.system_ca_certs_locater

Results

-   Your local control machine has now the tools that are needed for
    deployment in OpenStack environment

[Back to top](#provisioning-to-forge-iaas)

FORGE IaaS specify keypairs
============================================================================

In this task you will specify the keypair (SSH credentials) to access
the virtual machines.
 Keypair will be injected into virtual machine images when they are
launched.

You can either create a new keypair **(A)** or import an existing
keypair **(B)** with OpenStack web user interface.

See more information on SSH in [Getting Started with
OpenStack](3_OpenStackIaaSplatform.md#ssh-key)

Preconditions

-   You have user account and password for OpenStack usage
-   You have ssh credentials that you want to import and use (If you are
    using an existing keypair)

### A) Steps to create a new keypair

1.  Select **Access & Security** from the Manage Compute list

2.  Select **Keypairs** tab

3.  Press
    ![openstack security create keypair.jpg](/files/openstack_security_create_keypair.jpg) button.
    *Create Keypair* dialog opens.

    ![openstack security create keypair dialog.jpg](/files/openstack_security_create_keypair_dialog.jpg)

4.  Fill in Keypair Name

5.  Press **Create Keypair** button to create new keypair.

### B) Steps to use an existing keypair

1.  Select **Access & Security** from the Manage Compute list

2.  Select **Keypairs** tab

3.  Press
    ![openstack security import keypair.jpg](/files/openstack_security_import_keypair.jpg)
    button to import existing keypair. *Import Keypair* dialog opens.

    ![openstack security import keypair dialog.jpg](/files/openstack_security_import_keypair_dialog.jpg)

4.  Name your key.

5.  Paste your public key (starts with something like "ssh-rsa
    AAFAA...." or "ssh-dss AFAFA...") into the to *Public Key* field

6.  Press **Import Keypair** button to import the keypair.

Result

-   You have now a keypair listed in OpenStack *Access &
    Security* settings. This key is will be injected into virtual
    machine images when they are launched.

[Back to top](#provisioning-to-forge-iaas)

FORGE IaaS create virtual machine instances
============================================================================================================

The purpose of this task is to instantiate virtual machines for Plaza
environment on FORGE IaaS.
 See [Drupal-HA cluster
architecture](5_Exampleapplication.md#drupal-ha-cluster-architecture) for more information
on machine instances needed in Plaza.

Preconditions

-   You have user account and password for OpenStack usage
-   You have enough OpenStack resources for creating at least seven
    virtual machine instances

### 1. Steps for creating a Load Balancer instance

1.  Select **Instances** from the Manage Compute list

2.  Click
    ![openstack launch instance button.jpg](/files/openstack_launch_instance_button.jpg)
    button, the *Launch Instance* dialog appears

    ![openstack launch instance dialog.jpg](/files/openstack_launch_instance_dialog.jpg)

3.  Specify the details for Load Balancer instance.
    
     Plaza playbook expects all computing instances to be Debian!
    
    
     You should consider the instance flavor in order to allow the
    instance to withstand the load. You might want the Drupal instances
    to be at least small and the NFS/MySQL instances medium.

4.  Select *Access & Security* tab.

    ![openstack launch instance access dialog.jpg](/files/openstack_launch_instance_access_dialog.jpg)

5.  Set the instance access.

6.  Select *Networking* tab.

    ![openstack launch instance network dialog.jpg](/files/openstack_launch_instance_network_dialog.jpg)

7.  Select a network from *Available networks* by push button or drag
    and drop it into *Selected Network* box.

8.  Click
    ![openstack launch instance launch button.jpg](/files/openstack_launch_instance_launch_button.jpg) button.
    New Load Balancer instance row will appear on the *Instances* table.

Now you have launched one instance for Load Balancer

### 2. Repeat steps 1. - 8. for each of the following virtual machine instances:

**Drupal webserver cluster:** At least two nodes, scales out.

-   first instance for Drupal webservers cluster
-   second instance for Drupal webservers cluster
-   additional instance(s) for Drupal webservers cluster

**MySql HA cluster:** Two nodes, does not scale out.

-   first instance for MySql HA cluster
-   second instance for MySql HA cluster

**NFS HA cluster:** Two nodes, does not scale out.

-   first instance for NFS HA cluster
-   second instance for NFS HA cluster

Result

-   You have now at least seven virtual machine instances are launched.
-   All virtual machine instances are Active and Running.

Your OpenStack instances table should contain at least seven instances
and look something like this:

![openstack launch instance table.jpg](/files/openstack_launch_instance_table.jpg)

[Back to top](#provisioning-to-forge-iaas)

FORGE IaaS specify floating IPs
====================================================================================

In this task you will allocate floating IP addresses and assign them to
instances.

Preconditions

-   You have created instances for Drupal-HA cluster
-   You have enough free floating IP resources in OpenStack

Steps
 Select **Access & Security** from the Manage Compute list and select
**Floating IPs** tab.

### 1. Specify floating IP to Load Balancer

1.  Press
    ![openstack floating ip add button.jpg](/files/openstack_floating_ip_add_button.jpg) button.
    *Allocate Floating IP* dialog opens.

    ![openstack floating ip add dialog.jpg](/files/openstack_floating_ip_add_dialog.jpg)

2.  Specify floating IP pool.

3.  Press **Allocate IP** to allocate floating IP. New floating IP is
    now shown on *Floating IPs* table.

4.  Select Associate from the floating IP row, *Manage Floating IP
    Associations* dialog is shown

    ![ssh access floatip.jpg](/files/ssh_access_floatip.jpg)

5.  Select Load Balancer from the *Port to be assiacted* list.

6.  Press **Associate** button

### 2. Specify floating IP to NFS

Repeat the steps to associate new port to one of the NFS instance.

### 3. Specify floating IP to MySQL

Repeat the steps to associate new port to one of the MySQL instance.

### 4. Specify floating IP to Drupal

Repeat the steps to associate new port to one of the Drupal instance.

Result

-   You have now floating IPs attached to the instaces that need
    external access
-   Your floating IP table should have now floating IPs associated to
    Load Balancer, MySQL, NFS and Drupal virtual machine instances
    ![openstack floating ip table.jpg](/files/openstack_floating_ip_table.jpg)

[Back to top](#provisioning-to-forge-iaas)

FORGE IaaS configure security groups
==============================================================================================

The purpose of this task is to open SSH and HTTPS access to your Plaza
servers.
 Use OpenStack web user interface to define security group and open
access from you IP address block (this example uses 10.10.0.123/32 as
CIDR)

**NOTE:** This example shows how to define one security group for
accessing service from one IP address only.
 When the service is opened to actual production, you need to specify a
new security group for "World" access.

Please refer to [Security guidelines in OpenStack IaaS
platform](3_OpenStackIaaSplatform.md#security-guidelines) for more information on security
guidelines in FORGE IaaS.

Preconditions

-   You have OpenStack instances created

Steps

### 1. Create new security group

1.  Select **Access & Security** from the Manage Compute list

2.  Select **Security Groups** tab.

3.  Click
    ![openstack security create group button.jpg](/files/openstack_security_create_group_button.jpg)
    button, the *Create Security Group* dialog appears

    ![openstack security create group.jpg](/files/openstack_security_create_group.jpg)

4.  Specify the name and description for the group

5.  Click **Create Security Group**. New security group row will appear
    on the *Security Group*s table.

### 2. Add security group rules to allow access from your IP address block for testing

1.  Select **Edit rules** button from the created security group row,
    the default security rules for this group are shown:

    ![openstack security group rules.jpg](/files/openstack_security_group_rules.jpg)

2.  Click
    ![openstack security group rules add button.jpg](/files/openstack_security_group_rules_add_button.jpg)
    button, the *Add Rule* dialog appears

    ![openstack security add rule dialog.jpg](/files/openstack_security_add_rule_dialog.jpg)

3.  Open port **22** from your IP address block. Click **Add** to add
    the security rule for SSH.

4.  Click
    ![openstack security group rules add button.jpg](/files/openstack_security_group_rules_add_button.jpg)
    button and open port **443** from your IP address block. Click
    **Add** to add the security rule for HTTPS.

5.  After you have added SSH and HTTPS rules, your Group rules table
    should have four rules and it should look like this:

    ![openstack security group rules added.jpg](/files/openstack_security_group_rules_added.jpg)

### 3. Add new security group to Load Balancer instance

1.  Select **Instances** from the Manage Compute list

2.  Click **Edit Security Groups** from the menu button on your Load
    Balancer intance row

    ![openstack security edit groups menu.jpg](/files/openstack_security_edit_groups_menu.jpg)
     the *Edit instance* dialog appears

    ![openstack security group edit instance.jpg](/files/openstack_security_group_edit_instance.jpg)

3.  Your new security group is shown on *All Security Groups* list.
    Click
    ![openstack security group edit add button.jpg](/files/openstack_security_group_edit_add_button.jpg)
    button, to add the group to *Instance Security Groups*. Security
    group is now moved to instance groups

    ![openstack security group edit instance2.jpg](/files/openstack_security_group_edit_instance2.jpg)

4.  Press **Save** to end instance security group editing

Result

-   You have now allowed access from your IP address block to
    OpenStack instances.

[Back to top](#provisioning-to-forge-iaas)

FORGE IaaS create and attach volumes
==============================================================================================

It is required, for the four machines supporting the two HA clusters to
have a volume attached.
 This task will create volumes and attach them to MySQL and NFS
instances.

The Plaza playbook defaults the location of this volumes on the **vdb**
block device.

Preconditions

-   You have enough OpenStack resources for creating at least four
    volumes
-   You have launched two MySql virtual machine instances
-   You have launched two NFS virtual machine instances

Steps

### 1. Create volume

1.  Select **Volumes** from the Manage Compute list

2.  Click **Create Volume** button, the *Create Volume* dialog
    appears![openstack create volume dialog.jpg](/files/openstack_create_volume_dialog.jpg)

3.  Specify the details for volume.

4.  Click **Create Volume**. New volume row will appear on the
    *Volumes* table.

Now you have created one volume.

### 2. Attach volume to instance

1.  Select **Edit Attachments** button from volume row, the *Manage
    Volume Attachment* dialog
    appears![openstack manage volume attachments dialog.jpg](/files/openstack_manage_volume_attachments_dialog.jpg)

2.  Select an instance to attach

3.  Click **Attach Volume** button. Attachment is now shown in the
    volumes *Attached To* column

### 3. Repeat volume creation and attaching steps for each of the instances:

**MySql HA cluster:**

-   first instance for MySql HA cluster
-   second instance for MySql HA cluster

**NFS HA cluster:**

-   first instance for NFS HA cluster
-   second instance for NFS HA cluster

Result

-   MySql and NFS instances have volumes attached to them
    ![openstack volumes table.jpg](/files/openstack_volumes_table.jpg)

[Back to top](#provisioning-to-forge-iaas)

FORGE IaaS configure SSH access
====================================================================================

Ansible executes modules over SSH (by default) so you need to allow SSH
access to virtual server instances.

It is not necessary or recommended to assign floating IPs to every
virtual machine on the project to have ssh access to them.
 It is possible to connect to all virtual machines using their private
IPs, given that at least one of them does have a floating IP associated,
by using an SSH jump host.
 SSH jump uses ProxyCommand to automatically execute ssh command on
remote host to jump to the next host and forward all traffic through.
 Usually the floating IP is given to a loadbalancer as it needs public
access anyway.

Preconditions

-   You have a machine with GNU/Linux distribution to use as control
    machine

Steps

### 1. Configure SSH jump

Configure `public_vm` as a jump host on localhost's `~/.ssh/config`
file. See [SSH Access in Ansible
Guidelines](#ssh-access)

### 2. Test access directly to the non-exposed virtual machines using their private IPs

    $ ssh username_for_private_vm1@192.168.0.10

Result

-   You can access all virtual machine instances using SSH.

[Back to top](#provisioning-to-forge-iaas)

FORGE IaaS update servers
========================================================================

In this task you will update the package list index and upgrade existing
software packages in your virtual machine instances.

Preconditons

-   You have launched virtual machine instances

Steps

The examples below use apt-get to install packages (as in a Debian-based
distribution like Ubuntu)

### 1. Update the Package Index

Update the lists of software from repository.

    $ sudo apt-get update

If you are prompted for your root password, enter it.

### 2. Upgrade Packages

After apt-get is done, run

    $ sudo apt-get upgrade

You will see a list of packages which should be installed to upgrade.
 You will be asked if you want to upgrade those packages, if yes, type
'Y' and hit enter.

### 3. Update all instances

Repeat the steps 1-2 for all your virtual machine instances.

Result

-   All instances are updated with the newest versions of packages and
    their dependencies. [Back to top](#provisioning-to-forge-iaas)

You have now created virtual machines to FORGE IaaS and the cloud
environment is ready for the deployment playbook.

[Continue to run the playbook](#deployment-to-production)

------------------------------------------------------------------------

------------------------------------------------------------------------

Provisioning to Amazon AWS
===========================================================================================

This guide describes the tasks needed to provision Plaza service
environment to Amazon cloud service.
 It describes how to set up virtual machines with a set amount of
resources, attach various types of storage to the machines and connect
them using virtual networks. You will also configure SSH access to newly
created virtual machine instances.

Cloud Portal -&gt;<https://aws.amazon.com/>

Documentation -&gt; <https://aws.amazon.com/documentation/>

Provisioning tasks
 The following table shows the actions to deploy Plaza (Drupal-HA
cluster) digital service to Amazon AWS.
 The columns in the table define the tool/area what the action relates
to and where the action should be performed.

| Control machine (localhost) | Amazon AWS | Server Instances |
|-----------------------------|------------|------------------|
| [1. Install tools](#amazon-aws-install-tools) | [2. Specify keypairs](#amazon-aws-specify-keypairs)  | |
| | [3. Configure security groups](#amazon-aws-configure-security-groups) | |
| | [4. Create virtual machine instances](#amazon-aws-create-virtual-machine-instances) | |
| | [5. Create and attach volumes](#amazon-aws-create-and-attach-volumes) | |
| [6. Test SSH access](#amazon-aws-test-ssh-access) | | [7. Update servers](#amazon-aws-update-servers) |

Amazon AWS install tools
======================================================================

In this task you will configure your localhost to be used as control
machine for Amazon AWS environment.
 You will install the following packages and tools needed for Plaza
deployment:

	Tool   Description
	------ ---------------------------------------------------------
	git    Distributed revision control and source code management
	pip    Tool for installing and managing Python packages

Preconditions

-   You have a machine with GNU/Linux distribution to use as control
    machine
-   Your user account has the privileges to run programs with the
    security privileges of the superuser (root).

Steps
 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Install git
------------------------------------------------------------------

    $ sudo apt-get install git

You will be prompted for your root password (enter it).

2. Install pip
------------------------------------------------------------------

    $ sudo apt-get install python-pip

Result

-   Your local control machine has now the tools that are needed for
    deployment in Amazon AWS environment

[Back to top](#provisioning-to-amazon-aws)

Amazon AWS specify keypairs
============================================================================

You can use Amazon EC2 to create your keypair. Alternatively, you could
use a third-party tool and then import the public key to Amazon EC2.
 Each keypair requires a name. Be sure to choose a name that is easy to
remember. Amazon EC2 associates the public key with the name that you
specify as the key name.

Preconditions

-   You have user account and password for Amazon AWS usage
-   You have ssh credentials that you want to import and use (If you are
    using an existing keypair). The keys that Amazon EC2 uses are
    1024-bit SSH-2 RSA keys.

Steps

A) Steps to create a new keypair
------------------------------------------------------------------------------------------------------

1.  You can create a keypair using the Amazon EC2 console or the
    command line. See -&gt; Creating Your Key Pair Using Amazon EC2

B) Steps to use an existing keypair
------------------------------------------------------------------------------------------------------------

1.  import the public key to Amazon EC2. See -&gt; Importing Your Own
    Key Pair to Amazon EC2

Result

-   If the keypair is in the displayed list of keypairs, you have
    successfully created/imported a keypair to Amazon AWS.

[Back to top](#provisioning-to-amazon-aws)

Amazon AWS configure security groups
==============================================================================================

To enable network access to your instances, you must allow inbound
traffic to your instance. To open a port for inbound traffic, add a rule
to a security group. When you launch new instances, associate the
security group with your instance.

Preconditions

-   You have user account and password for Amazon EC2 usage

Steps

1. Create security group
--------------------------------------------------------------------------------------

To create a security group in Amazon EC2., see Creating a security group

Result

You should have new security group listed in Amazon EC2 Management
Console:

 ![aws security.png](/files/aws_security.png)

[Back to top](#provisioning-to-amazon-aws)

Amazon AWS create virtual machine instances
============================================================================================================

The purpose of this task is to instantiate virtual machines for Plaza
environment on Amazon AWS Cloud.

See [Drupal-HA cluster
architecture](5_Exampleapplication.md#drupal-ha-cluster-architecture) for more information
on machine instances needed in Plaza.
 For more information on Linux instances in Amazon, see Getting Started
with Amazon EC2 Linux Instances

Preconditions

-   You have user account and password for Amazon EC2 usage
-   You have enough Amazon AWS resources for creating at least seven
    virtual machine instances

Steps

1. - 8. Create instances
-----------------------------------------------------------------------------------

To create an instance in Amazon EC2., see Launch an Amazon EC2 Instance

Create the following virtual machine instances:

1.  Instance for Load Balancer
2.  Primary instance for NFS HA cluster
3.  Secondary instance for NFS HA cluster
4.  Primary instance for MySql HA cluster
5.  Secondary instance for MySql HA cluster
6.  First instance for Drupal webservers cluster
7.  Second instance for Drupal webservers cluster
8.  Additional instance(s) for Drupal webservers cluster (OPTIONAL)

Result

-   You have now at least seven virtual machine instances are launched.
-   All virtual machine instances are running.

Your EC2 instances table should contain at least seven instances and
look something like this:

 ![aws instances.jpg](/files/aws_instances.jpg)

[Back to top](#provisioning-to-amazon-aws)

Amazon AWS create and attach volumes
==============================================================================================

It is required, for the four machines supporting the two HA clusters to
have a volume attached.
 This task will create volumes and attach them to MySQL and NFS
instances.

Preconditions

-   You have user account and password for Amazon Cloud usage

Steps

1. Create a volume for primary NFS instance
----------------------------------------------------------------------------------------------------------------------------

See Creating a New Amazon EBS Volume

2. Attach volume to primary NFS instance
----------------------------------------------------------------------------------------------------------------------

See Attaching an Amazon EBS Volume to an Instance

3. Repeat volume creation and attaching steps for each of the following instances:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-   Secondary instance for NFS HA cluster
-   Primary instance for MySql HA cluster
-   Secondary instance for MySql HA cluster

Result

-   MySql and NFS instances have volumes attached to them

Your Volumes list in Elastic Block Store in Amazon shows four volumes
and each volume is *Attached* to an instance.

 ![aws volumes.jpg](/files/aws_volumes.jpg)

[Back to top](#provisioning-to-amazon-aws)

Amazon AWS test SSH access
==========================================================================

Ansible executes modules over SSH (by default) so you need to test SSH
access to virtual server instances.

Preconditions

-   You have a machine with GNU/Linux distribution to use as control
    machine
-   You have created virtual machines with Amazon AWS cloud

Steps
 Test access to the virtual machines using their public IPs

    $ ssh username@public_ip_to_instance

Result

You can access all virtual machine instances using SSH.

[Back to top](#provisioning-to-amazon-aws)

Amazon AWS update servers
========================================================================

In this task you will update the package list index and upgrade existing
software packages in your virtual machine instances.

Preconditions

-   You have launched virtual machine instances

Steps

 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Update the Package Index
--------------------------------------------------------------------------------------------

Update the lists of software from repository.

    $ sudo apt-get update

If you are prompted for your root password, enter it.

2. Upgrade Packages
----------------------------------------------------------------------------

After apt-get is done, run

    $ sudo apt-get upgrade

You will see a list of packages which should be installed to upgrade.
 You will be asked if you want to upgrade those packages, if yes, type
'Y' and hit enter.

3. Update all instances
------------------------------------------------------------------------------------

Repeat the steps 1-2 for all your virtual machine instances.

Result

-   All instances are updated with the newest versions of packages and
    their dependencies.

[Back to top](#provisioning-to-amazon-aws)

You have now created virtual machines to Amazon AWS and the cloud
environment is ready for the deployment playbook.

 [Continue to run the playbook](#deployment-to-production)

------------------------------------------------------------------------

Provisioning to Cybercom Cloud
=======================================================================================================

This guide describes the tasks needed to provision Plaza service
environment to Cybercom Cloud service.
 It describes how to set up virtual machines with a set amount of
resources, attach various types of storage to the machines and connect
them using virtual networks. You will also configure SSH access to newly
created virtual machine instances.

Cloud Portal -&gt; <https://cloud.cybercom.com/portal/>

Documentation -&gt; <https://confluence.cybercom.com/>

Service Desk -&gt; <sd@cybercom.com>

Differences when compared with FORGE IaaS

-   You cannot specify keypairs for the Cybercom Cloud environment. You
    need to import SSH public key to each virtual machine when instance
    is created.
-   Public IP is assigned to each instance during instance creation. You
    cannot specify floating IPs.
-   You cannot configure security groups. Cybercom Cloud does not have
    Security Group concept.

Provisioning tasks
 The following table shows the actions to deploy Plaza (Drupal-HA
cluster) digital service to Cybercom Cloud.
 The columns in the table define the tool/area what the action relates
to and where the action should be performed.

| Control machine (localhost) | Cybercom Cloud | Server Instances |
|-----------------------------|----------------|------------------|
| [1. Install tools](#cybercom-cloud-install-tools)          | | |
| | [2. Create virtual machine instances](#cybercom-cloud-create-virtual-machine-instances) | |
| | [3. Create and attach volumes](#cybercom-cloud-create-and-attach-volumes) | |
| [4. Test SSH access](#cybercom-cloud-test-ssh-access) | | [5. Update servers](#cybercom-cloud-update-servers)]

Cybercom Cloud install tools
==========================================================================

In this task you will configure your localhost to be used as control
machine for Cybercom cloud environment.
 You will install the following packages and tools needed for Plaza
deployment:

	Tool   Description
	------ ---------------------------------------------------------
	git    Distributed revision control and source code management
	pip    Tool for installing and managing Python packages

Preconditions

-   You have a machine with GNU/Linux distribution to use as control
    machine
-   Your user account has the privileges to run programs with the
    security privileges of the superuser (root).

Steps

 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Install git
----------------------------------------------------------------------

    $ sudo apt-get install git

You will be prompted for your root password (enter it).

2. Install pip
----------------------------------------------------------------------

    $ sudo apt-get install python-pip

Result

-   Your local control machine has now the tools that are needed for
    deployment in Cybercom cloud environment

[Back to top](#provisioning-to-cybercom-cloud)

Cybercom Cloud create virtual machine instances
================================================================================================================

The purpose of this task is to instantiate virtual machines for Plaza
environment on Cybercom Cloud
 See [Drupal-HA cluster
architecture](5_Exampleapplication.md#drupal-ha-cluster-architecture) for more information
on machine instances needed in Plaza.

Preconditions

-   You have user account and password for Cybercom Cloud usage
-   You have enough resources for creating at least seven virtual
    machine instances

1. Steps for creating a Load Balancer instance
--------------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

1.  Select **Create New** from the top menu in Home view. *Create new
    capacity* view is shown with a list of available instance templates.
    ![cybercom create new.png](/files/cybercom_create_new.png)
2.  Choose a instance template from and press launch. *Create new
    instance* view is shown.
    ![cybercom create new instance.png](/files/cybercom_create_new_instance.png)
3.  Set name and properties for new instance.
     The name may contain upper case and lower case letters (a-z, A-Z),
    numbers (0-9), and dashes (-). The first character must be a letter.

4.  Press **Create** button. A dialog for SSH key is shown:

    ![cybecom import ssh key.png](/files/cybecom_import_ssh_key.png)

5.  Import or download your SSH public key. Key will be injected into
    virtual machine images when they are launched.

6.  New instance is shown in My Cloud view with status "Pending"
    

    ![cybercom instance created.png](/files/cybercom_instance_created.png)

7.  When the instance has successfully started, you can open instance by
    clicking the instance name in top of the square. Open the network
    information by clicking the + sign in Network to see the assigned
    IPs.
    

    ![cybercom instance created2.png](/files/cybercom_instance_created2.png)

2. Repeat steps 1. - 7. for each of the following virtual machine instances:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Drupal webserver cluster:** At least two nodes, scales out.

-   first instance for Drupal webservers cluster
-   second instance for Drupal webservers cluster
-   additional instance(s) for Drupal webservers cluster

**MySql HA cluster:** Two nodes, does not scale out.

-   first instance for MySql HA cluster
-   second instance for MySql HA cluster

**NFS HA cluster:** Two nodes, does not scale out.

-   first instance for NFS HA cluster
-   second instance for NFS HA cluster

Result

-   You have now at least seven virtual machine instances are launched.
-   All instances are Running.

Your Cybercom Cloud instances in My Cloud view should contain at least
seven instances and look something like this:

![cybercom my cloud.png](/files/cybercom_my_cloud.png)

[Back to top](#provisioning-to-cybercom-cloud)

Cybercom Cloud create and attach volumes
==================================================================================================

It is required, for the four machines supporting the two HA clusters to
have a volume attached.
 This task will create volumes and attach them to MySQL and NFS
instances.

Preconditions

-   You have launched two MySql instances
-   You have launched two NFS instances

Steps

1. Create volume
--------------------------------------------------------------------------

1.  Select **Create New** from the top menu in Home view. *Create new
    capacity* view is shown with a list of available instance templates,
    also an template for Block Storage Volume is shown.

    ![cybercom create volume.png](/files/cybercom_create_volume.png)

2.  Choose Block Storage Volume template from template list and
    press launch. *Create new volume* view is shown.

    ![cybercom create volume dialog.png](/files/cybercom_create_volume_dialog.png)

3.  Set the name and size for new volume.

4.  Press **Create** button. A new volume is shown in My Cloud view. The
    volume is shown in gray color with status *Detached*

    ![cybercom create volume detached.png](/files/cybercom_create_volume_detached.png)

2. Attach volume to instance
--------------------------------------------------------------------------------------------------

1.  Open the instance and press **+** on the Storage. **Add storage**
    selection button is shown.

    ![cybercom create volume attach.png](/files/cybercom_create_volume_attach.png)

2.  Click
    ![cybercom create volume add button.png](/files/cybercom_create_volume_add_button.png)-button,
    *Select volume* dialog is shown:

    ![cybercom create volume attach dialog.png](/files/cybercom_create_volume_attach_dialog.png)

3.  Select the volume from the list and press **Select**. New volume is
    shown on instance storages:

    ![cybercom volume attached.png](/files/cybercom_volume_attached.png)

3. Repeat volume creation and attaching steps for each of the instances:
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**MySql HA cluster:**

-   first instance for MySql HA cluster
-   second instance for MySql HA cluster

**NFS HA cluster:**

-   first instance for NFS HA cluster
-   second instance for NFS HA cluster

Result

-   MySql and NFS instances have volumes attached to them

Your Cybercom Cloud instances in My Cloud view should contain four
volumes and show them all with status Attached:

![cybercom my cloud volumes.png](/files/cybercom_my_cloud_volumes.png)

[Back to top](#provisioning-to-cybercom-cloud)

Cybercom Cloud test SSH access
==============================================================================

Ansible executes modules over SSH (by default) so you need to test SSH
access to virtual server instances.

Preconditions

You have a machine with GNU/Linux distribution to use as control
machine
 You have created virtual machines with Cybercom cloud

Steps
 Test access to the virtual machines using their public IPs

    $ ssh username@public_ip_to_instance

Result

You can access all virtual machine instances using SSH.
 [Back to top](#provisioning-to-cybercom-cloud)

Cybercom Cloud update servers
============================================================================

In this task you will update the package list index and upgrade existing
software packages in your virtual machine instances.

Preconditions

-   You have launched virtual machine instances

Steps

 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Update the Package Index
------------------------------------------------------------------------------------------------

Update the lists of software from repository.

    $ sudo apt-get update

If you are prompted for your root password, enter it.

2. Upgrade Packages
--------------------------------------------------------------------------------

After apt-get is done, run

    $ sudo apt-get upgrade

You will see a list of packages which should be installed to upgrade.
 You will be asked if you want to upgrade those packages, if yes, type
'Y' and hit enter.

3. Update all instances
----------------------------------------------------------------------------------------

Repeat the steps 1-2 for all your virtual machine instances.

Result

-   All instances are updated with the newest versions of packages and
    their dependencies.

[Back to top](#provisioning-to-cybercom-cloud)

You have now created virtual machines to Cybercom Cloud and the cloud
environment is ready for the deployment playbook.

 [Continue to run the playbook](#deployment-to-production)

------------------------------------------------------------------------


------------------------------------------------------------------------


------------------------------------------------------------------------

Provisioning to Microsoft Azure
==========================================================================================================

This guide describes the tasks needed to provision Plaza service
environment to Microsoft Azure cloud service.
 It describes how to set up virtual machines with a set amount of
resources, attach various types of storage to the machines and connect
them using virtual networks. You will also configure SSH access to newly
created virtual machine instances.

Cloud Portal -&gt; <http://manage.windowsazure.com>

Documentation -&gt; <http://azure.microsoft.com/en-us/documentation/>

 Differences when compared with FORGE IaaS

-   You cannot upload keypairs. You can upload an X.509 certificate (in
    .cer or .pem format) or provide your password to sign in to a
    virtual machine when virtual machine is created. Learn more: How to
    Use SSH with Linux on Azure

-   Public IP is assigned to each instance during instance creation. You
    cannot specify floating IPs.

Provisioning Tasks
 The following table shows the actions to deploy Plaza (Drupal-HA
cluster) digital service to Microsoft Azure Cloud.
 The columns in the table define the tool/area what the action relates
to and where the action should be performed.

| Control machine (localhost) | Microsoft Azure | Server Instances |
|-----------------------------|-----------------|------------------|
| [1. Install tools](#microsoft-azure-install-tools) | | |
| | [2. Create virtual machine instances](#microsoft-azure-create-virtual-machine-instances) | |
| | [3. Configure endpoints](#microsoft-azure-configure-endpoints) | |
| | [4. Create and attach volumes](#microsoft-azure-create-and-attach-volumes) | |
| [5. Test SSH access](#microsoft-azure-test-ssh-access) | | [6. Update servers](#microsoft-azure-update-servers) |

Microsoft Azure install tools
===========================================================================

In this task you will configure your localhost to be used as control
machine for Microsoft Azure environment.
 You will install the following packages and tools needed for Plaza
deployment:

	Tool   Descrption
	------ ---------------------------------------------------------
	git    Distributed revision control and source code management
	pip    Tool for installing and managing Python packages

Preconditions
 \* You have a machine with GNU/Linux distribution to use as control
machine
 \* Your user account has the privileges to run programs with the
security privileges of the superuser (root).

Steps
 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Install git
-----------------------------------------------------------------------

    $ sudo apt-get install git

You will be prompted for your root password (enter it).

2. Install pip
-----------------------------------------------------------------------

    $ sudo apt-get install python-pip

Results

-   Your local control machine has now the tools that are needed for
    deployment in MIcrosoft Azure environment

[Back to top](#provisioning-to-microsoft-azure)

Microsoft Azure create virtual machine instances
=================================================================================================================

The purpose of this task is to instantiate virtual machines for Plaza
environment on MIcrosoft Azure Cloud.

See [Drupal-HA cluster
architecture](5_Exampleapplication.md#drupal-ha-cluster-architecture) for more information
on machine instances needed in Plaza.
 For more information on Linux instances in Microsoft Azure, see
Introduction to Linux on Azure

Preconditions

-   You have a MIcrosoft account for MIcrosoft Azure usage

Steps

1. - 8. Create instances
----------------------------------------------------------------------------------------

To create an instance in Azure Cloud., see How to create the virtual
machine

Create the following virtual machine instances:

1.  Instance for Load Balancer
2.  Primary instance for NFS HA cluster
3.  Secondary instance for NFS HA cluster
4.  Primary instance for MySql HA cluster
5.  Secondary instance for MySql HA cluster
6.  First instance for Drupal webservers cluster
7.  Second instance for Drupal webservers cluster
8.  Additional instance(s) for Drupal webservers cluster (OPTIONAL)

Result

-   You have now at least seven virtual machine instances launched.
-   All virtual machine instances are running.

Your Azure Cloud instances table should contain at least seven instances
and look something like this:
 ![azure instances.jpg](/files/azure_instances.jpg)

[Back to top](#provisioning-to-microsoft-azure)

Microsoft Azure configure endpoints
=======================================================================================

All virtual machines that you create in Azure can automatically
communicate using a private network channel with other virtual machines
in the same cloud service or virtual network.
 However, other resources on the Internet or other virtual networks
require endpoints to handle the inbound network traffic to the virtual
machine.

When you create a virtual machine in the Management Portal, you can
create these endpoints, such as for Secure Shell (SSH).
 After you create the virtual machine, you can create additional
endpoints as needed.
 You also can manage incoming traffic to the public port by configuring
rules for the network access control list (ACL) of the endpoint.

Preconditions

-   You have created virtual machine instances

Steps
 To create additional endpoints in Azure cloud, see How to Set Up
Endpoints to a Virtual Machine

Result

-   You have now specified network access to instances.

[Back to top](#provisioning-to-microsoft-azure)

Microsoft Azure create and attach volumes
===================================================================================================

It is required, for the four machines supporting the two HA clusters to
have a volume attached.
 The easiest way to do this is in Microsoft Azure is to attach an empty
data disk to the machine.
 This task will create volumes and attach them to MySQL and NFS
instances.

Preconditions

-   You have launched two MySql machine instances
-   You have launched two NFS machine instances

Steps

1. Attach an empty disk to instance
-----------------------------------------------------------------------------------------------------------------

See How to attach a data disk to the new virtual machine

2. Repeat step 1. for each of the instances
--------------------------------------------------------------------------------------------------------------------------------

Attach empty disk to NFS and MySQL instances.

Results

-   MySql and NFS instances have volumes attached to them.
-   You can see the attached volumes as data disks in the disks section
    of the instance details.
    ![azure volumes.jpg](/files/azure_volumes.jpg)

[Back to top](#provisioning-to-microsoft-azure)

Microsoft Azure test SSH access
===============================================================================

Ansible executes modules over SSH (by default) so you need to test SSH
access to virtual server instances.

Preconditions

-   You have a machine with GNU/Linux distribution to use as control
    machine
-   You have created virtual machines with MIcrosoft Azure Cloud

Steps
 1. Test access to the virtual machines using their public IPs

    ssh -i  myPrivateKey.key  azureuser@servicename.cloudapp.net

Result

-   You can access all virtual machine instances using SSH.

[Back to top](#provisioning-to-microsoft-azure)

Microsoft Azure update servers
=============================================================================

In this task you will update the package list index and upgrade existing
software packages in your virtual machine instances.

Preconditions

-   You have launched virtual machine instances

Steps

 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Update the Package Index
-------------------------------------------------------------------------------------------------

Update the lists of software from repository.

    $ sudo apt-get update

If you are prompted for your root password, enter it.

2. Upgrade Packages
---------------------------------------------------------------------------------

After apt-get is done, run

    $ sudo apt-get upgrade

You will see a list of packages which should be installed to upgrade.
 You will be asked if you want to upgrade those packages, if yes, type
'Y' and hit enter.

3. Update all instances
-----------------------------------------------------------------------------------------

Repeat the steps 1-2 for all your virtual machine instances.

Result

-   All instances are updated with the newest versions of packages and
    their dependencies.

[Back to top](#provisioning-to-microsoft-azure)


 You have now created virtual machines to Microsoft Azure and the cloud
environment is ready for the deployment playbook.

 [Continue to run the playbook](#deployment-to-production)

------------------------------------------------------------------------


------------------------------------------------------------------------

Provisioning to Rackspace
========================================================================================

This guide describes the tasks needed to provision Plaza service
environment to Rackspace cloud service.
 It describes how to set up virtual machines with a set amount of
resources, attach various types of storage to the machines and connect
them using virtual networks. You will also configure SSH access to newly
created virtual machine instances.

Cloud Portal -&gt; <https://mycloud.rackspace.com>

Documentation -&gt; <http://www.rackspace.com/knowledge_center/>

Differences when compared with FORGE IaaS

-   Public IP is assigned to each instance during instance creation. You
    cannot specify floating IPs.
-   Rackspace does not have Security Group concept.

Provisioning tasks
 The following table shows the actions to deploy Plaza (Drupal-HA
cluster) digital service to Rackspace Cloud.
 The columns in the table define the tool/area what the action relates
to and where the action should be performed.

| Control machine (localhost) | Rackspace | Server Instances |
|-----------------------------|-----------|------------------|
| [1. Install tools](#rackspace-install-tools) | [2. Specify keypairs](#rackspace-specify-keypairs) | | 
| | [3. Create virtual machine instances](#rackspace-create-virtual-machine-instances) | |
| | [4. Create and attach volumes](#rackspace-create-and-attach-volumes) | |
| [5. Test SSH access](#rackspace-test-ssh-access) | | [6. Update servers](#rackspace-update-servers) |

Rackspace install tools
=====================================================================

In this task you will configure your localhost to be used as control
machine for Rackspace environment.
 You will install the following packages and tools needed for Plaza
deployment:

	Tool   Descrption
	------ ---------------------------------------------------------
	git    Distributed revision control and source code management
	pip    Tool for installing and managing Python packages

Preconditions

-   You have a machine with GNU/Linux distribution to use as control
    machine
-   Your user account has the privileges to run programs with the
    security privileges of the superuser (root).

Steps

 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Install git
-----------------------------------------------------------------

    $ sudo apt-get install git

You will be prompted for your root password (enter it).

2. Install pip
-----------------------------------------------------------------

    $ sudo apt-get install python-pip

Result

-   Your local control machine has now the tools that are needed for
    deployment in Rackspace environment

[Back to top](#Provisioning-to-Rackspace)

Rackspace specify keypairs
===========================================================================

In this task you will import your public key to Rackspace.

For more information on security in Rackspace Cloud, see Rackspace Cloud
Essentials - Basic Cloud Server Security

Preconditions

-   You have user account and password for Rackspace Cloud usage
-   You have a ssh keypair that you want to import and use

Steps

1. Add Public Key to Rackspace
-------------------------------------------------------------------------------------------------

1.  Select **SSH Keys** in top menu. *SSH keys* view is shown.

2.  Click **Add Public Key** button. *Add Public Key* dialog is shown:

    ![rackspace import key.jpg](/files/rackspace_import_key.jpg)

3.  Fill in key name. Be sure to choose a name that is easy to remember.
    Rackspace associates the public key with the name that you specify
    as the key name.

4.  Paste your public key (starts with something like "ssh-rsa
    AAFAA...." or "ssh-dss AFAFA...") into the to Public Key field.

5.  Click **Add Public Key** button to create the key.

Result

You have now a key listed in Rackspace SSH Keys view. This key is will
be injected into virtual machine images when they are launched.
 ![rackspace key.jpg](/files/rackspace_key.jpg)

[Back to top](#provisioning-to-rackspace)

Rackspace ceate virtual machine instances
===========================================================================================================

The purpose of this task is to instantiate virtual machines for Plaza
environment on Rackspace Cloud.

See [Drupal-HA cluster
architecture](5_Exampleapplication.md#drupal-ha-cluster-architecture) for more information
on machine instances needed in Plaza.
 For more information on cloud servers in Rackspace, see Getting Started
with Cloud Servers

Preconditions

-   You have user account and password for Rackspace Cloud usage
-   You have enough resources for creating at least seven virtual
    machine instances

Steps

1. - 8. Create instances
----------------------------------------------------------------------------------

To create an instance in Rackspace, see Rackspace Cloud Essentials -
Creating A Cloud Server

Create the following virtual machine instances:

1.  Instance for Load Balancer
2.  Primary instance for NFS HA cluster
3.  Secondary instance for NFS HA cluster
4.  Primary instance for MySql HA cluster
5.  Secondary instance for MySql HA cluster
6.  First instance for Drupal webservers cluster
7.  Second instance for Drupal webservers cluster
8.  Additional instance(s) for Drupal webservers cluster (OPTIONAL)

Result

-   You have now at least seven virtual machine instances launched.
-   All virtual machine instances are running.

Your Rackspace instances table should contain at least seven instances
and look something like this:

![rackspace instances.jpg](/files/rackspace_instances.jpg)

[Back to top](#provisioning-to-rackspace)

Rackspace create and attach volumes
=============================================================================================

It is required, for the four machines supporting the two HA clusters to
have a volume attached.
 This task will create volumes and attach them to MySQL and NFS
instances.

Preconditions

-   You have user account and password for Rackspace Cloud usage

Steps

1. Create and attach volume to primary NFS instance
-------------------------------------------------------------------------------------------------------------------------------------------

See Create and Attach a Cloud Block Storage Volume

2. Repeat volume creation and attaching steps for each of the following instances:
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-   Secondary instance for NFS HA cluster
-   Primary instance for MySql HA cluster
-   Secondary instance for MySql HA cluster

Result

-   MySql and NFS instances have volumes attached to them

Your Block Storage Volumes tabale in Rackspace Cloud shows four volumes
and column *Attached to* lists instances that volumes are attached to.

![rackspace volume list.jpg](/files/rackspace_volume_list.jpg)

[Back to top](#provisioning-to-rackspace)

Rackspace test SSH access
=========================================================================

Ansible executes modules over SSH (by default) so you need to test SSH
access to virtual server instances.

Preconditions

You have a machine with GNU/Linux distribution to use as control
machine
 You have created virtual machines with Rackspace cloud

Steps
 Test access to the virtual machines using their public IPs

    $ ssh username@public_ip_to_instance

Result

You can access all virtual machine instances using SSH.

[Back to top](#provisioning-to-rackspace)

Rackspace update servers
=======================================================================

In this task you will update the package list index and upgrade existing
software packages in your virtual machine instances.

Preconditions

-   You have launched virtual machine instances

Steps
 The examples below use apt-get to install packages (as in a
Debian-based distribution like Ubuntu)

1. Update the Package Index
-------------------------------------------------------------------------------------------

Update the lists of software from repository.

    $ sudo apt-get update

If you are prompted for your root password, enter it.

2. Upgrade Packages
---------------------------------------------------------------------------

After apt-get is done, run

    $ sudo apt-get upgrade

You will see a list of packages which should be installed to upgrade.
 You will be asked if you want to upgrade those packages, if yes, type
'Y' and hit enter.

3. Update all instances
-----------------------------------------------------------------------------------

Repeat the steps 1-2 for all your virtual machine instances.

Result

-   All instances are updated with the newest versions of packages and
    their dependencies.

[Back to top](#provisioning-to-rackspace)


 You have now created virtual machines to Rackspace and the cloud
environment is ready for the deployment playbook.

 [Continue to run the playbook](#deployment-to-production)

Deployment to production
=====================================================================================

This guide describes the steps that needs to be taken to deploy the
digital service developed in FORGE Service Lab from testing to
production. The guidelines use Plaza playbook as an example deployment
playbook which deploys Drupal-HA cluster service environment to cloud
platform. Deployed service consists multiple virtual servers with
scalable Drupal webserver. See [Drupal-HA cluster
architecture](5_Exampleapplication.md#drupal-ha-cluster-architecture) for more information
about Plaza environment.

Deployment phase deploys the Plaza environment to cloud. Besides
installing the tools needed for running playbooks, this phase configures
and runs the Plaza playbook. This phase has no cloud platform specific
tasks and it is similar to all cloud platforms. The following steps show
how to deploy Plaza environment to a cloud platform.

1.  Install Ansible on your control machine
2.  Get Plaza playbook from GitLab
3.  Configure Inventory
4.  Check volume partitions by running the list-partitions playbook
    against your inventory
5.  Define playbook group variables in order to set the required
    variables for Plaza playbook
6.  Run Plaza playbook against your inventory

Make sure that you have successfully completed the cloud environment
provisioning and you can access the virtual servers and volumes before
running the playbook. At the end of this page, the chapter seven lists
some of the possible problems that you may encounter when running the
Plaza playbook.

1. Install Ansible
========================================================================

In this task you will install Ansible on your control machine. see
[Ansible](#ansible)

Preconditions

-   You have a control machine with installed GNU/Linux distribution.
-   You have installed python-pip

Steps

### 1. Install Ansible on your control machine

    $ sudo pip install ansible

If you need to upgrade Ansible, add argument --upgrade to pip command

### 2. Check Ansible version

Installed Ansible version should be atleast 1.6.x

    $ ansible --version

### 3. Configure SSH-agent forwarding

Add ssh\_args in Ansible configuration. See
<http://docs.ansible.com/intro_configuration.html> for more information
on Ansible confiuration file.

    ...
    [ssh_connection]
    ssh_args = -o ForwardAgent=yes
    ...

Changes can be made and used in Ansible configuration file which will be
processed in the following order:
 1) ANSIBLE\_CONFIG (an environment variable)
 2) ansible.cfg (in the current directory)
 3) .ansible.cfg (in the home directory)
 4) /etc/ansible/ansible.cfg

Result

-   Ansible is now ready for running Plaza playbook [Back to
    top](#deployment-to-production)

2. Get Plaza playbook from GitLab
======================================================================================================

This task will retrieve Plaza playbook for use.

Preconditions

-   You have access rights to [GitLab](https://git.forgeservicelab.fi)
    code hosting
-   You have git installed

Steps

### 1. Retrieve Plaza playbook

### 2. Install dependent roles

Use git to clone playbook repositories, see [Ansible
Guidelines](#retrieving-playbooks-for-use)

Result

-   You have Plaza playbook and dependent Plaza roles installed

[Back to top](#deployment-to-production)

3. Configure Inventory
================================================================================

In this task you will create the inventory file that Ansible uses to
specify the hosts and groups.
 For more information on Ansible inventory usage, see
<http://docs.ansible.com/intro_inventory.html>

Preconditions

-   You have retrieved Plaza playbook from GitLab
-   Your control machine has Ansible installed

Steps

### 1. Configure Ansible so that it takes the lists of hosts from OpenStack client

See [Inventory setup for the FORGE
OpenStack](#inventory-setup-for-the-forge-openstack)

### 2. Check Ansible against your virtual machine instance

    $ ansible all -m ping

Ansible will attempt to remote connect to the machines using your
current user name, just like SSH would. To override the remote user
name, just use the ‘-u’ parameter.
 Returned result from ping should look like the following

    <your_ip> | success >> {
        "changed": false, 
        "ping": "pong"
    }

### 3. Edit the plaza.inventory

Specify the correct IP addresses in Plaza inventory file. Edit the
example file: *plaza.inventory*

    127.0.0.1

    [loadbalancer]
    lb1 ansible_ssh_host=<ip_to_load_balancer> primary=yes ansible_ssh_user=debian

    [drupal]
    drupal1 ansible_ssh_host=<ip_to_primary_drupal> primary=yes ansible_ssh_user=debian
    drupal2 ansible_ssh_host=<ip_to_secondary_drupal> ansible_ssh_user=debian

    [nfs]
    nfs1 ansible_ssh_host=<ip_to_primary_nfs> primary=yes ansible_ssh_user=debian
    nfs2 ansible_ssh_host=<ip_to_secondary_nfs> ansible_ssh_user=debian

    [mysql]
    mysql1 ansible_ssh_host=<ip_to_primary_mysql> primary=yes ansible_ssh_user=debian
    mysql2 ansible_ssh_host=<ip_to_secondary_mysql> ansible_ssh_user=debian

Result

-   Ansible has now correct inventory file and is able to access your
    virtual machine instances

[Back to top](#deployment-to-production)

4. Check volume partitions
========================================================================================

It is highly recommended to run the list-partitions playbook to identify
the actual device location on each of the virtual machines and override
the defaults with the block\_device variable. This task will verify that
Ansible works correctly against your Plaza environment and you have
MySQL and NFS correctly configured with volumes.

Preconditions

-   You have created your inventory file
-   You have NFS and MySQL instances launched and running

Steps

### 1. Run list-partitions playbook against your inventory

    $ ansible-playbook list-partitions.yml -i my.inventory

The list-partitions playbook will report unpartitioned devices as
skipped results.

Result

-   Ansible works correctly against your Plaza environment
-   The four machines supporting the two HA clusters have a
    volume attached. list-partitions playbook recap should show the
    following:

<!-- -->

    ...
    PLAY RECAP ******************************************************************** 
    mysql1                     : ok=2    changed=0    unreachable=0    failed=0   
    mysql2                    : ok=2    changed=0    unreachable=0    failed=0   
    nfs1                          : ok=2    changed=0    unreachable=0    failed=0   
    nfs2                         : ok=2    changed=0    unreachable=0    failed=0  

Problems
 list-partitions playbook fails with error "SSH encountered an unknown
error during the connection." and play recap shows one or more
unreachable instances.

    mysql1                     : ok=0    changed=0    unreachable=1    failed=0   

Check IP address definitions in inventory.

 list-partitions playbook fails with error "SSH encountered an unknown
error. WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!"
 Check you SSH configuration, see [SSH Access in Ansible
Guidelines](#ssh-access)

You have changed instance IP addresses. Add correct host key in
ssh/known\_hosts to get rid of this message. Remove with:

    $ ssh-keygen -f "/home/username/.ssh/known_hosts" -R <ip_to_failing_instance>

[Back to top](#deployment-to-production)

5. Define playbook group variables
========================================================================================================

In this task you will define the Plaza role variables that define your
environment.
 Each role subdirectory has README file that contains the latest
information on role variables.

Preconditions

-   You have Plaza playbook on your control machine

Steps

### 1. Set common variables to Plaza playbook

Edit **group\_vars/all.yml** and set the role variables according to
file comments

| Variable | Descpription | 
|----------|--------------|
| IS_TARGET_OPENSTACK | Boolean defining whether the target environment is deployed on OpenStack |
| OS_AUTH_URL | URL of OpenStack's keystone service |
| OS_USERNAME | Username of OpenStack account allowed to make changes|
| OS_PASSWORD | Password for the account|
| OS_PROJECT | OpenStack project holding the target VMs|
| ALLOWED_IPS | List of IPs allowed to use the HA backends typically the webserver public IPs. |
| web_domain | FQDN of the provisioned website|
| NFS_VIRTUAL_IP | Service IP for the NFS HA cluster|
| MySQL_VIRTUAL_IP | Service IP for the MySQL HA cluster|
| certificate_prefix | Name of the SSL certificate files up to but not including file extension|
| drupal_database | Name of the database for Drupal|
| mailname | FQDN for Drupal's outgoing mail server|
| block_device | Device descriptor of the data disk for HA clusters. DO NOT set here if it is not the same on all target machines.|
| backends | List of webservers as seen from the loadbalancer. |


Example group\_vars/all.yml content:

    ---
    IS_TARGET_OPENSTACK: True
    OS_AUTH_URL: https://cloud.forgeservicelab.fi:5001/v2.0

    OS_USERNAME: myusername
    OS_PASSWORD: mypassword

    OS_PROJECT: myproject
    ALLOWED_IPS:
        - 196.166.34.10
        - 196.166.34.20
        - 196.166.34.30
    web_domain: mydomain.fi
    NFS_VIRTUAL_IP: 196.166.34.50
    MySQL_VIRTUAL_IP: 196.166.34.60
    certificate_prefix: mycertprefix
    drupal_database: mydrupaldb
    mailname: mail.example.com
    block_device: /dev/vdb
    backends:
        - 197.168.4.30
        - 197.168.4.20

### 2. Define Load Blancer role variables

Edit **group\_vars/loadbalancer.yml** and set floating IP for Load
Balancer

    ---
    OS_FLOATIP: <ip_to_my_loadbalancer>

### 3. Define MySQL role variables

Edit **group\_vars/mysql.yml** and set floating IP for MySQL

    ---
    OS_FLOATIP: <ip_to_my_mysql>

### 4. Define NFS role variables

Edit **group\_vars/nfs.yml** and set floating IP for NFS

    ---
    OS_FLOATIP: <ip_to_my_nfs>

Result

-   You have common group variables set for the Plaza playbook

[Back to top](#deployment-to-production)

6. Run Plaza playbook
==============================================================================

This task will run the Plaza playbook and deploy the Drupal HA-cluster
environment to your OpenStack instances.

Precondtions

-   You have Drupal-HA cluster configured and running in FORGE IaaS
-   You have configured Ansible in your control machine so that it can
    connect and run playbooks against your Drupal-HA cluster
-   You have created Ansible inventory that reflects your Drupal-HA
    cluster environment

Steps

### Run Plaza playbook against your inventory

    $ ansible-playbook plaza.yml -i my.inventory

You can set Ansible's verbosity to obtain detailed logging '-vvvv' for
connection debugging.

Result

Play recap from your playbook run shows all tasks are completed
successfully:

: PLAY RECAP
\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
 drupal1 : ok=30 changed=9 unreachable=0 failed=0

 drupal2 : ok=26 changed=7 unreachable=0 failed=0

 lb1 : ok=27 changed=4 unreachable=0 failed=0

 mysql1 : ok=44 changed=9 unreachable=0 failed=0

 mysql2 : ok=41 changed=7 unreachable=0 failed=0

 nfs1 : ok=43 changed=7 unreachable=0 failed=0

 nfs2 : ok=41 changed=7 unreachable=0 failed=0

**You have now deployed Plaza environment to FORGE OpenStack.**

[Back to top](#deployment-to-production)

7. Problems you may encounter
==============================================================================================

Playbook fails with error in undefined role variables, such as *"One or
more undefined variables: 'OS\_xxx' is undefined"
 Look up the role from the TASK line preceding the error: TASK: \[ &lt;
role &gt; | &lt; task name &gt;\]*
 Check Plaza playbook role definitions that you have specified missing
role variable. See role README.md for further information about role
variables.

Check that you have set the environment variables for OpenStack
environment, see See [Getting started with
OpenStack](3_OpenStackIaaSplatform.md#rc-file-for-the-nova-command-line-tools)

 Playbook fails with error \*"SSH encountered an unknown error during
the connection."
 One or more instance address definitions are not correct, check for
typos in inventory definitions.

 Playbook fails in "Base packages" task when apt cannot authenticate
packages
 Update server software in your virtual machine instances, see [Update
servers](#8.-update-servers)

 ha-disk role fails with error \*"State change failed: (-2) Need access
to UpToDate data"
 You have problems with cluster nodes communicating with each other.
Check your instance security settings.

Make sure you have updated server software in your virtual machine
instances, see [Update
servers](#8.-update-servers)

If you are running specific variant of the linux-image that is slimmed
down by removing the less common kernel modules (such as Ubuntu), you
need to install Linux kernel extra modules for virtual machines.

    $ sudo apt-get install linux-image-extra-virtual

\*\*\* System restart required \*\*\*
 After you have installed the extra modules, reboot the instance before
running the Plaza playbook.

 Playbook fails with error "xyz.yml must be stored as a
dictionary/hash"
 Check that you have specified OS\_FLOATIP in xyx.yml correctly. Do you
have some lines commented out?

 Playbook is unable to access git and TASK: \[drupal | Get drupal\]
fails.
 Check your git access rights and make sure that Ansible ssh-agent
forwarding is configured correctly, see Step 1. Install Ansible

 Plaza playbook hangs in task \[heartbeat | restart heartbeat\]
 Restart heartbeat process in your Load Balancer server instance.

 Playbook fails with error "fatal: \[xyz\] =&gt; error while evaluating
conditional: not ansible\_devices.vdb.partitions"
 You have not attached block devices to this instance, attach a volume
to xyz instance and rerun.

 Playbook task \[ha-disk | Install the drbd module\] fails with error
"FATAL: Module drbd not found."
 If you are running specific variant of the linux-image that is slimmed
down by removing the less common kernel modules (such as Ubuntu), you
need to install Linux kernel extra modules for virtual machines.

    $ sudo apt-get install linux-image-extra-virtual
    $ sudo apt-get update && sudo apt-get -y upgrade

\*\*\* System restart required \*\*\*
 After you have installed the extra modules, reboot the instance before
re-running the Plaza playbook.

Ramping down cloud service
=========================================================================================

Terminating the virtual machine instances and deleting the storage
volumes are the two main tasks for the cloud service ramp down process.

Other issues that needs to be considered:
 - Is there any content in storage devices that needs to be backed up.
Does the normal volume backup procedure provide adequate backups, or do
you need to take backups before the server is ramped down.
 - Do service instances need to be backed up, e.g. are you planning to
transfer linux images to another service as such. For example, OpenStack
environments have a feature to take instance backups and import them to
other OpenStack environment, see [Take a snapshot of your Linux
instance](3_OpenStackIaaSplatform.md#take-a-snapshot-of-the-instance)
 - Some of the cloud platforms allows you to store information that also
needs to be removed, such as keypairs and security settings.

Steps
 Perform the following steps to backup and ramp down the cloud service.
 Note that some of the steps listed are not applicable to all cloud
platforms, as they do not have support for the listed features, such as
imported keypairs.
 If you are not planning to take volume or instance backups at this
point, you can jump to step 6.

### 1. Freeze instances in preparation for snapshotting

This allows all ongoing transactions in the file system to complete, new
write system calls are halted, and other calls that modify the file
system are halted.

### 2. Take virtual instance snapshots

Use cloud service management portal GUI or command line tools to take
snapshots.

### 3. Unfreeze (thaw) instances

After the snapshots are taken, you can unfreeze your instances back to
normal.

### 4. Take volume backups

Take backups from the storage volumes using the mechanism that is
supported by the instance OS.
 In OpenStack Linux environments youcan use either snapshots or tar
backups to take backups for your storage volumes.
 Some cloud environments also provide backups tools that you can use to
back up and recover data via cloud management portal.

### 5. Retrieve the instance and volume backups to your local machines/servers

Download the backups (snapshots) using command line tools or management
portal.
 If the cloud platform does not support direct snapshot downloading,
contact the cloud support.

### 6. Stop (terminate) instances

Log in to cloud management portal and terminate running instances. Make
sure all instances are stopped.

### 7. Detach the storage disk volumes

Use management portal to detach the volumes.

### 8. Delete storage disk volumes

Note that some of the cloud services can automatically delete volumes.
When an instance terminates in this type of cloud service, any instance
volumes associated with that instance are also deleted.

### 9. Delete virtual instances

Use cloud service management portal to delete the instances.

### 10. Remove network definitions

Remove all network related settings and IP address reservations.

### 11. Remove security groups

Remove all security group definitions, if the cloud service has security
groups.

### 12. Remove keypairs

If cloud service has enabled imported keypairs, remove keypairs.

### 13. Remove virtual datacenters

If cloud service has pools of cloud infrastructure resources, such as
virtual datacenters, remove those too.

### 14. Terminate your cloud account

If you are planning to terminate your cloud account, double-check that
the all the information you want to remove is deleted. Once your account
is closed, cloud management portal no longer accessible by you.

To close your account, contact cloud support to request that your
account should be closed.
