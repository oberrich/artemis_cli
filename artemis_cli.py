#!/usr/bin/env python

# pip install pyyaml argparse requests json
import yaml
import argparse
import os
import sys

from detail.artemis_api import ArtemisAPI

parser = argparse.ArgumentParser(
    description='A command-line application for tutors to more productively grade programming excises on ArTEMiS')

valid_commands = {
    'downloadrepos',
    'getscores',
    'newresult'
}

sub_parsers = parser.add_subparsers(title='sub-commands',
                                    dest='command',
                                    description='Valid sub-commands',
                                    help='Additional help')

# downloadrepos
download_repos_parser = sub_parsers.add_parser('downloadrepos',
                                               help='Download student exercise repositories')
download_repos_parser.add_argument('-a',
                                   '--assignment',
                                   metavar='',
                                   nargs=1,
                                   help='The assignment to be processed (e.g. w01h01)')
download_repos_parser.add_argument('-s',
                                   '--students',
                                   metavar='tumId',
                                   nargs='+',
                                   help='The students TUM ids to be processed (e.g. ge36feg ba12sup, ...)')

# TODO getscores
get_scores_parser = sub_parsers.add_parser('getscores',
                                           help='Get scores for students\' assignments [not yet implemented]')
get_scores_parser.add_argument('-a',
                               '--assignment',
                               metavar='',
                               nargs=1,
                               help='The assignment to be processed (e.g. w01h01)')
get_scores_parser.add_argument('-s',
                               '--students',
                               metavar='tumId',
                               nargs='+',
                               help='The students TUM ids to be processed (e.g. ge36feg ba12sup, ...)')

# TODO newresult
new_result_parser = sub_parsers.add_parser('newresult',
                                           help='Post a new result for a student\'s assignment [not yet implemented]')
new_result_parser.add_argument('-a',
                               '--assignment',
                               metavar='',
                               nargs=1,
                               help='The assignment to be processed (e.g. w01h01)')
new_result_parser.add_argument('-s',
                               '--student',
                               metavar='tumId',
                               nargs=1,
                               help='The students TUM id to be processed (e.g. ge36feg)')

# allows only one argument
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


def download_repos(quiet=False, verbose=False):
    print('Fetching student assignments')
    students = args.students
    students.extend(['exercise', 'solution', 'tests'])
    assignment = args.assignment[0]  # is a list

    for student in students:

        # example repo url: https://bitbucket.ase.in.tum.de/scm/PGDP1920W01P01/pgdp1920w01p01-ab42cde.git
        print('Fetching assigment %s for %s...' % (assignment, student))

        course_assignment = course_name + assignment
        remote_repo = course_name + '-' + student + '.git'

        local_repo = os.path.join('..', course_assignment + '-' + student)

        if not os.path.exists(local_repo):
            os.mkdir(local_repo)
        os.chdir(local_repo)

        repo_url = os.path.join(bitbucket, 'scm', course_assignment, remote_repo)
        clone_cmd = 'git clone ' + repo_url
        print(clone_cmd)
        os.system(clone_cmd)
        # TODO: no access to repo ('The requested repository does not exist, or you do
        #  not have permission to access it.')


def get_scores(quiet=False, verbose=False):
    print('Chosen command: getscores not implemented yet.')
    sys.exit(1)


def new_result(quiet=False, verbose=False):
    print('Chosen command: newresult not implemented yet.')
    sys.exit(1)


# MAIN
command_dispatch = {
    'downloadrepos': download_repos,
    'getscores': get_scores,
    'newresult': new_result,
}

command_dispatch[args.command](quiet=args.quiet, verbose=args.verbose)


# TODO finish implementing API in detail/artemis_api.py
# TODO port backup/artemis-cli.sh to python
# TODO create symlink to tests repository for every student's submission to
#      make testing a lot easier
# TODO add feature to upload grades
# TODO create an eclipse/intellij project containing all student's submissions)
