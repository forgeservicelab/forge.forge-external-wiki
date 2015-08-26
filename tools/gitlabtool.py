# dependencies: gitpython, pyapi-gitlab, PyGithub, docopt

"""
gitlabtool is able to view and manipulate projects in FORGE and Github services.
You can list projects, create projecs and copy projects between the services and
using both user namespace and organization namespace.

Usage:
  gitlabtool.py forge <forgeusername> <forgepassword> [<projectname>] [--list | --clone] [--branch=BRANCH]
  gitlabtool.py github <githubusername> <githubpassword> [--list | --organizations]
  gitlabtool.py github <githubusername> <githubpassword> <projectname> [<organization>] [--list | --create]
  gitlabtool.py copy <forgeusername> <forgepassword> <githubusername> <githubpassword> <projectname> [<organization>] [--toforge | --togithub]
  gitlabtool.py (-h | --help)

Options:
  -h, --help

"""

from docopt import docopt
import getopt
import gitlab
import sys
from git import Repo
from github import Github
import json
from pprint import pprint


def check_forge_user(arg):
    gitl = gitlab.Gitlab("git.forgeservicelab.fi")
    gitl.login(arg['<forgeusername>'], arg['<forgepassword>'])
    return gitl


def check_github_user(arg):
    gith = Github(arg['<githubusername>'], arg['<githubpassword>'])
    return gith


def main(arg):
    forge = {}
    github = {}
    if arg['forge']:
        gitl = check_forge_user(arg)
        a = gitl.getprojectsall(page=1, per_page=100)
        b = gitl.getprojectsall(page=2, per_page=100)
        projects = a + b
        if arg['--list'] and not arg['<projectname>']:
            print "List all Gitlab projects"
            print "--------------------"
            for project in projects:
                print project['path_with_namespace']
        if arg['--list'] and arg['<projectname>']:
            print "Print Gitlab project details"
            print "----------------------------"
            for project in projects:
                if project['path_with_namespace'] == arg['<projectname>']:
                    print project['path_with_namespace']
                    print "----------------------------"
                    for k,v in project.iteritems():
                        print "%s: %s" %(k,v)
        if arg['--clone'] and not arg['<projectname>']:
            print "Cloning all Gitlab repositories to local"
            print "----------------------------------------"
            for project in projects:
                err = False
                if arg['--branch']:
                    try:
                        Repo.clone_from(project['ssh_url_to_repo'], project['path_with_namespace'], branch=arg['--branch'])
                    except:
                        err = True
                else:
                    try:
                        Repo.clone_from(project['ssh_url_to_repo'], project['path_with_namespace'])
                    except:
                        err = True
                if err:
                    print "OMITTED %s" %(project['path_with_namespace'])
                else:
                    print project['path_with_namespace']
        if arg['--clone'] and arg['<projectname>']:
            print "Cloning Gitlab repository to local"
            print "----------------------------------"
            for project in projects:
                err = False
                if project['path_with_namespace'] == arg['<projectname>']:
                    if arg['--branch']:
                        try:
                            Repo.clone_from(project['ssh_url_to_repo'], project['path_with_namespace'], branch=arg['--branch'])
                        except:
                            err = True
                    else:
                        try:
                            Repo.clone_from(project['ssh_url_to_repo'], project['path_with_namespace'])
                        except:
                            err = True
                    if err:
                        print "OMITTED %s" %(project['path_with_namespace'])
                    else:
                        print project['path_with_namespace']
    if arg['github']:
        gith = check_github_user(arg)
        if arg['--list'] and not arg['<projectname>']:
            print "List Github projects"
            print "--------------------"
            repos = gith.get_user().get_repos()
            for repo in repos:
                print repo.full_name
        if arg['--list'] and arg['<projectname>']:
            repos = gith.get_user().get_repos()
            for repo in repos:
                if repo.full_name == arg['<projectname>']:
                    print "Print Github project details"
                    print "----------------------------"
                    print repo.full_name
                    print "----------------------------"
                    pprint (repo._rawData)
        if arg['--organizations']:
            print "List Github organizations"
            print "-------------------------"
            # for org in gith.get_user().get_orgs():
            #     print org.name
            orgs = gith.get_user().get_orgs()
            for org in orgs:
                print org.name
        if arg['--create'] and not arg['<organization>']:
            print "Create Github project"
            print "---------------------"
            print arg['<projectname>']
            gith.get_user().create_repo(arg['<projectname>'])
        if arg['--create'] and arg['<organization>']:
            orgs = gith.get_user().get_orgs()
            for org in orgs:
                if org.name == arg['<organization>']:
                    print "Create Github project"
                    print "---------------------"
                    print "%s/%s" %(org.name, arg['<projectname>'])
                    repo = org.create_repo(arg['<projectname>'])
    if arg['copy']:
        gitl = check_forge_user(arg)
        gith = check_github_user(arg)
        a = gitl.getprojectsall(page=1, per_page=100)
        b = gitl.getprojectsall(page=2, per_page=100)
        projects = a + b
        if arg['--toforge']:
            print "Copy project from Github to FORGE"
            print "---------------------------------"
            print "Not implemented"
        if arg['--togithub']:
            print "Copy project from FORGE to Github"
            print "---------------------------------"
            print "Not properly implemented yet"
            for project in projects:
                if project['path_with_namespace'] == arg['<projectname>']:
                    Repo.clone_from(project['ssh_url_to_repo'], project['path_with_namespace'])
                    if arg['<organization>']:
                        orgs = gith.get_user().get_orgs()
                        for org in orgs:
                            if org.name == arg['<organization>']:
                                print "%s/%s" %(org.name, project['name'])
                                repo = org.create_repo(arg['<projectname>'])
                    else:
                        print "%s" %(project['path_with_namespace'])
                        repo = gith.get_user().create_repo(arg['<projectname>'])


if __name__ == "__main__":
    arg = docopt(__doc__)
    main(arg)
