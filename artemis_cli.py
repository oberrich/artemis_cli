#!/usr/bin/env python
# coding: utf-8

# pip install pyyaml argparse requests unicodecsv
import fnmatch
import shutil

import yaml
import os
import sys
import random
import re
import subprocess
import json
import datetime
import unicodecsv as csv

from shutil import copytree, copyfile, ignore_patterns
from functools import partial
from xml.etree import ElementTree
from codecs import open

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


# https://stackoverflow.com/a/6257321
def find_and_replace(directory, find, replace, file_pattern):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, file_pattern):
            filepath = os.path.join(path, filename)
            with open(filepath, encoding='utf-8') as f:
                s = f.read()
            s = s.replace(find, replace)
            with open(filepath, "w", encoding='utf-8') as f:
                f.write(s)


def generate_gradebook(gradebook_dir, students):
    filename = os.path.join(gradebook_dir, 'gradebook.yml')


    penguin_species = [
        'Adéliepinguin',
        'Brillenpinguin',
        'Dickschnabelpinguin',
        'Eselspinguin',
        'Galápagospinguin',
        'Gelbaugenpinguin',
        'Goldschopfpinguin',
        'Haubenpinguin',
        'Humboldtpinguin',
        'Kaiserpinguin',
        'Kronenpinguin',
        'Königspinguin',
        'Magellanpinguin',
        'Snaresinselpinguin',
        'Südlicher Felsenpinguin',
        'Zwergpinguin',
        'Zügelpinguin'
    ]

    if os.path.exists(filename):
        print('Warning: gradebook already existed, delete the gradebook and run '
              'the repos command again if you want to generate a new gradebook.')
        return
    else:
        assessments = ["""
  - name: %s
    score: 100
    text: ''
    negative:
      - text: ''
        detail: ''
      - text: ''
        detail: ''
    positive:
      - text: ''
        detail: ''
  # %s""" % (s, random.choice(penguin_species)) for s in students]

        gradebook = """generated_at: %s
assignment: %s
# %s
assessments:%s""" % (datetime.datetime.utcnow().isoformat(), args.assignment,
                     ','.join([s for s in students]),
                     ''.join(assessments))

        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(gradebook.encode('utf-8').decode('utf-8'))
            print('Successfully created %s' % filename)
        except:
            print("Failed to create %s due to error:\n" % filename)
            os.remove(filename)
            raise


