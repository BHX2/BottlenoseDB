import sys
import weakref
from pattern.search import Taxonomy
from pattern.search import WordNetClassifier

sys.dont_write_bytecode = True
# Keeps directory clean by not compiling utilities to bytecode
import utilities

class Concept:
  taxonomy = Taxonomy()
  taxonomy.classifiers.append(WordNetClassifier())
  thesaurus = dict()
  _instances = set()
  
  def __init__(self, name=None, type=None):
    if name: 
      self.name = utilities.camelCase(name)
    else:
      self.name = None
    if type: 
      type = utilities.sanitize(type)
      if name:
        self.classify(utilities.sanitize(name), utilities.sanitize(type))
      self.type = utilities.camelCase(type)
    else:
      self.type = None
    self._instances.add(weakref.ref(self))
  
  @classmethod
  def instances(clss):
    dead = set()
    for reference in clss._instances:
      instance = reference()
      if instance is not None:
        yield instance
      else:
        dead.add(reference)
    clss._instances -= dead
    
  def ancestors(self, type=None):
    if not type: 
      if not self.type:
        return None
      type = self.type
    type = utilities.sanitize(type)
    response = utilities.unicodeDecode(self.taxonomy.parents(type, recursive=True))
    response.append(utilities.camelCase(type))
    return response
    
  def descendants(self, name=None):
    if not name: 
      if not self.name:
        return None
      name = self.name
    name = utilities.sanitize(name)
    if name.istitle(): return
    firstPass = utilities.unicodeDecode(self.taxonomy.children(name, recursive=False))
    response = []
    for thing in firstPass:
      if utilities.sanitize(thing).istitle():
        continue
      else:
        response.extend(utilities.unicodeDecode(self.descendants(thing)))
    response.extend(firstPass)
    return response
    
  def classify(self, term1, term2=None):
    self.type = utilities.camelCase(term1)
    if not term2:
      if not self.name:
        return
      child = self.name
      parent = term1
    else:
      child = term1
      parent = term2
    child = utilities.sanitize(child)
    parent = utilities.sanitize(parent)
    if not self.paternityTest(child, parent) and parent is not child :
      self.taxonomy.case_sensitive = True
      self.taxonomy.append(child, type=parent)
      self.taxonomy.case_sensitive = False
    
  def paternityTest(self, term1, term2=None):
    if not term2:
      if not self.name:
        return False
      child = self.name
      parent = term1
    else:
      child = term1
      parent = term2
    child = utilities.sanitize(child)
    parent = utilities.sanitize(parent)
    existingParents = map(str, self.taxonomy.parents(child, recursive=True))
    return parent in existingParents

  def equate(self, *phrases):
    if self.name: phrases += (self.name,)
    phrases = map(utilities.camelCase, phrases)
    phraseSets = map(self.synonyms, phrases)
    mergedSet = set.union(*phraseSets)
    for phrase in mergedSet:
      self.thesaurus[phrase] = mergedSet
      
  def synonyms(self, phrase=None):
    if not phrase:
      if not self.name:
        return False
      phrase = self.name
    phrase = utilities.camelCase(phrase)
    listOfSetsWithPhrase = []
    for key in self.thesaurus:
      if phrase in self.thesaurus[key]:
        if self.thesaurus[key] not in listOfSetsWithPhrase:
          listOfSetsWithPhrase.append(self.thesaurus[key])
    if len(listOfSetsWithPhrase) == 0:
      self.thesaurus[phrase] = {phrase}
    elif len(listOfSetsWithPhrase) > 1:
      mergedSet = set.union(*listOfSetsWithPhrase)
      for element in mergedSet:
        self.thesaurus[element] = mergedSet
    elif phrase not in self.thesaurus:
      self.thesaurus[phrase] = listOfSetsWithPhrase[0]
    return self.thesaurus[phrase]
    

  

		