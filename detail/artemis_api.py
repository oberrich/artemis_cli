import requests
import json

from detail.artemis_api_payloads import *


class ArtemisAPI:
    def __init__(self, cfg):
        self._base_url = cfg['base_url']
        self._course = cfg['course']
        self._creds = cfg['credentials']

        # make sure credentials were set
        if not self._creds['username'] or \
            not self._creds['password'] or \
            self._creds['password'] == 's3cur3_l337sp33k_p4zzw0rd':
            raise RuntimeError('Artemis credentials required: Enter your username and password into `config.yml`')

        # create session and set headers and cookies
        s = requests.Session()

        s.headers.update({
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
            'X-XSRF-TOKEN': "2d141b5-9e1c-4390-ae06-5143753b4459",
            'Content-Type': "application/json;charset=UTF-8",
            'Accept': "application/json, text/plain, */*",
            'Connection': "keep-alive",
            'TE': "Trailers"
        })

        s.cookies.update({
            'XSRF-TOKEN': "2d141b5-9e1c-4390-ae06-5143753b4459"
        })

        # setup a hook that calls raise_for_status() on every response
        s.hooks = {
            'response': lambda r, *args, **kwargs: r.raise_for_status()
        }

        self.session = s
        self.__authenticate()

    def __post(self, route, body):
        # type: (str, Serializable) -> dict
        return self.session.post(self._base_url + route, data=body.serialize()).json()

    def __get(self, route):
        # type: (str) -> dict
        return self.session.get(self._base_url + route).json()

    def __authenticate(self):
        body = LoginBody(
            self._creds['username'],
            self._creds['password']
        )

        resp = self.__post('/authenticate', body)

        if 'id_token' not in resp.keys():
            raise RuntimeError('Failed to authenticate!\nExpected field \'id_token\' in\n  ' + str(resp))

        self.session.headers.update({'Authorization': 'Bearer ' + resp['id_token']})

    def get_exercise(self, short_name):
        exercises = self.__get('/courses/%d/programming-exercises/' % self._course['id'])

        for exercise in exercises:
            if exercise['shortName'] == short_name:
                return exercise
        return None

    def get_deadline(self, exercise):
        if 'dueDate' in exercise:
            return exercise['dueDate']
        return None

    def post_new_result(self, new_result_body, assignment, student):
        # type: (NewResultBody, str, str) -> None

        print(new_result_body.serialize())

        # TODO post result via Artemis api, use assignment and student vars if necessary
        # self.__post(route=?, data=data)
