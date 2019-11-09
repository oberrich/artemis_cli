import json
import datetime

class Serializable:
    def default(self, o):
        return o.__dict__

    def serialize(self):
        return json.dumps(self, default=self.default, indent=2, sort_keys=True, separators=(',', ': '))


class ManualResultBody(Serializable):
    def __init__(self, score, text, feedbacks, participation):
        # type: (int, str, List[Dict[str,str]], List[Dict[str,str]])
        self.buildArtifact = False
        self.score = score
        self.resultString = text
        self.successful = True if score == 100 else False
        self.participation = participation
        self.completionDate = datetime.datetime.utcnow().isoformat()[:-3] + 'Z'
        self.feedbacks = list(map(lambda f: FeedbackBody(f), feedbacks))


class FeedbackBody(Serializable):
    def __init__(self, feedback):
        # type: (bool, str, str)
        self.credits = 0            # default
        self.type = 'MANUAL'        # default
        self.referenceId = None     # default
        self.referenceType = None   # default

        [setattr(self, k, v) for k,v in feedback.items()]


class LoginBody(Serializable):
    def __init__(self, username, password):
        # type: (str, str)
        self.username = username
        self.password = password
        self.rememberMe = False
