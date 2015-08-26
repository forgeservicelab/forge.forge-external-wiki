![](/files/book.png)

User guides
==========================================

-------------------------------------------------------------------------------

GitLab
=============================

GitLab is a code hosting service similar to [GitHub](http://github.com).

This document assumes Gitlab service is installed and available at <https://git.forgeservicelab.fi>

Projects
---------------------------------

Project in GitLab is a repository plus issue tracker and wiki. Use only
the repository, we have other means for wiki and issue tracking.

Documentation
-------------------------------------------

There is not much user-facing documentation available. The interface is
quite intuitive though and it's very GitHub like.

Nice Git overview: <http://rogerdudler.github.io/git-guide/>

If you wonder how to clone and push repository, you should visit the
page of the project:
git.forgeservicelab.fi/&lt;your\_LDAP\_username&gt;/&lt;project\_name&gt;

To see all available public projects, visit
<https://git.forgeservicelab.fi/public>

### Group membership

At the moment, gitlab does not reflect your group membership from FORGE
LDAP. That means that you have to explicitly add users to your
repository if you want to collaborate. User must first log in with his
FORGE LDAP credentials before you can see him in gitlab and add him as a
collaborator.

Walkthroughs
-----------------------------------------

### Log in to the web interface

In the web interface (<https://git.forgeservicelab.fi>) you must, for
the first time, login with your FORGE credentials via "LDAP Sing in".
After that, whenever you want to login, you can use the Single Sign-on
session by just clicking the "Cas" button.

### Set up your git identity

    git config --global user.name "John Doe"
    git config --global user.email johndoe@example.com

### Try if it works

    git clone https://git.forgeservicelab.fi/testgroup/test-repo.git

### Create a repository

-   Log in to gitlab and click the "New project" icon in the upper right
    part of the user interface.
-   Pick a name, select namespace (your namespace or one of your groups)
    and other features of the new repository
-   Click "Create project" in green.
-   You see instructions how to add files or import a repository.

### Clone a repository

-   you can fetch (clone) over HTTPS or SSH (port 10022)
-   go to the repository home view. For example
    <https://git.forgeservicelab.fi/testgroup/test-repo>
-   in the upper part of the view you can see the repository url.

If you clone a private repo over HTTPS, you should specify your username
in the URL. Git should ask you for password then. For example:

` git clone https://myusername@git.forgeservicelab.fi/forge/private_repo.git`

### SSH Access

With Git you can use SSH as a transport protocol, as an alternative to
HTTPS. SSH daemon for Gitlab is running on port 10022. In order to
access repositories over SSH, you need to upload a public key to your
account in Gitlab. You can't clone anonymously over SSH.

-   Visit <https://git.forgeservicelab.fi/profile/keys> and follow
    instructions how to generate and upload a key.
-   If you already have a private key in PEM format (perhaps from
    OpenStack Horizon) which you want to reuse, you can get the public
    key based on the private key as:

<!-- -->

    ssh-keygen -y -f /home/youruser/keys/private.pem

And then you can copy-paste the public key to
<https://git.forgeservicelab.fi/profile/keys/new>.

Then, you can set up your OpenSSH client. Gitlab is using a single
service account for SSH access. It adds the public keys of all the users
to one authorized\_keys file of the "gitlab" account. Therefore, you
need to instruct your SSH client to use particular credentials for
connections to git.forgeservicelab.fi:10022. If you are using
openssh-client, you can do this by creating following entry in
.ssh/config in your home directory:

    Host git.forgeservicelab.fi
        HostName git.forgeservicelab.fi
        User gitlab
        Port 10022
        IdentityFile /path/to/your/privatekey.pem

You can test if it works by cloning the testing repo over SSH:

    git clone ssh://gitlab@git.forgeservicelab.fi:10022/testgroup/test-repo.git

FAQ
-----------------------

### I am getting `fatal: HTTP request failed`

Your Git is old. You should have at least Git 1.8. If you are using RHEL
or CentOS, you can install recent Git from the IUS Community Project
site:

    mkdir delme
    cd delme
    wget http://dl.iuscommunity.org/pub/ius/stable/Redhat/6/x86_64/git18-1.8.4-1.ius.el6.x86_64.rpm
    wget http://dl.iuscommunity.org/pub/ius/stable/Redhat/6/x86_64/perl-Git18-1.8.4-1.ius.el6.noarch.rpm
    yum install *rpm

### I try to push over HTTPS with valid credentials and it gives me "Invalid credentials" error.

This is an issue given by aggregating CAS and LDAP login in GitLab. It's
easy to resolve - just go to GitLab web, log out, and log in there with
LDAP credentials.

------------------------------------------------------------------------

XMPP
=======================

Openfire is an instant messaging (IM) and groupchat server that uses XMPP.
There can be public and private conference rooms available.

This document assumes Openfire service is installed and available at xmpp.forgeservicelab.fi

In order to use the service the user has to install a client - any of
<https://xmpp.org/xmpp-software/clients/>. One of the most common
clients is [Pidgin](http://www.pidgin.im).

------------------------------------------------------------------------


Redmine
=======================================================

Redmine is a flexible project management web application. Written using
the Ruby on Rails framework, it is cross-platform and cross-database.
Redmine is open source and released under the terms of the GNU General
Public License v2 (GPL).

Redmine has the capability of
being a full featured ticketing system which teams e.g. helpdesk can utilize.
Redmine can be used to manage development projects' backlogs and sprints too.
FORGE Service Lab is using Redmine both to operate FORGE Service Lab and
to manage its own agile development projects. 

 More information about Redmine is in
<http://www.redmine.org/projects/redmine/wiki/Guide>

This document assumes Redmine service is available at <https://support.forgeservicelab.fi>
and is is configured to provide tools for project management, documents, forums and news.

When you log in to <https://support.forgeservicelab.fi> then depending
on your role you may access one or more projects.

Features
---------------------------------------------------------

Some of the Redmine features that are enabled by default are:

-   Multiple projects support
-   Flexible role based access control
-   Flexible issue tracking system
-   News, documents & files management
-   Feeds & email notifications
-   Per project wiki
-   Per project forums
-   Backlogs

Get Redmine
---------------------------------------------------------------

Development projects which are using FORGE Service Lab will have an
opportunity to utilize hosted Redmine service. The main technical contact
of the development project may request a template project to be set up
for the project and he then becomes the admin for the project.

In case development projects rather want to have the Redmine service of
their own, then they can reuse the Ansible playbook created by FORGE
Service Lab in order to setup a Redmine instance of their own.

Project admin role
-------------------------------------------------------------------------------------

Project admin is the main contact in Redmine project. FORGE Service Lab has
also used the term "technical contact" which is legally binding role. Project
admin instead has full access to his Redmine project and is able to configure
the project and add/remove new project members and grant them different roles
and access rights.

Roles
---------------------------------------------------

When Project admin adds new members to his project he has to define
which role each member plays in the project.

-   **Project admin** role provides edit access to project settings and
    capability to add sub projects and members to the project. This role
    is suitable for scrum masters and product owners who have to edit
    releases and sprints in addition to managing product backlogs
-   **Team member** role provides edit access to issues and
    product backlogs. This role can be used to provide access for
    project members, developers, product owners and scrum masters who
    manage product backlogs and resolve issues
-   **Stakeholder** role provides edit access to issues. This role can
    be used to provide project external (temporary) stakeholders edit
    access to the projects issues. Stakeholder can also create new
    issues but can not edit backlogs so it's not suitable for scrum
    masters nor product owners.
-   **QA** role is similar to Team member role and provides edit access
    to issues and product backlogs.
-   **Watcher** role provides read and commenting access to all
    project's issues. This role can be used to provide an external party
    read only access to all project issues so that they can comment on
    the issues but not update them.

Note! If you want to provide a project external stakeholder a view
access to a specific issue only (instead of all project issues) and to
provide him a notification about the issue updates, then you can set the
project external stakeholder as a watcher for the issue (not watcher
role). The project external stakeholder will then be able to see the
specific issue when he selects "issues" tab and he won't be able to see
other issues. This feature is well suited to allow a customer to follow
up the development of a particular issue he might have initiated.

Managing projects
---------------------------------------------------------------------------

FORGE's Redmine uses Redminebacklogs in order to enable scrum projects
to be managed and it provides backlogs, releases, sprints, issues,
statistics and many more features. There is a good document about how to
manage projects with Redminebacklogs.

See the document from <http://www.redminebacklogs.net/>

------------------------------------------------------------------------

Setting up Continuous Integration with Jenkins
======================================================================================================================

The following reference is extracted and updated from
[Stouts.jenkins](https://github.com/Stouts/Stouts.jenkins) on github,
from which [FORGE's Jenkins
role](https://git.forgeservicelab.fi/ansible-roles/jenkins/tree/master)
is a fork.\
 It should provide the guidelines to set up a Jenkins instance with
Ansible.

Stouts.jenkins
-----------------------------------------------------

[![Build
Status](https://travis-ci.org/Stouts/Stouts.jenkins.png)](https://travis-ci.org/Stouts/Stouts.jenkins)

Ansible role which manage [Jenkins CI](http://jenkins-ci.org/)

-   Install and configure Jenkins
-   Proxy jenkins with nginx
-   Setup SSH credentials for Jenkins (key, known\_hosts)
-   Install Jenkins plugins
-   Manage Jenkins jobs
-   Create jobs
-   Restore backed up configurations

### Variables

Here is the list of all variables and their default values:

    jenkins_enabled: yes                        # The role is enabled
    jenkins_name: jenkins
    jenkins_user: jenkins
    jenkins_group: jenkins
    jenkins_http_port: 8000                     # Set jenkins port
    jenkins_ssh_key_file: ""                    # Set private ssh key for Jenkins user
    jenkins_ssh_known_hosts: []                 # Set known hosts for ssh
    jenkins_nginx_proxy: no                     # Enable nginx proxy
    jenkins_nginx_hostname: ""                  # Set jenkins host
    jenkins_apt_packages: []                    # Ensure the packages installed
    jenkins_plugins: []                         # Ensure the plugins is installed
    jenkins_jobs: []                            # Simple manage Jenkins jobs
                                                # Ex. jenkins_jobs:
                                                #       - name: job
                                                #         action: enable  # (enable|disable|delete|create)
                                                #       - name: test
                                                #         action: disable
    jenkins_configuration: /etc/default/jenkins
    jenkins_configurations: (undefined)                    #Tarball with a JENKINS_HOME directory tree containing `config.xml` files.
                                                                                        # This typically comes from a jenkins backup.
    jenkins_home: /var/lib/jenkins
    jenkins_java: /usr/bin/java
    jenkins_logdir: /var/log/jenkins
    jenkins_log: "{{jenkins}logdir}}/{{jenkins_name}}.log"
    jenkins_pidfile: /var/run/jenkins.pid
    jenkins_prefix: "/"
    jenkins_run_standalone: yes
    jenkins_war: /usr/share/jenkins/jenkins.war

### Usage

Add `jenkins` to your roles and setup the variables in your playbook
file.

 Example:

    - hosts: all

      roles:
        - role: jenkins
          jenkins_nginx_proxy: yes
          jenkins_nginx_hostname: jenkins.myhost.com
          jenkins_ssh_key_file: "{{resources_to}}/resources/jenkins/ssh_key" 
          jenkins_ssh_known_hosts:
            - bitbucket.org
            - github.com
          jenkins_jobs:
            - name: test
              action: delete
            - name: newjob
              action: create
              config: job-config.xml

Jenkins Pipeline
----------------------------------------------------------

FORGE Service Lab recommends the following jenkins pipeline for project
management. It makes extensive use of Ansible:

-   Main project job. Tracks the project's source code, triggers
    deployment to testing.
-   Deployment to testing job. Tracks deployment playbook, triggers
    automatic testing.
-   Automatic testing job. Tracks automated tests, prompts
    build promotion.
-   Deployment to production job. Tracks deployment playbook, does not
    build automatically, triggers automatic testing.
-   Automatic testing job for production. End of the pipeline, ensures
    proper production deployment.

Depending on the type of project, particularly on maven/java projects,
most of the pipeline can be compressed in a single jenkins job. This
pipeline is still recommended due to its ability to accommodate all
sorts of free form projects.

### Main project job

This job will track the project's source code (deployable repositories
or similar). The job's task is to track the project development tree,
build if necessary and trigger the deployment job. It is also possible
to run static tests on this job (e.g. checkstyle). It is the starting
point in the management pipeline.

### Deployment to testing job

This job will track the playbook to deploy the project to the testing
environment. It is triggered either by the Main project job or by
changes to the playbook and it ensures that the project is deployed to
testing environment always on the latest working revision with the
latest deployment procedures. The job will trigger automatic testing
after deployment, it is the task of this job to revert the testing
environment to the last known working revision if automatic testing
fails.

### Automatic testing job

This job will run automated testing suites against the testing
environment, ensuring that the latest deployed revision works as
expected. A successful build on this job will propagate upwards to the
beginning of the pipeline and is the starting point for Q&A verification
and promotion of the project's revision. The job is triggered by either
the deployment to testing job or by changes to the tests suite. This
ensures that the project is tested always with the latest revision of
the tests.

### Deployment to production job

This job will always be manually triggered. It tracks the deployment to
production playbook which, if properly parameterized, can be the same as
the deployment to testing playbook. A highly recommended prerequisite
for this job is that it be parameterized with a promoted build from the
Main project job, which will ensure that only verified builds are
deployed to production. It triggers the automated testing job for
production.

### Automatic testing job for production

This is the end of the pipeline. The job is triggered by builds of
deployment to production and runs a set of automated test suites against
production. It is very similar to the automatic testing job for the
testing environment and given proper parameterization it can be the same
job. It ensures that the deployment to production has gone according to
plan.

Using hooks
------------------------------------------------

Jenkins offers several options to regularly poll version control systems
for changes in the sources tracked by its jobs. However jenkin's GIT
plugin allows git's hook system to trigger a build as soon as changes
are made to the repository. By configuring git hooks on the source repo
and setting the polling frequency sparse enough (FORGE Service Lab polls
yearly) we can substantially reduce wait times and ensure that each job
in the pipeline is built as soon as changes to the source are published.

------------------------------------------------------------------------

Backup best practices
==========================================================================

There is a sizable amount of backup practices and guidelines, we at
FORGE Service Lab recommend the following process:

-   Separate the service's components
-   Separate the backup server from the backed up services
-   Keep a daily copy of the backed up data
-   Set up a secondary warehousing
-   Automate the provisioning of the services

Following are the detailed guidelines for each of these steps.

Separate the service's components
---------------------------------------------------------------------------------------------------

This item boils down to minimizing Single Points of Failure (SPOFs) so
we'd be looking at separating the service's components into as many
nodes as possible or, to put it another way, build a service cluster
where each node has one and only one task. Typically this will mean
having the web application on one node and the database in another,
lightweight components such as reverse proxies could be bundled with
related services as application servers if their usage load doesn't
warrant a new node.

In systems where the database is tightly coupled to the application this
does not remove a SPOF but it does make the system easier to diagnose
and restore, the more components on a node the more difficult it becomes
to maintain and to spot internal dependencies.

Separate the backup server from the backed up services
--------------------------------------------------------------------------------------------------------------------------------------------

This might seem obvious but keeping the service backups in the same
location as the backup sources is a recipe for disaster as they'll
become unavailable in case of a catastrophic event.\
 There is an extra upside to this separation and it is that the back up
server can encompass the backup procedures for a variety of possibly
unrelated services so that the backups are not spread across the entire
infrastructure. This of course incurs in the risk of introducing a SPOF
for the backups themselves, which is why it's necessary to set up a
[secondary warehousing](#set-up-secondary-warehousing).

Keep a daily copy of the backed up data
--------------------------------------------------------------------------------------------------------------

It is not enough to keep a live stream copy of the backup sources but
also a daily copy or snapshot of that data. This process works on the
assumption that a snapshot of the streaming copy taken at odd hours will
contain a valid representation of the day's data.

### Streaming copy

This process is best represented by database backup strategies, in this
scenario we'd be looking at a database replication slave or a hot
standby or even a hidden secondary replica, depending on the engine and
its jargon but it's basically always the same, another database server
that holds a live copy of the production data but is not used by the
application so that it can be stopped without adverse effects.

The same process can be replicated for filesystem backups. Instead of
taking snapshots of the production filesystem what we'll do is keep a
*fairly* updated copy of the source files on the backup service, this
can be easily accomplished by running rsync at regular intervals via
cron jobs. Typically hourly syncs are enough.

### Daily snapshots

With the streaming copy procedures in place, the backup server has a
local copy of the production sources which can be manipulated without
affecting the production environment. We'll be taking a snapshot of
these on at least a daily basis. For database servers we'd want to stop
or pause the replication process on the local server and take a database
dump and save it as a compressed file. The specifics of this will depend
on the database server itself. For the synced filesystem we'll want to
create a tarball of the synced directories, the granularity of which
will depend on the data synced, its services' sources and the
manageability when restoring.

 All of this will be typically handled via cron jobs.

Set up secondary warehousing
----------------------------------------------------------------------------------------

As stated
[above](#separate-the-backup-server-from-the-backed-up-services), the
separation of the backup server could introduce a SPOF on backup
recovery. Secondary warehousing involves the setup of one or more nodes
that will keep a copy of the backed up data. Note that it is not
necessary (though it could be beneficial) to replicate the entire backup
strategy from the backup server onto the secondary warehouses but
instead it is sufficient that these warehouses pull a copy of the daily
snapshots from the database server.

 So in short, these nodes are not backups but rather backups of a
backup.

Automate the provisioning of the services
------------------------------------------------------------------------------------------------------------------

This is the key that makes the effort worthwhile. By using automatic
provisioning tools (FORGE Service Lab recommends and supports Ansible)
any nodes on the service can be easily restored in case of a
catastrophic event. With carefully constructed playbooks or provisioning
recipes we can restore entire service clusters within minutes and
combining this with restoration of backed up data the impact of a
catastrophic event is minimal.

 As an added bonus, sticking by this procedure makes the service nodes
expendable. Since it is so easy to restore a lost node, nothing keeps us
from destroying and replacing a node in case of any less catastrophic
situation. The node no longer needs to be dead and buried before
replacement or restoration but it can be replaced if it becomes
compromised or overloaded or even if it just starts under performing for
no apparent reason.

------------------------------------------------------------------------

Host certificates
==============================================================

Why host certificate
--------------------------------------------------------------------

If you want to create a credible web service that supports https, then
you need signed host certificate installed into your web server. Trusted
certificates are signed by the trusted certificate authority (CA),
otherwise if the CA is not trusted by the web browser then the web
browser throws a warning message to the user "This site is not
trusted...do you still want to continue" or other similar kind of
warning message.

Certificate signing request
----------------------------------------------------------------------------------

Certificate signing request is used when you ask your trusted CA to sign
your certificate. You can sign your certificate by yourself but then the
certificate becomes so called "self signed" certificate and end users
web browsers will still throw the warning message.

There are instructions in internet about how to create a certificate and
signing request. E.g.

<http://www.rackspace.com/knowledge_center/article/generate-a-csr-with-openssl>

Who could sign my certificate
--------------------------------------------------------------------------------------

There are many options to get your certificate signed by the trusted
certificate authority. Usually signing is provided by commercial vendors
as a service and requires a transaction fee depending on the vendor. It
is up to you to make the decision which CA you want to use.

Manufacturers of web browsers (Microsoft, Google and Mozilla) have
announced deprecation of certificates using SHA-1 hash in 2017.
Therefore it's recommended to use SHA-2 certificates instead. Web sites,
which are protected with SHA-1 certificates, may cause a warning to be
displayed in the browser. SHA-1 algorithm is not compromised, but it is
becoming too weak for high-security applications.

It is a good idea to select the certificate authority that is already
trusted by web browsers and is able to provide SHA-2 certificates. It's
a common practice (not guaranteed though) that web browsers trust the
same CA than Mozilla and therefore you might want to select your CA from
this list
<http://www.mozilla.org/en-US/about/governance/policies/security-group/certs/included/>
. If you are designing your web application for a specific browser, then
you might want to test your browser first if it trusts the CA you are
planning to use.
