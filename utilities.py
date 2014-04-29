import re
import string

def camelCase(text):
  isNegative = re.match('(^!)(.*)', text)
  if isNegative:
    text = isNegative.group(2)
  response = ''
  isQuantitative = True if re.search('(^[0-9.]+)(.*)', text) else False
  if isQuantitative:
    quantity = re.search('(^[0-9.]+)(.*)', text).group(1)
    text = re.search('(^[0-9.]+)(.*)', text).group(2)
    response += quantity
  words = text.replace("'s", "s").translate(string.maketrans(string.punctuation, ' '*len(string.punctuation))).split()
  if words: response += words.pop(0)
  if isNegative:
    response = '!' + response
  for word in words:
    response += word.capitalize()
  return response
  
def unCamelCase(text):
  isNegative = re.match('(^!)(.*)', text)
  if isNegative:
    text = isNegative.group(2)
  response = ''
  isQuantitative = True if re.search('(^[0-9.]+)(.*)', text) else False
  if isQuantitative:
    quantity = re.search('(^[0-9.]+)(.*)', text).group(1)
    text = re.search('(^[0-9.]+)(.*)', text).group(2)
    response += quantity
  text = re.sub("([A-Z0-9]*)([A-Z][a-z0-9]+)","\g<1> \g<2>", text)
  text = re.sub("([a-z0-9])([A-Z])","\g<1> \g<2>", text).strip()
  if text.istitle():
    return (response + text)
  else:
    words = text.split()
    if words: response += words.pop(0)
    for word in words:
      if word.isupper():
        response += (' ' + word)
      else:
        response += (' ' + word.lower())
    if isNegative:
      response = '!' + response
    return response
 
def sanitize(text):
  result = unCamelCase(camelCase(text))
  return result
  
def unicodeDecode(patternUnicodeStrings):
  patternStrings = map(str, patternUnicodeStrings)
  return map(camelCase, patternStrings)