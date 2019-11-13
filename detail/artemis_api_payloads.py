import json
import datetime

if False:
    from typing import List, Dict


class Serializable:
    @staticmethod
    def default(o):
        return o.__dict__

    def serialize(self):
        return json.dumps(self, default=self.default, indent=2, sort_keys=True, separators=(',', ': '))


class ManualResultBody(Serializable):
    def __init__(self, is_build_result, result, score, text, feedbacks, participation):
        # type: (bool, Dict, int, str, List[Dict[str,str,bool]], Dict) -> None
        
        # if this is a build reset, don't submit an id to the request so a new result is created
        if not is_build_result:
            # just all fields of original result in case we missed something
            [setattr(self, k, v) for k, v in result.items()]
            self.id = result['id']
        self.rated = True
        self.assessmentType = "MANUAL"
        self.buildArtifact = False
        self.score = score
        self.resultString = text
        self.successful = True if score == 100 else False
        self.participation = participation
        self.completionDate = datetime.datetime.utcnow().isoformat()[:-6] + '000Z'
        self.feedbacks = list(map(lambda f: FeedbackBody(f), feedbacks))
        self.hasFeedback = True if self.feedbacks else False


class FeedbackBody(Serializable):
    def __init__(self, feedback):
        # type: (Dict[str, str, bool]) -> None
        self.credits = 0            # default
        self.type = 'MANUAL'        # default
        self.referenceId = None     # default
        self.referenceType = None   # default

        [setattr(self, k, v) for k, v in feedback.items()]


class LoginBody(Serializable):
    def __init__(self, username, password):
        # type: (str, str) -> None
        self.username = username
        self.password = password
        self.rememberMe = False
