#!/usr/bin/env python
import requests
import json
import sys

if len(sys.argv) != 6:
    raise Exception(
        'usage: python3 _detail_artemis_cli.py action courseid exercise username password \nactions currently include "deadline"');

sys_args = {
    "action": sys.argv[1],
    "course_id": sys.argv[2],
    "exercise": sys.argv[3],
    "username": sys.argv[4],
    "password": sys.argv[5]
}

action = sys_args["action"]

api_base_url = 'https://artemis.ase.in.tum.de/api/'
course_id = sys_args["course_id"]

headers = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
    'X-XSRF-TOKEN': "2d141b5-9e1c-4390-ae06-5143753b4459",
    'Content-Type': "application/json;charset=UTF-8",
    'Accept': "application/json, text/plain, */*",
    'Connection': "keep-alive",
    'TE': "Trailers"
}

cookies = {'XSRF-TOKEN': "2d141b5-9e1c-4390-ae06-5143753b4459"}


def api_post(route, data):
    route = f'{api_base_url}{route}'
    return requests.post(route, headers=headers, cookies=cookies, data=data)


def api_get(route):
    route = f'{api_base_url}{route}'
    return requests.get(route, headers=headers, cookies=cookies)


def authenticate(username, password):
    payload = '{{"username": "{}", "password": "{}", "rememberMe": false}}'.format(username, password)
    resp = api_post('authenticate', payload)

    if resp.status_code != 200:
        raise Exception("Failed to authenticate, result: " + resp.text)

    return resp.json()['id_token']


def programming_exercises():
    return api_get(f'courses/{course_id}/programming-exercises/');


def get_due_date(exercise):
    for attrs in programming_exercises().json():
        if attrs['shortName'] == exercise:
            if 'dueDate' in attrs:
                return attrs['dueDate']
        return None
    raise Exception("Exercise doesn't exist, check shortName of exercise on Artemis")


def action_deadline(exercise):
    due_date = get_due_date(exercise)
    if due_date == None:
        print("2069-01-01T04:20:00+01:00")
    else:
        print(due_date)


def action_get_scores(exercise):
    raise Exception('TODO')


def action_post_scores(exercise):
    raise Exception('TODO')


token = authenticate(sys_args["username"], sys_args["password"])
headers['Authorization'] = f'Bearer {token}'

action_dispatch = {
    "deadline": action_deadline,
    "getscores": action_get_scores,
    "postscores": action_post_scores
}

# "deadline" -> get deadline
# "getscore" -> get scores/build results of student
# "getscores" -> getscores for list of students
# "postscore" -> upload score/feedback for student
# "postscores" -> upload score/feedback for list of students from file

# syntax -score 80 "gut gemacht " -positive "Kommentare" "Gute Dokumentation" -negative "Formatierung" "Bitte nutze Autoformat"

action_dispatch[action](sys_args["exercise"])
exit(0)
