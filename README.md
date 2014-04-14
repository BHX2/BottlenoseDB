#Bottlenose
**Bottlenose** is a command-line program written in Python that allows a user to store semantic knowledge representations as a graph network. It uses a simple scripting language for data entry called **Cogscript**. The most basic operations are as follows:

##Synonyms
Use *=* to indicate synonymous words or phrases which can be seperated by commas. 
```
cat = kitty, feline
```
##Taxonomy
Use *=/* to indicate an *'is a type of'* relationship. Alternatively use */=* to indicate the reverse relationship (*includes*). 
```
cat =/ mammal
```
OR
```
mammal /= cat
```
##Components / Relationships
Use *.* to indicate the existence of a component or relationship. This can be paired with *=* to assign the role. Both the component/relationship or assigned entity should be noun phrases. If the attribute is in the form of a verb phrase use **Actions** as described below.
```
cat.owner = John
```

##Actions
Use *.* followed by a verb phrase and parenthesis to indicate an action. All verb phrases should be affirmative and in the present tense. Comma-seperated direct objects may be placed within the parens. In order to indicate a negative verb phrase *!* should be prefixed before the direct object rather than introducing negatives alongside the verb component.
```
cat.sleeps()
cat.eats(mouse)
cat.playsWith(yarn)
cat.likes(!dog)
```

##States
Use *#* followed by an adjective to indicate the state of the entity or a component entity. If the right-sided phrase is a noun phrase it should be assigned to a component via *=* as shown above.
```
cat#lazy
cat.fur#orange
cat.whiskers#long
```
