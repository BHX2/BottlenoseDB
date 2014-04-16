class Synonyms(dict):
	def equate(self, firstPhrase, *phrases):
		firstPhraseList = self.list(firstPhrase)
		phraseLists = map(self.list, phrases)
		# Merge all phrases into first phrase's list
		for list in phraseLists:
			for phrase in list:
				if phrase not in firstPhraseList:
					firstPhraseList.append(phrase)
		# Point all phrases to the updated list
		for phrase in firstPhraseList:
			self[phrase] = firstPhraseList
			
	def list(self, phrase):
		# Make a new list if new phrase
		if phrase not in self:
			self[phrase] = [phrase]
		# Prepare list response	
		listToReturn = self[phrase]
		listOfListsWithPhrase = [listToReturn]
		# If the search comes back unexpectedly everything will need to be standardized
		fuckeryAfoot = False
		# Look for occurence in existing list
		for key in self:
			if phrase in self[key]:
				if self[key] not in listOfListsWithPhrase:
					# If another list has this phrase in it...
					fuckeryAfoot = True
					listOfListsWithPhrase.append(self[key])
					for synonym in self[key]:
						if synonym not in listToReturn:
							listToReturn.append(synonym)
		if fuckeryAfoot:
			for phrase in listToReturn:
				self[phrase] = listToReturn
		return listToReturn