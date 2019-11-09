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
