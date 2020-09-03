from segment import Segment


class Word:
    '''A representation of a word, containing multiple Segments.'''

    __slots__ = ['segments']

    def __init__(self, segments):
        self.segments = segments

    def __key(self):
        '''The key of a Word is a tuple containing a tuple for each segment,
        where the first item is the set of segment.positive, the second is
        the set of segment.negative, and the third is the set of segment.zero. The function is necessary 
        to use in both equality testing and hashing; for this reason the hashable frozenset is used.
        '''
        return tuple((frozenset(segment.positive), frozenset(segment.negative), frozenset(segment.zero)) for segment in self.segments)

    def __eq__(self, other):
        '''Compares Word objects by ensuring each segment is equal.'''
        return self.__key() == other.__key()

    def index_applicable(self, index, rule):
        '''Given an index and a rule, check if the segment at the given index
        meets the conditions of the current rule.'''

        # Break out if the current segment isn't applicable.
        if not self.segments[index].meets_conditions(rule['conditions']):
            return False

        # Break out if the segment does not obey optional first, last, before,
        # or after indicators.
        if 'first' in rule:
            if index != 0:
                return False

        if 'last' in rule:
            if index != len(self.segments) - 1:
                return False

        if 'before' in rule:
            if index == 0:
                return False

            before_segment = self.segments[index - 1]
            if not before_segment.meets_conditions(rule['before']):
                return False

        if 'after' in rule:
            if index == len(self.segments) - 1:
                return False

            after_segment = self.segments[index + 1]
            if not after_segment.meets_conditions(rule['after']):
                return False

        # Finally, return True if nothing has caused an early exit
        return True

    def applicable(self, rule):
        '''Returns True if any segment in the word meets all conditions of the
        given rule.'''

        return any(self.index_applicable(i, rule) for i in
                   range(len(self.segments)))

    def apply_rule(self, rule):
        '''Apply the given rule to the current Segments, returning a new Word.'''
        new_segments = []

        # Create a Segment from the rule to add to current segments
        rule_segment = Segment(rule['applies'].get('positive', []),
                               rule['applies'].get('negative', []),
                               rule['applies'].get('zero', []))

        for i in range(len(self.segments)):
            if self.index_applicable(i, rule):
                # If the rule contains the deletion feature, don't add the new
                # segment, effectively removing it entirely. Otherwise, add the
                # modified segment.
                if 'deletion' not in rule['applies'].get('positive', []):
                    new_segments.append(self.segments[i] + rule_segment)

            else:
                new_segments.append(self.segments[i])

        return Word(new_segments)
