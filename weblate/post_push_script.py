#! /usr/bin/env python

import os
import requests
import json
import re


giturl = os.environ.get('WL_REPO','git@git.dryrun.nl:doni/doni-portal.git')


private_token = 'XXVC9yjxvRpwdeHyV-pZ'
jenkins_private_token = 'Yx6G7iQUwPb2XZs5szkG'
branch = os.environ.get('WL_BRANCH','features/translations')
target_branch = 'development'
merge_title = 'Weblate translations'

headers = {'PRIVATE-TOKEN' : private_token}
jenkins_headers = {'PRIVATE-TOKEN' : jenkins_private_token}


gitre = re.compile('(?P<host>(git@|https://)([\w\.@]+)(/|:))(?P<owner>[\w,\-,\_]+)/(?P<repo>[\w,\-,\_]+)(.git){0,1}((/){0,1})')
url = gitre.match(giturl)
host = url.group(3) #'git.dryrun.nl'
group_name = url.group(5)
project_name = url.group(6)

print "Searching for project {0} on {1}".format(project_name,host)

r = requests.get("http://{0}/api/v3/projects/search/{1}".format(host,project_name), headers=headers)
project_id = r.json()[0]['id']

print "Searching for group {0} on {1}".format(group_name,host)
r = requests.get("http://{0}/api/v3/groups?search={1}".format(host,group_name), headers=jenkins_headers)

group_id = r.json()[0]['id']
print "Found group with id:{0}".format(group_id)

membersRequest = requests.get("http://{0}/api/v3/projects/{1}/members/".format(host,project_id), headers=headers)
projectMembers = membersRequest.json()

membersRequest = requests.get("http://{0}/api/v3/groups/{1}/members/".format(host,group_id), headers=headers)
groupMembers = membersRequest.json()
print groupMembers

projectMembers = sorted(projectMembers, key=lambda k: k['access_level'])
groupMembers = sorted(groupMembers, key=lambda k: k['access_level'])

print groupMembers

def master_access(member):
    return member['access_level'] == 40

projectMasters = filter(master_access, projectMembers)
groupMasters = filter(master_access, groupMembers)

assignee = None

if len(projectMasters):
    assignee = projectMasters[0]
elif len(groupMasters):
    assignee = groupMasters[0]

payload = {'source_branch': branch, 'target_branch': target_branch, 'title': merge_title, 'assignee_id': assignee['id']}


print "Create merge request for local branch {0} -> remote branch {1}, assigned to {2}".format(branch,target_branch, assignee['name'])

mr = requests.post("http://{0}/api/v3/projects/{1}/merge_requests/".format(host,project_id), data=payload, headers=headers)

print mr.text