def command_repos():
    # TODO check if paths with spaces are working properly
    assignment = args.assignment
    deadline = api.get_deadline(args.exercise)

    num_students = len(args.students)
    num_succeeded = 0

    # TODO rename to root_dir and add option to config.yml
    script_dir = os.path.dirname(os.path.realpath(__file__))

    print('Fetching %s-%s@{%s} for %d student%s.\n' % (course_name, assignment, str(deadline),
                                                       num_students, '' if num_students == 1 else 's'))

    special_repos = ['tests', 'exercise', 'solution']

    course_dir = os.path.join(script_dir, course_name)
    if not os.path.exists(course_dir):
        os.mkdir(course_dir)
    elif not os.path.isdir(course_dir):
        print('Failed to create %s/ folder, because a non-directory file with the same name already exists.'
              % course_dir)
        sys.exit(1)

    assignment_dir = os.path.join(course_dir, assignment)
    if not os.path.exists(assignment_dir):
        os.mkdir(assignment_dir)
    elif not os.path.isdir(assignment_dir):
        print('Failed to create %s/ folder, because a non-directory file with the same name already exists.'
              % assignment_dir)
        sys.exit(1)

    package_name = None
    pom_xml_tpl = None
    sandbox_ver = "0.1.3"
    minijava_exists = False

    if general['link_tests'] and course_name == 'pgdp1920':
        with open(os.path.join(script_dir, 'detail', 'pom.xml.tpl'), 'r') as tpl_file:
            pom_xml_tpl = tpl_file.read()

    for student in special_repos + args.students:
        sys.stdout.write('Fetching assigment for %s... ' % student)
        sys.stdout.flush()

        repo_name = '%s%s-%s' % (course_name, assignment, student)
        repo_url = '/'.join([bitbucket, 'scm', course_name + assignment, repo_name + '.git'])

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

        if not any(student in s for s in special_repos) and deadline is not None:
            _, rev = run_git(['rev-list', '-1', '--before="%s"' % deadline, 'master'], cwd=repo_dir)
            run_git(['checkout', '`%s`' % rev], cwd=repo_dir)

        run_git(['remote', 'set-url', '--push', 'origin', 'forbidden'], cwd=repo_dir)

        num_succeeded += 1
        print('ok!')

        if general['fix_eclipse_import']:
            dot_project_path = os.path.join(repo_dir, '.project')

            if os.path.exists(dot_project_path):
                # parse .project file and find projectDescription/name
                dot_project = ElementTree.parse(dot_project_path)
                name = dot_project.getroot().find('name')
                project_name = '%s%s' % (assignment, student)
                # and if not already done
                if name is not None and not name.text == project_name:
                    # append student name to it
                    name.text = project_name
                    # and write back to .project file
                    dot_project.write(dot_project_path)
            else:
                pass  # fail silently, project may not be a Java project

        if general['link_tests'] and course_name == 'pgdp1920':
            if student == 'tests':
                pom_xml_path = os.path.join(repo_dir, 'pom.xml')
                if os.path.exists(pom_xml_path):
                    schema = '{http://maven.apache.org/POM/4.0.0}'
                    pom_xml = ElementTree.parse(pom_xml_path)
                    group_id = pom_xml.getroot().find('%sgroupId' % schema)
                    if group_id is not None:
                        package_name = group_id.text
                    # extract sandbox version
                    depends = pom_xml.getroot().find('%sdependencies' % schema)
                    depends = depends.findall('%sdependency' % schema)

                    for depend in depends:
                        artifact_id = depend.find('%sartifactId' % schema)
                        if artifact_id.text == 'artemis-java-test-sandbox':
                            sandbox_ver = depend.find('%sversion' % schema).text

                new_test_dir = os.path.join(assignment_dir, 'tutortest')
                if not os.path.exists(new_test_dir):
                    test_api_package = 'tum.pgdp.testapi'

                    test_dir = os.path.join(*([repo_dir, 'test'] + package_name.split('.')))
                    test_api_dir = os.path.join(*([repo_dir, 'test'] + test_api_package.split('.')))

                    has_test_dir = os.path.exists(test_dir)
                    is_artemist_test = not has_test_dir
                    if is_artemist_test:
                        test_dir = os.path.join(*([repo_dir, 'structural', 'test'] + package_name.split('.')))
                        test_api_dir = os.path.join(*([repo_dir, 'behavior', 'test'] + package_name.split('.')))

                        if not os.path.exists(test_dir) or not os.path.exists(test_api_dir):
                            raise RuntimeError("Unknown Test API")

                    has_test_api = os.path.exists(test_api_dir)

                    copytree(test_dir, new_test_dir, ignore=ignore_patterns(
                        'testutils' if not is_artemist_test else 'DUMMYFILTER', 'pom.xml'))
                    if has_test_api:
                        if not is_artemist_test:
                            copytree(test_api_dir, os.path.join(new_test_dir, 'testapi'))
                        else:
                            copytree(test_api_dir, os.path.join(new_test_dir, 'behavior'), ignore=ignore_patterns(
                                'pom.xml'))

                    # find_and_replace(new_test_dir, package_name, package_name + '.tutortest', '*.java')
                    if has_test_api and not is_artemist_test:
                        find_and_replace(new_test_dir, test_api_package, package_name + '.tutortest.testapi', '*.java')

                    find_and_replace(new_test_dir,
                                     'package %s;' % package_name,
                                     'package %s.tutortest;\nimport %s.*;' % (package_name, package_name),
                                     '*.java')
                    minijava_exists = os.path.exists(os.path.join(new_test_dir, 'MiniJava.java'))
                pass
            elif package_name is not None:
                student_test_path = os.path.join(*([repo_dir, 'src'] + package_name.split('.') + ['tutortest']))

                if not os.path.exists(student_test_path):
                    copytree(os.path.join(assignment_dir, 'tutortest'), student_test_path)

                    minijava_path = os.path.join(os.path.join(student_test_path, 'MiniJava.java'))
                    if minijava_exists:
                        student_minijava_path = os.path.join(*([repo_dir, 'src'] + package_name.split('.') + ['MiniJava.java']))
                        if os.path.exists(student_minijava_path):
                            find_and_replace(student_test_path, package_name + '.tutortest', package_name, 'MiniJava.java')
                            os.remove(student_minijava_path)
                            copyfile(minijava_path, student_minijava_path)
                            os.remove(minijava_path)

                if pom_xml_tpl:
                    with open(os.path.join(repo_dir, 'pom.xml'), 'w') as pom_file:
                        fs_name = package_name.replace('.', '-') + '-' + student
                        package_path = '/'.join(package_name.split('.'))
                        pom_file.write(pom_xml_tpl % (package_name, fs_name, fs_name, package_path, package_path, sandbox_ver))

    num_repos = num_students + len(special_repos)
    print('\nManaged to successfully fetch %d/%d (%.0f%%) repositories.'
          % (num_succeeded, num_repos, num_succeeded / float(num_repos) * 100.))

    if num_students > 2:
        generate_gradebook(assignment_dir, args.students)


