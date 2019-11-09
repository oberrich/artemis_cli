#!/usr/bin/env python

# pip install pyyaml argparse requests json typing
import yaml
import os
import sys
import re

from detail.artemis_api import ArtemisAPI
from detail.arg_parser import ArgParser

from detail.artemis_api_payloads import NewResultBody

def generate_gradebook(students):
    pass # TODO

def command_repos(quiet=False, verbose=False):
    # TODO check for this in other commands
    assignment = args.assignment

    if course_name == "pgdp1920" and not re.match("^w[0-9][0-9]?[hp][0-9][0-9]?$", assignment):
        raise RuntimeError('Assignment name doesn\'t match the shortName convention of PGdP course')

    students = args.students
    # remove whitespaces, commas and duplicates
    students = list(set(filter(lambda s: s, [s.replace(' ', '').replace(',', '') for s in students])))

    num_students = len(students)

    if num_students == 0:
        raise RuntimeError('No valid student name in args.students')

    students.extend(['exercise', 'solution', 'tests'])

    print('Fetching %s assignment %s for student%s...' % (course_name, assignment, '' if num_students == 1 else 's'))

    for student in students:
        print('Fetching assigment for %s...' % student)


        pass
        """
        # TODO unflatten project structure, add option to flatten it
        # TODO add option to customize path to root folder

        # example repo url: https://bitbucket.ase.in.tum.de/scm/PGDP1920W01P01/pgdp1920w01p01-ab42cde.git
        print('Fetching assigment for %s...' % student)


        course_assignment = course_name + assignment
        remote_repo = course_name + '-' + student + '.git'

        local_repo = os.path.join('..', course_assignment + '-' + student)

        if not os.path.exists(local_repo):
            os.mkdir(local_repo)

        os.chdir(local_repo)

        # TODO: After resetting repository for a student make sure to

        repo_url = os.path.join(bitbucket, 'scm', course_assignment, remote_repo)
        clone_cmd = 'git clone ' + repo_url
        print(clone_cmd)
        os.system(clone_cmd)
        # TODO: no access to repo ('The requested repository does not exist, or you do
        #  not have permission to access it.')
        """

def command_get_scores(quiet=False, verbose=False):
    print('Chosen command: getscores not implemented yet.')
    sys.exit(1)

def command_new_result(quiet=False, verbose=False):
    # TODO feedback not required

    positive_feedback_entries = [] # type: List[Dict[str, str]]
    if args.positive is not None:
        for pos_feedback in args.positive:
            positive_feedback_entries.append(dict(text=pos_feedback[0], detail_text=pos_feedback[1]))
    negative_feedback_entries = [] # type: List[Dict[str, str]]
    if args.negative is not None:
        for neg_feedback in args.negative:
            negative_feedback_entries.append(dict(text=neg_feedback[0], detail_text=neg_feedback[1]))

    new_result_body = NewResultBody(
        score=args.score,
        result_text=args.text,
        positive_feedback_entries=positive_feedback_entries,
        negative_feedback_entries=negative_feedback_entries
    )

    print('Chosen command: newresult not implemented yet but here\'s the data that would be sent to ArTEMiS:')

    api.post_new_result(new_result_body=new_result_body,
                        assignment=args.assignment,
                        student=args.student)
    sys.exit(1)


def main():
    global parser, args, api, bitbucket, course_name, course_id

    # parse arguments
    parser = ArgParser()
    args = parser.parse_args()

    # load config
    with open('config.yml', 'r') as config_file:
        cfg = yaml.safe_load(config_file)

    # alias commonly used config fields
    artemis     = cfg['artemis']
    bitbucket   = cfg['bitbucket']['base_url']
    course_name = artemis['course']['name']
    course_id   = artemis['course']['id']

    # instantiate the artemis api client
    api = ArtemisAPI(artemis)

    # dispatch command
    dispatch = {
        'repos': command_repos,
        'getscores': command_get_scores,
        'newresult': command_new_result
    }

    dispatch[args.command](quiet=args.quiet, verbose=args.verbose)

if __name__=="__main__":
    main()

# TODO finish implementing API in detail/artemis_api.py
# TODO port backup/artemis-cli.sh to python
# TODO create symlink to tests repository for every student's submission to
#      make testing a lot easier
# TODO add feature to upload grades
# TODO create an eclipse/intellij project containing all student's submissions)
