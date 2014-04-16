class Synonyms(dict):
	def equate(self, firstPhrase, *phrases):
		phraseSets = map(self.list, phrases)
		self[firstPhrase] = self.list(firstPhrase).union(*phraseSets)
		for phrase in self[firstPhrase]:
			self[phrase] = self[firstPhrase]
			
	def list(self, phrase):
		if phrase in self:
			return self[phrase]
		else:
			# Look for occurence in existing set
			for key in self:
				if phrase in self[key]:
					self[phrase] = self[key]
					return self[phrase]
			# No set found => Make one
			self[phrase] = {phrase}
			return self[phrase]
