from time import clock, sleep
import requests
import re
import json

try:
    from pyokc.settings import DELAY
except ImportError:
    from settings import DELAY

class Jsonifiable:
    '''Mixin to allow automatic serialization of objects as JSON.  Adds
    two methods, as_json and to_json.  as_json returns a dict that
    will be converted to JSON, and to_json converts said dict to JSON.
    The default implementation of as_json includes all attributes of
    the object that have simple JSON representations, excluding
    anything that begins with a double underscore.

    '''

    # types that can be output to JSON
    types = (int, float, str, list, tuple, dict, type(None))

    @classmethod
    def jsonify(cls, val):
        if hasattr(val, 'as_json'):
            val = val.as_json()
        if isinstance(val, (list, tuple)):
            val = [cls.jsonify(i) for i in val]
        elif hasattr(val, 'items'):
            val = {cls.jsonify(k): cls.jsonify(v) for (k, v) in val.items()}
        if not isinstance(val, cls.types):
            raise TypeError
        return val

    def as_json(self, exclude='^__'):
        result = {}
        for key in self.__dict__:
            if re.search(exclude, key):
                continue
            val = getattr(self, key)
            try:
                val = self.jsonify(val)
            except TypeError:
                continue
            result[key] = val
        return result

    def to_json(self, *args, **kw):
        # given here are passed on to json.dumps
        obj = self.as_json()
        return json.dumps(obj, *args, **kw)


class Session(requests.Session):
    def __init__(self):
        super().__init__()
        clock()
        self.timestamp = -DELAY

    def post(self, *args, **kwargs):
        while clock() - self.timestamp < DELAY:
            pass
        self.timestamp = clock()
        response = super().post(*args, **kwargs)
        response.raise_for_status()
        return response

    def get(self, *args, **kwargs):
        while clock() - self.timestamp < DELAY:
            pass
        self.timestamp = clock()
        response = super().get(*args, **kwargs)
        response.raise_for_status()
        return response

class MessageThread:
    """
    Represent a sequence of messages between the main user and
    someone else.
    Parameters
    ----------
    self.sender : str
        The username of the other person with whom you are
        communicating.
    self.threadid : str
        A unique threadid assigned by OKCupid.
    self.unread : bool
        True if you have never read this message. False otherwise.
    self.messages : list of str
        List of messages within this thread. Initially empty. Can be
        updated by calling the read() method of the User class.
    """
    def __init__(self, sender, threadid, unread, session, direction):
        self.sender = sender
        self.threadid = threadid
        self.unread = unread
        self.messages = []
        self._direction = direction

    def __repr__(self):
        if self.unread:
            unread_string = 'Unread'
        else:
            unread_string = 'Read'
        return '<{0} message {1} {2}>'.format(unread_string, self._direction, self.sender)

class Question(Jsonifiable):
    def __init__(self, text, user_answer, explanation):
        self.text = text
        self.user_answer = user_answer
        self.explanation = explanation

    def __repr__(self):
        return '<Question: {0}>'.format(self.text)
