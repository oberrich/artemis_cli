#!/usr/bin/env python

# pip install pyyaml argparse requests json
import yaml
import argparse

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

api = ArtemisAPI(cfg['artemis'])

# TODO finish implementing API in detail/artemis_api.py
# TODO port backup/artemis-cli.sh to python
# TODO create symlink to tests repository for every student's submission to
#      make testing a lot easier
# TODO add feature to upload grades
#(TODO create an eclipse/intellij project containing all student's submissions)  