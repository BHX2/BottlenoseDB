import re
import string

def camelCase(text):
  isNegative = re.match('^!', text)
  words = text.replace("'s", "s").translate(string.maketrans(string.punctuation, ' '*len(string.punctuation))).split()
  response = words.pop(0)
  if isNegative:
    response = '!' + response
  for word in words:
    response += word.capitalize()
  return response
  
def unCamelCase(text):
  text = re.sub("([A-Z0-9]*)([A-Z][a-z0-9]+)","\g<1> \g<2>", text)
  text = re.sub("([a-z0-9])([A-Z])","\g<1> \g<2>", text).strip()
  if text.istitle():
    return text
  else:
    words = text.split()
    response = words.pop(0)
    for word in words:
      if word.isupper():
        response += (' ' + word)
      else:
        response += (' ' + word.lower())
    return response