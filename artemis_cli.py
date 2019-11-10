#!/usr/bin/env python

# pip install pyyaml argparse requests json
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


def generate_gradebook(dir, students):
    filename = os.path.join(dir, 'gradebook.yml')

    if os.path.exists(filename):
        print('Warning: gradebook already existed, delete the gradebook and run '
              'the repos command again if you want to generate a new gradebook.')

    gradebook = {'assignment': args.assignment, 'assessments': list(map(lambda s: {
        'name': s,
        'score': 100,
        'text': '',
        'positive': [
            ['', '']
        ],
        'negative': [
            ['', ''],
            ['', '']
        ]
    }, students))}

    with open(filename, 'w') as file:
        yaml.dump(gradebook, file, encoding='utf-8')

    print('Successfully created %s' % filename)


def command_repos():
    # TODO apply sanitization in main function
    assignment = args.assignment
    deadline = api.get_deadline(args.exercise)

    num_students = len(args.students)
    num_succeeded = 0

    # TODO rename to root_dir and add option to config.yml
    script_dir = os.path.dirname(os.path.realpath(__file__))

    print('Fetching %s-%s@{%s} for %d student%s.\n' % (course_name, assignment, str(deadline),
                                                       num_students, '' if num_students == 1 else 's'))

    special_repos = ['exercise', 'solution', 'tests']

    course_dir = os.path.join(script_dir, course_name)
    if not os.path.exists(course_dir):
        os.mkdir(course_dir)
    elif not os.path.isdir(course_dir):
        print('Failed to create %s/ folder, because a non-directory file with the same name already exists.' % course_dir)
        sys.exit(1)

    assignment_dir = os.path.join(course_dir, assignment)
    if not os.path.exists(assignment_dir):
        os.mkdir(assignment_dir)
    elif not os.path.isdir(assignment_dir):
        print('Failed to create %s/ folder, because a non-directory file with the same name already exists.' % assignment_dir)
        sys.exit(1)

    for student in special_repos + args.students:
        sys.stdout.write('Fetching assigment for %s... ' % student)
        sys.stdout.flush()

        repo_name = "%s%s-%s" % (course_name, assignment, student)
        repo_url = os.path.join(bitbucket, 'scm', course_name + assignment, repo_name + '.git')

        repo_dir = os.path.join(assignment_dir, student)

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

    num_repos = num_students + len(special_repos)
    print('\nManaged to successfully fetch %d/%d (%.0f%%) repositories.' % (num_succeeded, num_repos, num_succeeded / float(num_repos) * 100.))

    #if num_students > 2:
    generate_gradebook(assignment_dir, args.students)


def command_grades():
    print('Fetching results for all students, this may take a few seconds...')
    results = api.get_results(api.get_exercise_id(args.exercise), args.students)

    for assessment in args.gradebook['assessments']:
        try:
            args.students[0] = assessment['name'] # hacky
            args.score = assessment['score']
            args.text = assessment['text']
            args.positive = list(filter(lambda f: f[0], assessment['positive']))
            args.negative = list(filter(lambda f: f[0], assessment['negative']))

            command_grade(results=results)
        except RuntimeError as err:
            print('  Failed with error: ' + str(err))
            print('  Continuing with next student')

    print('Done!')


def command_get_scores():
    print('Chosen command: getscores not implemented yet.')
    sys.exit(1)


def command_grade(results=None):
    results = results[:]
    is_internal_use = results is not None

    # TODO change so we can reuse it for submitting all student's scores
    if args.score not in range(0, 101):
        raise RuntimeError('score has to be within [0;100]')

    if not args.text:
        raise RuntimeError('text cannot be \'\' or None')

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

    if not is_internal_use:
        print('Fetching results for all students, this may take a few seconds...')
        results = api.get_results(api.get_exercise_id(args.exercise))

    participations = [p['participation'] for p in results if p['participation']['student']['login'] == args.students[0]]
    if not participations:
        raise RuntimeError('No participations for any of the students')

    print('Submitting feedback for student ' + args.students[0])
    api.post_new_result(participations[0]['id'], args.score, args.text, feedbacks)

    if not is_internal_use:
        print('Done!')


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

    if args.command == 'grades':
        args.gradebook = None

        try:
            with open(args.gradebook_file, 'r') as file:
                args.gradebook = yaml.load(file)
        except FileNotFoundError as err:
            print(err)
            print('Example for gradebook path pgdp1920/w01h01/gradebook.yml')
            sys.exit(1)

        args.assignment = args.gradebook['assignment']
        args.students = list(map(lambda s: s['name'], args.gradebook['assessments']))

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
        'grade': command_grade,
        'grades': command_grades
    }

    dispatch[args.command]()


if __name__ == "__main__":
    main()
