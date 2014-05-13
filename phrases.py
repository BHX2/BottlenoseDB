import os
import re
'''
BottlenoseDB / Phrases

Copyright 2014 Bharath Panchalamarri Bhushan

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

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
    if re.match('.*\*$', name.strip()):
      name = name[:-1]
    if not utilities.sanitize(name).istitle():
      type = utilities.sanitize(name).split()[-1]
    else:
      type = None
    Concept.__init__(self, name, type)

class Descriptor(Concept):
  def __init__(self, name):
    self.isVerb = False
    quantitative = re.search('^[0-9.]+', name)
    if not quantitative:
      quantitative = re.search('^-[0-9.]+', name)
    if quantitative:
      self.quantity = float(quantitative.group(0))
      self.isQuantity = True
      type = 'quantity'
    else:
      self.quantity = None
      self.isQuantity = False
      type = name
    Concept.__init__(self, name, type)