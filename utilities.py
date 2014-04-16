import re
import string

def camelCase(text):
	words = text.replace("'s", "s").translate(string.maketrans(string.punctuation, ' '*len(string.punctuation))).split()
	response = words.pop(0);
	for word in words:
		response += word.capitalize()
	return response