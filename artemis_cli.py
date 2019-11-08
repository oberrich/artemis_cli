#!/usr/bin/env python

# pip install pyyaml argparse requests json
import yaml
import argparse

from detail.artemis_api import ArtemisAPI

parser = argparse.ArgumentParser(description='A command-line application for tutors to more productively grade programming excises on ArTEMiS')
# TODO: think of and parse arguments
args = parser.parse_args();

with open('config.yml', 'r') as config_file:
    cfg = yaml.safe_load(config_file)

api = ArtemisAPI(cfg['artemis'])

# TODO finish implementing API in detail/artemis_api.py
# TODO port backup/artemis-cli.sh to python
# TODO create symlink to tests repository for every student's submission to
#      make testing a lot easier
# TODO add feature to upload grades
#(TODO create an eclipse/intellij project containing all student's submissions)  