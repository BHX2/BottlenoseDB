from contexts import Context

def Subcontext(Context):
  def __init__(self, supercontext)
    self.isUniversal = False
    self.clauseTable = dict()
    self.supercontext = supercontext
    self.componentGraph = self.supercontext.DiGraph()
    self.actionGraph = self.supercontext.DiGraph()
    self.stateGraph = self.supercontext.DiGraph()
    self.concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
    self.conceptHashTable = dict()
    self.prototypes = dict()
    
  def add(self, concept):
    if concept not in self:
      if isinstance(concept, NounPhrase):
        self.concepts['noun_phrases'].add(concept)
      elif isinstance(concept, VerbPhrase):
        self.concepts['verb_phrases'].add(concept)
      elif isinstance(concept, Descriptor):
        self.concepts['descriptors'].add(concept)
  