from contexts import Context

def Subcontext(Context):
  def __init__(self, supercontext)
    self.supercontext = supercontext
    self.componentGraph = self.supercontext.DiGraph()
    self.actionGraph = self.supercontext.DiGraph()
    self.stateGraph = self.supercontext.DiGraph()
    self._concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
    
  def add(self, concept):
    if concept not in self:
      if isinstance(concept, NounPhrase):
        self._concepts['noun_phrases'].add(concept)
      elif isinstance(concept, VerbPhrase):
        self._concepts['verb_phrases'].add(concept)
      elif isinstance(concept, Descriptor):
        self._concepts['descriptors'].add(concept)
  