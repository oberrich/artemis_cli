#!/usr/bin/env python

# pip install pyyaml
import yaml
import argparse

from detail.artemis_api import ArtemisAPI

parser = argparse.ArgumentParser(description='A command-line application for tutors to more productively grade programming excises on ArTEMiS')
# TODO: think of and parse arguments
args = parser.parse_args(); 

with open('config.yml', 'r') as config_file:
    cfg = yaml.safe_load(config_file)

creds = cfg['artemis']['credentials'];

if not creds['username'] or \
   not creds['password'] or \
	   creds['password'] == 's3cur3_l337sp33k_p4zzw0rd':
	pass # raise RuntimeError('Artemis credentials required: Enter your username and password into `config.yml`')

api = ArtemisAPI()
# TODO implement API in detail/artemis_api.py
