import sys
sys.dont_write_bytecode = True
# Keeps directory clean by not compiling utilities to bytecode

import utilities

class Synonyms(dict):
	def equate(self, *phrases):
		phrases = map(utilities.camelCase, phrases)
		phraseSets = map(self.list, phrases)
		mergedSet = set.union(*phraseSets)
		for phrase in mergedSet:
			self[phrase] = mergedSet
			
	def list(self, phrase):
		phrase = utilities.camelCase(phrase)
		listOfSetsWithPhrase = []
		for key in self:
			if phrase in self[key]:
				if self[key] not in listOfSetsWithPhrase:
					listOfSetsWithPhrase.append(self[key])
		if len(listOfSetsWithPhrase) == 0:
			self[phrase] = {phrase}
		elif len(listOfSetsWithPhrase) > 1 or phrase not in self:
			mergedSet = set.union(*listOfSetsWithPhrase)
			for element in mergedSet:
				self[element] = mergedSet
		return self[phrase]
