import requests

from detail.artemis_api_payloads import *


class ArtemisAPI:
    def __init__(self, cfg):
        # type: (Dict) -> None
        self._base_url = cfg['base_url']
        self._course = cfg['course']
        self._creds = cfg['credentials']

        # make sure credentials were set
        if not self._creds['username'] or not self._creds['password']:
            raise RuntimeError('Artemis credentials required: Enter your username and password into `config.yml`')

        # create session and set headers and cookies
        s = requests.Session()

        s.headers.update({
            'User-Agent': "github.com/oberrich/artemis_cli",
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
        # type: (str, Serializable) -> Dict
        return self.session.post(self._base_url + route, data=body.serialize()).json()

    def __put(self, route, body):
        # type: (str, Serializable) -> Dict
        return self.session.put(self._base_url + route, data=body.serialize()).json()

    def __get(self, route):
        # type: (str) -> Dict
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
        # type: (Dict) -> int
        return exercise['id'] if 'id' in exercise else None

    @staticmethod
    def get_deadline(exercise):
        # type: (Dict) -> str
        return exercise['dueDate'] if 'dueDate' in exercise else None

    @staticmethod
    def get_participation_id(participation):
        # type: (Dict) -> int
        return participation['id'] if 'id' in participation else None

    def get_results(self, exercise_id, students=None, with_assessors=False):
        # type: (id, List[str], bool) -> List[Dict]
        results = self.__get('/exercises/%d/results?ratedOnly=true&withSubmissions=false&withAssessors=%s'
                             % (exercise_id, str(with_assessors)))
        if students:
            results = list(filter(lambda r: r['participation']['student']['login'] in students, results))
        return results

    def get_result_details(self, result_id):
        # type: (int) -> Dict
        return self.__get('/results/%d/details' % result_id)

    def get_participation(self, participation_id):
        # type: (int) -> Dict
        return self.__get('/participations/%d' % participation_id)

    def post_new_result(self, exercise_id, result, score, text, feedbacks):
        # type: (int, Dict, int, str, List[Dict[str, str, bool]]) -> None
        is_build_result = 'assessmentType' not in result or result['assessmentType'] == 'AUTOMATIC'
        # Maybe dont get participation from participation route, instead build it from /courses/ and /exercises/ routes
        # to closer mimic artemis's use of the api
        participation_id = result['participation']['id']
        body = ManualResultBody(is_build_result, result, score, text, feedbacks)
        self.__put('/participations/%d/manual-results' % participation_id, body)
