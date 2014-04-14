#Bottlenose
**Bottlenose** is a command-line program written in Python that allows a user to store semantic knowledge representations as a graph network. It uses a simple scripting language for data entry called **Cogscript** that helps the program understand more complex patterns that utilize non-uniform terminology. The most basic operations are as follows:

###Synonyms
Use `=` to indicate synonymous words or phrases. Multiple synonyms can be defined at once if seperated by commas. All phrases should be written in *camelCase* such that spaces are removed between words, the first word is in all lower case, and all subsequent words are capitalized; capitilazation of proper nouns and abbreviations can be preserved. Examples: *houseCat*, *Garfield*, *LOLCat*. When possible the singular form of noun phrases should be used.
```
cat = kitty, feline
```

###Taxonomy
Use `=/` to indicate an *is-a-type-of* relationship. Alternatively use `/=` to indicate the converse relationship. 
```
cat =/ mammal
```
OR
```
mammal /= cat
```

###Components / Relationships
Use `.` to indicate the existence of a component or relationship. This can be paired with `=` to assign the role. Both the component/relationship and any assigned entities should be noun phrases. If the attribute is in the form of a verb phrase use **Actions** as described below.
```
cat.owner = John
```

###Actions
Use `.` followed by a verb phrase and parentheses to indicate an action. All verb phrases should be affirmative and in the present tense. Comma-seperated direct objects may be placed within the parentheses. In order to indicate a negative verb phrase `!` should be prefixed before the direct object rather than introducing negatives alongside the verb component.
```
cat.sleeps()
cat.eats(mouse)
cat.playsWith(yarn)
cat.likes(!dog)
```

###States
Use `#` followed by an adjective to indicate the state of the entity or a component entity. If the right-sided phrase is a noun phrase it should be instead assigned as a **Component** (shown above).
```
cat#furry
cat.fur#orange
cat.whiskers#long
```

---
###Behaviors
The real power of Bottlenose is leveraging the "semantic glue" described above into forming dynamic rules.

###Arithmetic
In order to describe slightly more complex patterns there are a few operators that can be used to describe basic arithmetic (addition, subtraction). As mentioned above, noun phrases should be written in singular form wherever possible. For plural items a number can be placed after `#` and used as if the number were an adjective. The same convention can be applied to a **Component**. A range of values can be described by writing two numbers seperated by `-`. Units can be typed directly after the number(s) (without intervening spaces). When describing an arithmetic operation within a **Behavior** `++` or `--` should be placed after a **Component**. If a particular value for the operation is being defined then it should follow a single `+` or `-`. Also of note, trigger (in)equalities can be indicated within behaviors by using a single `>`, `<`, `<=`, `>=`, `==`. 

```
cat.weight#10lbs

cat.eats(iceCream) >> cat.weight+
cat.eats(quarterPounder) >> cat.weight+0.25lbs
cat.walks() >> cat.weight-

cat.weight > 20lbs >> cat#fat
cat.weight <= 5lbs >> cat#skinny
```