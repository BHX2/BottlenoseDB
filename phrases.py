import os
import re
from pattern.en import conjugate
from pattern.en import singularize
from concepts import Concept
import utilities

class VerbPhrase(Concept):
  def __init__(self, name=None, type=None):
    self.isVerb = True
    self.type = utilities.camelCase(type)
    self.name = self.type + '_' + os.urandom(5).encode('hex').lower()
    broaderVerb = str(utilities.sanitize(type).split()[0])
    #self.type = str(conjugate(utilities.sanitize(type).split()[0], aspect='progressive'))
    self.classify(utilities.sanitize(self.name), self.type)
    self.classify(self.type, broaderVerb)
	
class NounPhrase(Concept):
  def __init__(self, name=None, type=None):
    self.isVerb = False
    if not type and not utilities.sanitize(name).istitle():
      type = str(singularize(utilities.sanitize(name).split()[-1]))
    Concept.__init__(self, name, type)

class Descriptor(Concept):
  def __init__(self, name=None, type=None):
    if name:
      quantitative = re.search('(^[0-9.]+)(.*)', name)
    if quantitative:
      self.quantity = float(quantitative.group(1))
      self.units = quantitative.group(2) if quantitative.group(2) else None
      self.isQuantity = True
    else:
      self.quantity = None
      self.units = None
      self.isQuantity = False
    self.isVerb = False
    Concept.__init__(self, name, type)