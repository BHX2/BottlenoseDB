from contexts import Context

def Subcontext(Context):
  def __init__(self, supercontext)
    self.isUniversal = False
    self.clauseTable = dict()
    self.supercontext = supercontext
    self.componentGraph = self.supercontext.componentGraph
    self.actionGraph = self.supercontext.actionGraph
    self.stateGraph = self.supercontext.stateGraph
    self.concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
    self.conceptHashTable = self.supercontext.conceptHashTable
    self.prototypes = self.supercontext.prototypes
    self.potentialTaxonomy = self.supercontext.potentialTaxonomy
    self.potentialComponentGraph = self.supercontext.potentialComponentGraph
    self.potentialActionGraph = self.supercontext.potentialActionGraph
    self.potentialStateGraph = self.supercontext.potentialStateGraph
    
  def add(self, concept):
    if concept not in self:
      if isinstance(concept, NounPhrase):
        self.concepts['noun_phrases'].add(concept)
      elif isinstance(concept, VerbPhrase):
        self.concepts['verb_phrases'].add(concept)
      elif isinstance(concept, Descriptor):
        self.concepts['descriptors'].add(concept)
  