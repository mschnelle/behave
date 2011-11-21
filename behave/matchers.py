import re

import parse

from behave import model

class Matcher(object):
    def __init__(self, func, string):
        self.func = func
        self.string = string
        
    def check_match(self, step):
        raise NotImplementedError

    def match(self, step):
        result = self.check_match(step)
        if result is None:
            return None
        return model.Match(self.func, result)

class ParseMatcher(Matcher):
    def __init__(self, func, string):
        super(ParseMatcher, self).__init__(func, string)
        self.parser = parse.compile(self.string)
    
    def check_match(self, step):
        result = self.parser.parse(step)
        if not result:
            return None
            
        args = []
        for index, arg in enumerate(result.fixed, 1):
            start, end = result.spans[index]
            args.append(model.Argument(start, end, step[start:end], arg))
        for name, arg in result.named.items():
            start, end = result.spans[name]
            args.append(model.Argument(start, end, step[start:end], arg, name))
        return args

class RegexMatcher(Matcher):
    def __init__(self, func, string):
        super(RegexMatcher, self).__init__(func, string)
        self.regex = re.compile(self.string)
    
    def check_match(self, step):
        m = self.regex.match(step)
        if not m:
            return None

        groupindex = dict((y, x) for x, y in self.regex.groupindex.items())
        args = []
        for index, group in enumerate(m.groups(), 1):
            name = groupindex.get(index, None)
            args.append(model.Argument(m.start(index), m.end(index), group,
                                       group, name))
        
        return args

matcher_mapping = {
    'parse': ParseMatcher,
    're': RegexMatcher,
}

current_matcher = RegexMatcher

def step_matcher(name):
    global current_matcher
    current_matcher = matcher_mapping[name]

def get_matcher(func, string):
    return current_matcher(func, string)