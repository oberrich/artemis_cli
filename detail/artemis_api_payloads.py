import json

class Serializable:
    def default(self, o):
        return o.__dict__

    def serialize(self):
        return json.dumps(self, default=self.default, indent=2, separators=(',', ': '))


class ManualResultBody(Serializable):
    '''
    Artemis api new result schema:
      {
        "score" : 85,
        "buildArtifact": false
        "assessmentType": "MANUAL"
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

    def __init__(self, score, text, feedbacks, participation):
        # type: (int, str, List[Dict[str,str]], List[Dict[str,str]])
        self.assessmentType = 'MANUAL'
        self.buildArtifact = False
        self.score = score
        self.resultString = text
        self.successful = True if score == 100 else False
        self.participation = participation
        self.feedbacks = map(lambda f: FeedbackBody(f), feedbacks)

        """
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
        """

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
