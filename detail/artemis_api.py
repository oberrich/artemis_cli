import requests
import json

class ArtemisAPI:

  def __init__(self, cfg):
    self.base_url = cfg['base_url']
    self.course = cfg['course']
    self.creds = cfg['credentials']

    s = requests.Session()
    s.headers.update({
      'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
      'X-XSRF-TOKEN': "2d141b5-9e1c-4390-ae06-5143753b4459",
      'Content-Type': "application/json;charset=UTF-8",
      'Accept': "application/json, text/plain, */*",
      'Connection': "keep-alive",
      'TE': "Trailers"
    });
    
    s.cookies.update({
      'XSRF-TOKEN': "2d141b5-9e1c-4390-ae06-5143753b4459"
    })

    # call raise_for_status() for every response
    s.hooks = {
      'response': lambda r, *args, **kwargs: r.raise_for_status()
    }

    self.session = s;
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

  def TODO(self):
    pass
