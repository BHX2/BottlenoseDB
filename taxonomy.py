from pattern.search import Taxonomy as PatternTaxonomy
from pattern.search import WordNetClassifier

import sys
sys.dont_write_bytecode = True
# Keeps directory clean by not compiling utilities to bytecode

import utilities

class Taxonomy:
	def __init__(self):
		self.patternTaxonomy = PatternTaxonomy()
		self.patternTaxonomy.classifiers.append(WordNetClassifier())
		
	def parents(self, type):
		return self.sanitize(self.patternTaxonomy.parents(type))
		
	def children(self, type):
		return self.sanitize(self.patternTaxonomy.children(type))
		
	def ancestors(self, type):
		return self.sanitize(self.patternTaxonomy.parents(type, recursive=True))
		
	def descendants(self, type):
		return self.sanitize(self.patternTaxonomy.children(type, recursive=True))
		
	def classify(self, child, parent):
		if not self.test(child, parent):
			self.patternTaxonomy.append(child, type=parent)
		
	def test(self, child, parent):
		existingParents = map(str, self.patternTaxonomy.parents(child, recursive=True))
		return parent in existingParents
		
	def sanitize(self, patternUnicodeStrings):
		patternStrings = map(str, patternUnicodeStrings)
		return map(utilities.camelCase, patternStrings)
	