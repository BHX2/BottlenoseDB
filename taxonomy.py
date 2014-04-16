from pattern.search import Taxonomy as PatternTaxonomy
from pattern.search import WordNetClassifier

class Taxonomy:
	def __init__(self):
		self.patternTaxonomy = PatternTaxonomy()
		self.patternTaxonomy.classifiers.append(WordNetClassifier())
		
	def parents(self, type):
		return self.sanitize(self.patternTaxonomy.parents(type))
		
	def children(self, type):
		return self.sanitize(self.patternTaxonomy.children(type))
		
	def classify(self, child, parent):
		if not self.test(child, parent):
			self.patternTaxonomy.append(child, type=parent)
		
	def test(self, child, parent):
		existingParents = map(str, self.patternTaxonomy.parents(child, recursive=True))
		return parent in existingParents
		
	def sanitize(self, patternArray):
		patternStrings = map(str, patternArray)
		# TODO: convert to camelCase
	