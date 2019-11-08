#!/usr/bin/env python

# pip install pyyaml argparse requests json
import yaml
import argparse
import os

from detail.artemis_api import ArtemisAPI


parser = argparse.ArgumentParser(description='A command-line application for tutors to more productively grade programming excises on ArTEMiS')
# TODO: think of and parse arguments
parser.add_argument('command', help='The command for the script. Valid commands are "downloadrepos", "getscores", "newresult".')
parser.add_argument('-s', '--students', metavar='', nargs='+', help='The students TUM ids to be processed (e.g. ge36feg ba12sup, ...)')
parser.add_argument('-a', '--assignment', metavar='', nargs=1, help='The assignment to be processed (e.g. w01h01)')

group = parser.add_mutually_exclusive_group()
group.add_argument('-q', '--quiet', action='store_true', help='Print quiet')
group.add_argument('-v', '--verbose', action='store_true', help='Print verbose')

args = parser.parse_args()

with open('config.yml', 'r') as config_file:
    cfg = yaml.safe_load(config_file)

artemis = cfg['artemis']
api = ArtemisAPI(artemis)
bitbucket = cfg['bitbucket']['base_url']
course_name = artemis['course']['name']


def download_repos():
    students = args.students
    # students.extend(['exercise', 'solution', 'tests'])
    assignment = args.assignment[0]
    for student in students:
        # mkdir
        # cd (if not there raise 'Failed to create parent folder, check your permissions.'
        # da rein klonen

        # example repo: https://bitbucket.ase.in.tum.de/scm/PGDP1920W01P01/pgdp1920w01p01-ge36zuv.git
        print('Cloning repo of assigment %s for %s' % (assignment, student))

        course_assignment = course_name + assignment
        repo_remote = course_name + "-" + student
        os.mkdir(course_assignment)
        os.chdir(course_assignment)

        repo_url = os.path.join(bitbucket, 'scm', course_assignment, repo_remote + '.git')
        os.system(('git clone ' + repo_url))


if __name__ == '__main__':
    command_dispatch = {
        'downloadrepos': download_repos
    }

    command_dispatch[args.command]()

# TODO finish implementing API in detail/artemis_api.py
# TODO port backup/artemis-cli.sh to python
# TODO create symlink to tests repository for every student's submission to
#      make testing a lot easier
# TODO add feature to upload grades
# TODO create an eclipse/intellij project containing all student's submissions)
