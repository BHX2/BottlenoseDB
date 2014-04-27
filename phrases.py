import os
import re
from pattern.en import conjugate
from pattern.en import singularize
from concepts import Concept
import utilities

class VerbPhrase(Concept):
  def __init__(self, name):
    self.isVerb = True
    type = str(utilities.sanitize(name).split()[0])
    Concept.__init__(self, name, type)
	
class NounPhrase(Concept):
  def __init__(self, name):
    self.isVerb = False
    if not utilities.sanitize(name).istitle():
      type = str(singularize(utilities.sanitize(name).split()[-1]))
    else:
      type = None
    Concept.__init__(self, name, type)

class Descriptor(Concept):
  def __init__(self, name):
    self.isVerb = False
    quantitative = re.search('(^[0-9.]+)(.*)', name)
    if quantitative:
      self.quantity = float(quantitative.group(1))
      self.units = quantitative.group(2) if quantitative.group(2) else None
      self.isQuantity = True
      type = 'quantity'
    else:
      self.quantity = None
      self.units = None
      self.isQuantity = False
      type = 'quality'
    Concept.__init__(self, name, type)