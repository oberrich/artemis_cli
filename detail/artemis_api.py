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

    @staticmethod
    def get_exercise_id(exercise):
        return exercise['id'] if 'id' in exercise else None

    @staticmethod
    def get_deadline(exercise):
        return exercise['dueDate'] if 'dueDate' in exercise else None

    def get_results(self, exercise_id):
        return self.__get('/courses/%d/exercises/%d/results?ratedOnly=true&withSubmissions=false&withAssessors=false' % (self._course['id'], exercise_id))

    @staticmethod
    def get_participations(results, students):
        results = filter(lambda r: r['participation']['student']['login'] in students, results)
        return map(lambda r: r['participation'], results)

    @staticmethod
    def get_participation_id(participation):
        return participation['id'] if 'id' in participation else None

    def post_new_result(self, participation_id, score, feedbacks):
        pass
        # type: (str, str, str, List[Dict[str, str, Boolean]])


        # result = self.__get('/courses/37/exercises/733/results?ratedOnly=true&withSubmissions=false&withAssessors=false')
        # result = self.__get('/participations/192130')
        # print(json.dumps(result, indent=4, sort_keys=True))

        # TODO post result via Artemis api, use assignment and student vars if necessary
        # self.__post(route=?, data=data)
