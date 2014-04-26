import os
import weakref
from pattern.search import Taxonomy
from pattern.search import WordNetClassifier
import utilities

class Concept:
  taxonomy = Taxonomy()
  wordnetClassifier = WordNetClassifier()
  taxonomy.classifiers.append(wordnetClassifier)
  thesaurus = dict()
  
  def __init__(self, name=None, type=None):
    if name: 
      self.name = utilities.camelCase(name)
    else:
      if type:
        if type.istitle():
          self.name = utilities.camelCase(type)
        else:
          self.name = utilities.camelCase(type) + '-' + os.urandom(5).encode('hex')
      else:
        self.name = os.urandom(10).encode('hex')
    if type: 
      self.classify(utilities.sanitize(self.name), utilities.sanitize(type))
  
  def parents(self, name=None):
    if not name:
      name = self.name
    name = utilities.sanitize(name)
    if name.istitle():
      self.taxonomy.classifiers = []
      self.taxonomy.case_sensitive = True
    if not getattr(self, 'isVerb', False):
      response = utilities.unicodeDecode(self.taxonomy.parents(name, recursive=False))
    else:
      response = utilities.unicodeDecode(self.taxonomy.parents(name, recursive=False, pos='VB'))
    if name.istitle():
      self.taxonomy.classifiers.append(self.wordnetClassifier)
      self.taxonomy.case_sensitive = False
    return response
    
  def ancestors(self, name=None):
    if not name: 
      name = self.name
    name = utilities.sanitize(name)
    if name.istitle():
      self.taxonomy.classifiers = []
      self.taxonomy.case_sensitive = True
    if not getattr(self, 'isVerb', False):
      response = utilities.unicodeDecode(self.taxonomy.parents(name, recursive=True))
    else:
      response = utilities.unicodeDecode(self.taxonomy.parents(name, recursive=True, pos='VB'))
    if name.istitle():
      self.taxonomy.classifiers.append(self.wordnetClassifier)
      self.taxonomy.case_sensitive = False
    return response
    
  def descendants(self, name=None):
    if not name: 
      name = self.name
    name = utilities.sanitize(name)
    if name.istitle(): return
    if not getattr(self, 'isVerb', False):
      firstPass = utilities.unicodeDecode(self.taxonomy.children(name, recursive=False))
    else:
      firstPass = utilities.unicodeDecode(self.taxonomy.children(name, recursive=False, pos='VB'))
    response = []
    for thing in firstPass:
      if utilities.sanitize(thing).istitle():
        continue
      else:
        response.extend(utilities.unicodeDecode(self.descendants(thing)))
    response.extend(firstPass)
    return response
    
  def classify(self, term1, term2=None):
    if not term2:
      child = self.name
      parent = term1
    else:
      child = term1
      parent = term2
    child = utilities.sanitize(child)
    parent = utilities.sanitize(parent)
    if not self.isA(child, parent) and not parent.istitle():
      self.taxonomy.case_sensitive = True
      self.taxonomy.append(child, type=parent)
      self.taxonomy.case_sensitive = False
      
  def isA(self, term1, term2=None):
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
    if child.istitle() or parent.istitle():
      self.taxonomy.classifiers = []
      self.taxonomy.case_sensitive = True
    if not getattr(self, 'isVerb', False):
      existingParents = map(str, self.taxonomy.parents(child, recursive=True))
    else:
      existingParents = map(str, self.taxonomy.parents(child, recursive=True, pos='VB'))
    if child.istitle() or parent.istitle():
      self.taxonomy.classifiers.append(self.wordnetClassifier)
      self.taxonomy.case_sensitive = False
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
    

  

		