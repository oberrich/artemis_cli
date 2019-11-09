#!/usr/bin/env python

# pip install pyyaml argparse requests json typing
import yaml
import os
import sys
import re
import subprocess

from functools import partial

from detail.artemis_api import ArtemisAPI
from detail.arg_parser import ArgParser


def run_git(params, cwd=None):
    params = ['git'] + params

    p = subprocess.Popen(params, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()

    if args.verbose and out:
        print('Output of git ' + params[1] + ':')
        print('  ' + out)

    return p.returncode, out


def generate_gradebook(students):
    pass  # TODO


def command_repos():
    # TODO apply sanitization in main function
    assignment = args.assignment
    deadline = api.get_deadline(args.exercise)

    num_students = len(students)

    script_dir = os.path.dirname(os.path.realpath(__file__))

    print('Fetching %s-%s@{%s} for %d student%s.\n' % (course_name, assignment, str(deadline),
                                                       num_students, '' if num_students == 1 else 's'))

    special_repos = ['exercise', 'solution', 'tests']

    num_succeeded = 0

    for student in special_repos + students:
        sys.stdout.write('Fetching assigment for %s... ' % student)
        sys.stdout.flush()

        repo_name = "%s%s-%s" % (course_name, assignment, student)
        repo_url = os.path.join(bitbucket, 'scm', course_name + assignment, repo_name + '.git')

        # TODO create a folder structure unless flatten option in config is set
        repo_dir = os.path.join(script_dir, repo_name)

        if os.path.exists(repo_dir):
            if not os.path.isdir(repo_dir):
                print(
                    'failed! Directory where student\'s repository is supposed to be clone into cannot be '
                    'created because a non-directory file with the same name already exists.')
                continue
            elif not os.listdir(repo_dir):
                os.rmdir(repo_dir)

        if os.path.exists(repo_dir):
            # directory for repo already exists
            if not os.path.exists(os.path.join(repo_dir, '.git')):
                print('failed! Directory for student\'s repository already existed but was not a git repository.')
                continue

            run_git(['checkout', 'master'], cwd=repo_dir)

            status, _ = run_git(['pull'], cwd=repo_dir)
            if status != 0:
                print('failed! `git pull` returned %d.' % status)
                continue
        else:
            os.mkdir(repo_dir)

            status, _ = run_git(['clone', repo_url, repo_dir], cwd=repo_dir)
            if status != 0:
                os.rmdir(repo_dir)
                print('failed! `git clone` returned %d.' % status)
                continue

        if not any(student in s for s in ['exercise', 'solution', 'tests']) and deadline is not None:
            _, rev = run_git(['rev-list', '-1', '--before="%s"' % deadline, 'master'], cwd=repo_dir)
            run_git(['checkout', '`%s`' % rev], cwd=repo_dir)

        run_git(['remote', 'set-url', '--push', 'origin', 'forbidden'], cwd=repo_dir)

        num_succeeded += 1
        print("ok!")

    num_repos = len(students) + len(special_repos)
    print('\nManaged to successfully fetch %d/%d (%.0f%%) repositories.' % (
        num_succeeded, num_repos, num_succeeded / float(num_repos) * 100.))


def command_get_scores():
    print('Chosen command: getscores not implemented yet.')
    sys.exit(1)


def command_new_result():
    # TODO change so we can reuse it for submitting all student's scores
    if args.score not in range(0, 101):
        raise RuntimeError('score has to be within [0;100]')

    # assign empty list if is None
    args.positive = [] if args.positive is None else args.positive
    args.negative = [] if args.negative is None else args.negative

    # ensures all feedbacks have at most one description
    any_invalid = lambda fs: any((len(f) != 1 and len(f) != 2) or not f[0] for f in fs)

    if any_invalid(args.positive) or any_invalid(args.negative):
        raise RuntimeError('Text for feedback is required (detail_text is optional, no extra arguments allowed)')

    # map arguments to a well-formed dictionary
    dict_mapper = lambda f, positive: {
        'text': f[0],
        'detailText': '' if len(f) == 1 else f[1],
        'positive': positive
    }

    feedbacks = list(map(partial(dict_mapper, positive=True), args.positive))
    # and combine positive and negative feedbacks
    feedbacks.extend([x for x in list(map(partial(dict_mapper, positive=False), args.negative))])

    print('Fetching results for all students, this may take a few seconds...')
    results = api.get_results(api.get_exercise_id(args.exercise))

    participations = api.get_participations(results, args.students)
    if not participations:
        raise RuntimeError('No participations for any of the students')

    # TODO ensure args.text != ''

    print('Submitting feedback for student ' + args.students[0])
    api.post_new_result(participations[0]['id'], args.score, args.text, feedbacks)
    print('Done!')

    sys.exit(1)


def main():
    global parser, args, api, bitbucket, course_name, course_id

    # disable stdout if --quiet

    # parse arguments
    parser = ArgParser()
    args = parser.parse_args()

    # load config
    with open('config.yml', 'r') as config_file:
        cfg = yaml.safe_load(config_file)

    # alias commonly used config fields
    artemis = cfg['artemis']
    bitbucket = cfg['bitbucket']['base_url']
    course_name = artemis['course']['name']
    course_id = artemis['course']['id']

    # instantiate the artemis api client
    api = ArtemisAPI(artemis)

    # verify course name against patterns
    if course_name == "pgdp1920":
        regex = "^w[0-9][0-9]%s[hp][0-9][0-9]%s$"

        if not re.match(regex % ('?', '?'), args.assignment):
            raise RuntimeError('Assignment name doesn\'t match the shortName convention of PGdP course')

        if not re.match(regex % ('', ''), args.assignment):
            print('Warning: Usually shortNames for exercises follow the convention "w01h01",'
                  ' you can find the correct shortName on ArTEMiS if pulling the repos fails')

    # get exercise data from artemis, raise if it doesn't exist
    args.exercise = api.get_exercise(args.assignment)
    if args.exercise is None:
        raise RuntimeError('Exercise does not exist, you can find the correct shortName on ArTEMiS')

    # normalize student names
    if hasattr(args, 'student'):
        args.students = [args.student]

    # by removing whitespaces, commas and duplicates
    args.students = list(set(filter(lambda s: s, [s.replace(' ', '').replace(',', '') for s in args.students])))

    # raise if no well-formed students have been passed to args
    if not args.students:
        raise RuntimeError('No valid student name in args.students')

    # dispatch command
    dispatch = {
        'repos': command_repos,
        # 'getscores': command_get_scores,
        'newresult': command_new_result
    }

    dispatch[args.command]()


if __name__ == "__main__":
    main()

# TODO finish implementing API in detail/artemis_api.py
# TODO port backup/artemis-cli.sh to python
# TODO create symlink to tests repository for every student's submission to
#      make testing a lot easier
# TODO add feature to upload grades
# TODO create an eclipse/intellij project containing all student's submissions)
