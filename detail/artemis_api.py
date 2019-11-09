import requests
import json

class Serializable:
    def default(self, o):
        return o.__dict__

    def serialize(self):
        return json.dumps(self, default=self.default, indent=2, separators=(',', ': '))


class NewResultBody(Serializable):
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

    def __init__(self, score, result_text, positive_feedback_entries = None, negative_feedback_entries = None):
        # type: (int, str, List[Dict[str,str]], List[Dict[str,str]])
        self.score = score
        self.id = 12345  # TODO get right new result(?) id
        self.resultString = result_text
        self.successful = True if score == 100 else False
        self.feedbacks = [] # type: List[FeedbackBody]

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


class FeedbackBody(Serializable):
    def __init__(self, positive, text, detail_text):
        # type: (bool, str, str)
        self.credits = 0            # default
        self.type = 'MANUAL'        # default
        self.text = text
        self.detailText = detail_text
        self.referenceId = None     # default
        self.referenceType = None   # default
        self.positive = positive


class LoginBody(Serializable):
    def __init__(self, username, password):
        # type: (str, str)
        self.username = username
        self.password = password
        self.rememberMe = False


class ArtemisAPI:
    def __init__(self, cfg):
        self._base_url = cfg['base_url']
        self._course   = cfg['course']
        self._creds    = cfg['credentials']

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
        # type: (string, Serializable) -> Dict
        return json.loads(self.session.post(self._base_url + route, data=body.serialize()).text)

    def __get(self, route):
        # type: (string) -> Dict
        return json.loads(self.session.get(self._base_url + route))

    def __authenticate(self):
        body = LoginBody(
            self._creds['username'],
            self._creds['password']
        )

        resp = self.__post('/authenticate', body)

        if 'id_token' not in resp.keys():
            raise RuntimeError('Failed to authenticate!\nExpected field \'id_token\' in\n  ' + str(resp))

        self.session.auth = ('Bearer', resp['id_token'])

    def post_new_result(self, new_result_body, assignment, student):
        # type: (NewResultBody, str, str)

        print(new_result_body.serialize())

        # TODO post result via Artemis api, use assignment and student vars if necessary
        # self.__post(route=?, data=data)
