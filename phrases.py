import sys
import re
from pattern.en import conjugate
from pattern.en import singularize
sys.dont_write_bytecode = True
from concepts import Concept
import utilities

class VerbPhrase(Concept):
  def __init__(self, name=None, type=None):
    self.isVerb = True
    if not type:
      type = str(conjugate(utilities.sanitize(name).split()[0], aspect='progressive'))
    Concept.__init__(self, name, type)
	
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