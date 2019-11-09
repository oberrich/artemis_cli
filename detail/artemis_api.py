import requests
import json

from json import JSONEncoder  # somehow necessary
from typing import List, Dict


class DictEncoder(JSONEncoder):
    '''
    wtf Python that I have to implement this myself
    '''
    def default(self, o):
        return o.__dict__


class NewResultBody:
    '''
    Artemis api new result schema:
      {
        "score" : 85,
        "id": 191374,
        "resultString": "Excellent!",
        "successful": "false",
        "feedbacks": [
          {
            "credits": 0,
            "type": "MANUAL",
            "text": "well done!",
            "detailText" : "detailText",
            "referenceId": null,
            "referenceType": null,
            "positive": "true"
          }
        ]
      }
    '''

    def __init__(self,
                 score: int,
                 result_text: str,
                 positive_feedback_entries: List[Dict[str, str]] = None,
                 negative_feedback_entries: List[Dict[str, str]] = None):
        self.score = score
        self.id = 12345  # TODO get right new result(?) id
        self.result_String = result_text
        self.successful = True if score == 100 else False
        self.feedbacks: List[FeedbackBody] = []
        if positive_feedback_entries is not None:
            for pos_feedback in positive_feedback_entries:
                pos_feedback_body = FeedbackBody(positive=True,
                                                 text=pos_feedback["text"],
                                                 detail_text=pos_feedback["detail_text"])
                self.feedbacks.append(pos_feedback_body)
        if negative_feedback_entries is not None:
            for neg_feedback in negative_feedback_entries:
                neg_feedback_body = FeedbackBody(positive=False,
                                                 text=neg_feedback["text"],
                                                 detail_text=neg_feedback["detail_text"])
                self.feedbacks.append(neg_feedback_body)


class FeedbackBody:
    def __init__(self, positive: bool, text: str, detail_text: str):
        self.credits = 0            # default
        self.type = 'MANUAL'        # default
        self.text = text
        self.referenceId = None     # default
        self.referenceType = None   # default
        self.positive = positive


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

    def __request_post(self, route, data):
        return json.loads(self.session.post(self._base_url + route, data=json.dumps(data)).text)

    def __request_get(self, route):
        return self.session.get(self._base_url + route)

    def __authenticate(self):
        payload = {
            'username': self._creds['username'],
            'password': self._creds['password'],
            'rememberMe': False
        }

        resp = self.__request_post('/authenticate', payload)

        if 'id_token' not in resp.keys():
            raise RuntimeError('Failed to authenticate!\nExpected field \'id_token\' in\n  ' + str(resp))

        self.session.auth = ('Bearer', resp['id_token'])

    def post_new_result(self, new_result_body: NewResultBody, assignment: str, student: str):

        data = json.dumps(new_result_body,
                          cls=DictEncoder,
                          indent=4,
                          separators=(',', ': '))
        print(data)

        # TODO post result via Artemis api, use assignment and student vars if necessary
        # self.__request_post(route=?, data=data)