def command_grades():
    print('Fetching results for all students, this may take a few seconds...\n')
    results = api.get_results(api.get_exercise_id(args.exercise), args.students)

    num_submitted = 0

    for assessment in args.gradebook['assessments']:
        try:
            args.students[0] = assessment['name']  # hacky
            args.score = assessment['score']
            args.text = assessment['text']

            # make sure changes don't break old gradebook formats
            # TODO remove else-block in a few weeks from now (11/13/2019)
            if 'generated_at' in args.gradebook:
                args.positive = [[f['text'], f['detail']] for f in assessment['positive'] if f['text']]
                args.negative = [[f['text'], f['detail']] for f in assessment['negative'] if f['text']]
            else:
                args.positive = list(filter(lambda f: f[0], assessment['positive']))
                args.negative = list(filter(lambda f: f[0], assessment['negative']))

            command_grade(results=results)
            num_submitted += 1
        except Exception as err:
            print('Failed to submit student %s because %s' % (args.students[0], str(err)))

    print('Done, submitted results for %d students!' % num_submitted)


def command_results():
    print('Fetching results for all students, this may take a few seconds...\n')

    results = api.get_results(api.get_exercise_id(args.exercise), args.students, with_assessors=True)

    with open('results.csv', 'wb') as csv_file:
        csv_file.write(u'\ufeff'.encode('utf8'))

        fields = ['name', 'login', 'type', 'score', 'result', 'feedbacks', 'assessor_name', 'assessor_login',
                  'repo']
        writer = csv.DictWriter(csv_file, fieldnames=fields, encoding='utf-8')
        writer.writeheader()

        num_exported = 0

        for result in results:
            is_build_result = 'assessmentType' not in result or result['assessmentType'] == 'AUTOMATIC'

            feedbacks = api.get_result_details(result['id']) \
                if ('hasFeedback' in result and result['hasFeedback']) else []
            feedbacks = list(map(
                lambda f: {
                    'text': f['text'],
                    'detailText': f['detailText'] if 'detailText' in f else '<null>',
                    'positive': f['positive'] if 'positive' in f else '<null>'
                },
                feedbacks
            ))

            if is_build_result:
                feedbacks = list(filter(lambda f: f['positive'] is False, feedbacks))

            participation = result['participation']
            student = participation['student']

            assessor_name = ''
            assessor_login = ''

            if is_build_result:
                assessor_name = 'Bamboo'
            elif 'assessor' in result:
                assessor_name = result['assessor']['name']
                assessor_login = result['assessor']['login']

            writer.writerow({
                'name': student['name'],
                'login': student['login'],
                'type': result['assessmentType'],
                'score': result['score'],
                'result': result['resultString'],
                'feedbacks': feedbacks,
                'assessor_name': assessor_name,
                'assessor_login': assessor_login,
                'repo': participation['repositoryUrl']
            })

            num_exported += 1

    print('Done, exported %d results to result.csv' % num_exported)


