#!/usr/bin/env python

# pip install pyyaml argparse requests json typing
import yaml
import argparse
import os
import sys

from detail.artemis_api import *

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
                                   metavar='assignment',
                                   nargs=1,
                                   help='The assignment to be processed (e.g. w01h01)')
download_repos_parser.add_argument('-s',
                                   '--students',
                                   metavar='tumId',
                                   nargs='+',
                                   help='The students TUM ids to be processed (e.g. ge36feg ba12sup, ...)')

# getscores
get_scores_parser = sub_parsers.add_parser('getscores',
                                           help='Get scores for students\' assignments [not yet implemented]')
get_scores_parser.add_argument('-a',
                               '--assignment',
                               metavar='assignment',
                               nargs=1,
                               help='The assignment to be processed (e.g. w01h01)')
get_scores_parser.add_argument('-s',
                               '--students',
                               metavar='tumId',
                               nargs='+',
                               help='The students TUM ids to be processed (e.g. ge36feg ba12sup, ...)')

# newresult
# sytax:
# -a w01h01 -s ab43cde
# -score 80 -text "Gut gemacht "
#   -positive "Kommentare" "Gute Dokumentation"
#   -negative "Formatierung" "Bitte nutze Autoformat"
new_result_parser = sub_parsers.add_parser('newresult',
                                           help='Post a new result for a student\'s assignment [not yet implemented]')
new_result_parser.add_argument('-a',
                               '--assignment',
                               metavar='assignment',
                               required=True,
                               nargs=1,
                               help='The assignment to be processed (e.g. w01h01)')
new_result_parser.add_argument('-s',
                               '--student',
                               required=True,
                               metavar='tum_id',
                               nargs=1,
                               help='The students TUM id to be processed (e.g. ge36feg)')
new_result_parser.add_argument('-score',
                               metavar='score',
                               required=True,
                               type=int,
                               nargs=1,
                               help='The Score of the assignment (e.g. 80)')
new_result_parser.add_argument('-text',
                               required=True,
                               metavar='result_text',
                               nargs=1,
                               help='The Result Text of the assignment (e.g. "Gut gemacht")')
new_result_parser.add_argument('-pos',
                               '--positive',
                               metavar=('text', 'detail_text'),
                               nargs=2,
                               action='append',
                               help='A positive feedback consisting of Text and Detail Text '
                                    '(e.g. "Dokumentation" "Gute und präzise Kommentare")')
new_result_parser.add_argument('-neg',
                               '--negative',
                               metavar=('text', 'detail_text'),
                               nargs=2,
                               action='append',
                               help='A negative feedback consisting of Text and Detail Text '
                                    '(e.g."Formatierung" "Bitte Autoformatierung benutzen")')

# allows only one of the specified arguments
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

    positive_feedback_entries: List[Dict[str, str]] = []
    if args.positive is not None:
        for pos_feedback in args.positive:
            positive_feedback_entries.append(dict(text=pos_feedback[0], detail_text=pos_feedback[1]))
    negative_feedback_entries: List[Dict[str, str]] = []
    if args.negative is not None:
        for neg_feedback in args.negative:
            negative_feedback_entries.append(dict(text=neg_feedback[0], detail_text=neg_feedback[1]))

    new_result_body = NewResultBody(
        score=args.score[0],
        result_text=args.text[0],
        positive_feedback_entries=positive_feedback_entries,
        negative_feedback_entries=negative_feedback_entries
    )

    print('Chosen command: newresult not implemented yet but here\'s the data that would be sent to ArTEMiS:')

    api.post_new_result(new_result_body=new_result_body,
                        assignment=args.assignment[0],
                        student=args.student[0])
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
