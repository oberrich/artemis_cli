import requests
import json


class ArtemisAPI:

    def __init__(self, cfg):
        self.base_url = cfg['base_url']
        self.course = cfg['course']
        self.creds = cfg['credentials']

        # make sure credentials were set
        if not self.creds['username'] or \
                not self.creds['password'] or \
                self.creds['password'] == 's3cur3_l337sp33k_p4zzw0rd':
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
        return json.loads(self.session.post(self.base_url + route, data=json.dumps(data)).text)

    def __request_get(self, route):
        return self.session.get(self.base_url + route)

    def __authenticate(self):
        payload = {
            'username': self.creds['username'],
            'password': self.creds['password'],
            'rememberMe': False
        }

        resp = self.__request_post('/authenticate', payload)

        if 'id_token' not in resp.keys():
            raise RuntimeError('Failed to authenticate!\nExpected field \'id_token\' in\n  ' + str(resp))

        self.session.auth = ('Bearer', resp['id_token'])

    def todo(self):
        pass