def command_grade(results=None):
    if results is not None:
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
    def any_invalid(fs):
        return any((len(f) != 1 and len(f) != 2) or not f[0] for f in fs)

    if any_invalid(args.positive) or any_invalid(args.negative):
        raise RuntimeError('Text for feedback is required (detail_text is optional, no extra arguments allowed)')

    # map arguments to a well-formed dictionary
    def dict_mapper(f, positive):
        return {'text': f[0], 'detailText': '' if len(f) == 1 else f[1], 'positive': positive}

    feedbacks = list(map(partial(dict_mapper, positive=True), args.positive))
    # and combine positive and negative feedbacks
    feedbacks.extend([x for x in list(map(partial(dict_mapper, positive=False), args.negative))])

    if not is_internal_use:
        print('Fetching results for all students, this may take a few seconds...')
        results = api.get_results(api.get_exercise_id(args.exercise))

    student_result = [r for r in results if r['participation']['student']['login'] == args.students[0]]
    if not student_result:
        raise RuntimeError('No previous result for student')

    if not is_internal_use:
        print('Submitting feedback for student ' + args.students[0])
    api.post_new_result(args.exercise, student_result[0], args.score, args.text, feedbacks)

    if not is_internal_use:
        print('Done!')


def main():
    global args, general, api, bitbucket, course_name, course_id
    # disable stdout if --quiet
    # parse arguments
    parser = ArgParser()
    args = parser.parse_args()

    # load config
    with open('config.yml', 'r', encoding='utf-8') as config_file:
        cfg = yaml.safe_load(config_file)

    # alias commonly used config fields
    general = cfg['general']
    artemis = cfg['artemis']
    bitbucket = cfg['bitbucket']['base_url']
    course_name = artemis['course']['name']
    course_id = artemis['course']['id']

    # instantiate the artemis api client
    api = ArtemisAPI(artemis)

    # for Python 2.7 compatibility: FileNotFoundError throws a NameError and when the file
    # does not exist, `open` throws an IOError instead of a FileNotFoundError
    if args.command == 'grades':
        args.gradebook = None
        try:
            with open(args.file, 'r', encoding='utf-8') as file:
                args.gradebook = yaml.load(file, Loader=yaml.SafeLoader)
        except Exception as err:
            print(err)
            print('Example for gradebook path pgdp1920/w01h01/gradebook.yml')
            sys.exit(1)

        args.assignment = args.gradebook['assignment']
        args.students = list(map(lambda s: s['name'], args.gradebook['assessments']))

    # get exercise data from artemis, raise if it doesn't exist
    args.exercise = api.get_exercise(args.assignment)
    if args.exercise is None:
        print('Exercise does not exist, you can find the correct shortName on ArTEMiS')
        sys.exit(1)

    # normalize student names
    if hasattr(args, 'student'):
        args.students = [args.student]

    if args.command != 'results' or hasattr(args, 'students'):
        # split students by comma, strip white spaces, remove empty students and duplicates then sort list of students
        args.students = sorted(list(set([s.strip() for ss in args.students for s in ss.split(',') if s])))
        # raise if no well-formed students have been passed to args
        if not args.students:
            print('No valid student name in args.students')
            exit(1)
    else:
        args.students = None

    # dispatch command
    dispatch = {
        'repos': command_repos,
        'grade': command_grade,
        'grades': command_grades,
        'results': command_results
    }

    dispatch[args.command]()


if __name__ == '__main__':
    main()
