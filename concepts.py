import os
import re
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
      self.name = None
    if type: 
      self.classify(utilities.sanitize(self.name), utilities.sanitize(type))
    else:
      self.type = None
  
  def parents(self, name=None):
    if not name:
      names = self.synonyms()
    else:
      names = self.synonyms(name)
    response = set()
    for name in names:
      name = utilities.sanitize(name)
      if name.istitle():
        self.taxonomy.classifiers = []
        self.taxonomy.case_sensitive = True
      if not getattr(self, 'isVerb', False):
        response |= set(utilities.unicodeDecode(self.taxonomy.parents(name, recursive=False)))
      else:
        response |= set(utilities.unicodeDecode(self.taxonomy.parents(name, recursive=False, pos='VB')))
      if name.istitle():
        self.taxonomy.classifiers.append(self.wordnetClassifier)
        self.taxonomy.case_sensitive = False
    return response
    
  def ancestors(self, name=None):
    if not name: 
      names = self.synonyms()
    else:
      names = self.synonyms(name)
    response = set()
    for name in names:
      name = utilities.sanitize(name)
      if name.istitle():
        self.taxonomy.classifiers = []
        self.taxonomy.case_sensitive = True
      if not getattr(self, 'isVerb', False):
        response |= set(utilities.unicodeDecode(self.taxonomy.parents(name, recursive=True)))
      else:
        response |= set(utilities.unicodeDecode(self.taxonomy.parents(name, recursive=True, pos='VB')))
      if name.istitle():
        self.taxonomy.classifiers.append(self.wordnetClassifier)
        self.taxonomy.case_sensitive = False
    return response
    
  def descendants(self, name=None):
    if not name: 
      names = self.synonyms()
    else:
      names = self.synonyms(name)
    response = set()
    for name in names:
      name = utilities.sanitize(name)
      if name.istitle(): return
      if not getattr(self, 'isVerb', False):
        firstPass = utilities.unicodeDecode(self.taxonomy.children(name, recursive=False))
      else:
        firstPass = utilities.unicodeDecode(self.taxonomy.children(name, recursive=False, pos='VB'))
      for thing in firstPass:
        if utilities.sanitize(thing).istitle():
          continue
        else:
          response |= set(utilities.unicodeDecode(self.descendants(thing)))
      response |= set(firstPass)
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
      childTerms = self.synonyms()
      parent = term1
    else:
      childTerms = self.synonyms(term1)
      parent = term2
    existingParents = set()
    for child in childTerms:
      child = utilities.sanitize(child)
      parent = utilities.sanitize(parent)
      if child.istitle() or parent.istitle():
        self.taxonomy.classifiers = []
        self.taxonomy.case_sensitive = True
      if not getattr(self, 'isVerb', False):
        existingParents |= set(map(str, self.taxonomy.parents(child, recursive=True)))
      else:
        existingParents |= set(map(str, self.taxonomy.parents(child, recursive=True, pos='VB')))
      if child.istitle() or parent.istitle():
        self.taxonomy.classifiers.append(self.wordnetClassifier)
        self.taxonomy.case_sensitive = False
    for term in self.synonyms(parent):
      if term in existingParents:
        return True
    return False

  def equate(self, *phrases):
    if self.name: 
      if not re.match('^unspecified', self.name):
        phrases += (self.name,)
    phrases = map(utilities.camelCase, phrases)
    phraseSets = map(self.synonyms, phrases)
    mergedSet = set.union(*phraseSets)
    for phrase in mergedSet:
      self.thesaurus[phrase] = mergedSet
      
  def synonyms(self, phrase=None):
    if not phrase:
      if not self.name:
        return None
      else:
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
    

  

		