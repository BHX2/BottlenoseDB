#Bottlenose
**Bottlenose** is a command-line program written in Python that allows a user to store semantic knowledge representations as a graph network. It uses a simple scripting language for data entry called **Cogscript** that helps the program understand more complex patterns that utilize non-uniform terminology. The most basic operations are as follows:

###Synonyms
Use `=` to indicate synonymous words or phrases. Multiple synonyms can be defined at once if seperated by commas. All phrases should be written in *camelCase* such that spaces are removed between words, the first word is in all lower case, and all subsequent words are capitalized; capitilazation of proper nouns and abbreviations can be preserved. Examples: *houseCat*, *Garfield*, *LOLCat*. When possible the singular form of noun phrases should be used. Also, all punctuation including single-quotes should be omitted.
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
Use `#` followed by an adjective to indicate the state of the entity or a component entity. If the right-sided phrase is a noun phrase it should be instead assigned as a **Component** (shown above). For plural items a number can be placed after `#` and used as if the number were an adjective.
```
cat#furry
cat.fur#orange
cat.whiskers#long
```

---
###Rules & Clauses
The real power of Bottlenose is derived from leveraging the "semantic glue" described above in forming dynamic artificial cognitive behaviors. A Cogscript **Rule** is not a rule in a  strict sense; it does not have to be correct all the time and there need not be any true causation, directionality, or temporal seperation. Instead, its purpose is to describe a reflexive cognitivie association or general correlation. Each **Rule** follows the syntax of two **Clauses** seperated by `>>`. A **Clause** can be a plain-phrase denoting existence of a concept, or a **Relationship** assertion, **Action**, or **State**. 

```
cat.speaks() >> cat.grammar=bad
```

A **Compound Clause** can be formed using `&` (*AND*), `,` (*INCLUSIVE OR*), and `|` (*EXCLUSIVE OR*). The `&` would indicate that in order to fulfill the entire **Clause**, statements of both sides of the `&` must be true. Differentiating the utility of `,` and `|` is more intricate. One can think of the `,` as expanding into two rules. An example clause `A >> B , C` can be thought of as `A >> B` (*if A is true, then B could be true*) and `A >> C` (*if A is true, then C could be true*). Contrarily, the statement `A >> B | C` might translate *if A is true, then either B or C could be true, but it is unlikely that B and C would be simultaneously true*. 

```
cat & laserPointer >> cat.chase(laserPointer)
```

If a **Rule** is more meaningful and/or directional, then there is additional syntax that can be added. To denote the first clause supporting or opposing the second clause `>>+` or `>>-` can be used respectively. For example `A >>+ B` might be translated *if A is true, then it is more likely that B is true*. `A >>- B` might be translated *if A is true, then it is less likely that B is true*. 

```
cat#hungry >>+ cat.plays()
cat#old >>- cat.plays()
```

To take things even further quantitative probabilities can be expressed. The probability of the second *Clause* given the truth of the first *Clause* can be assigned a numerical value between 0.0 (never co-occurs) and 1.0 (always co-occurs). This value would be placed between brackets, which is itself placed immediately behind the dependent/second **Clause**. 

```
coin.flips() >> coin#heads[0.5] | coin#tails[0.5]
magiciansCoin.flips() >> magiciansCoin#heads[1] | magiciansCoin#tails[0]
```

Another use of **Rules** is to hardcode more 'syntactic glue' than is available by default. Using the cat example above we can connect the **Action** of 'owning a cat' to the **Relationship** of 'cat having an owner'. Below, we equate the **Action** `.owns(X)` to the **Relationship** `.owner =X`. Note that because of the directionality imposed by introducing quantitative probability, two statements are neccesary to fully describe the concept. 

```
cat.owner=person >> person.owns(cat)[1.0]
person.owns(cat) >> cat.owner=person[1.0]
```

###Arithmetic
In order to describe slightly more complex patterns there are a few operators that can be used to describe basic arithmetic (addition, subtraction). The same convention can be applied to a **Component**. A range of values can be described by writing two numbers seperated by `-`. Units can be typed directly after the number(s) (without intervening spaces). When describing an arithmetic operation within a **Rule**, `++` or `--` should be placed after a **Component**. If a particular value for the operation is being defined then it should follow a single `+` or `-`. Also of note, trigger (in)equalities can be indicated within a **Clause** using `>`, `<`, `<=`, `>=`, or `==`. 

```
cat.weight#10lbs

cat.eats(iceCream) >> cat.weight++
cat.eats(quarterPounder) >> cat.weight+0.25lbs
cat.walks() >> cat.weight--

cat.weight > 20lbs >> cat#fat
cat.weight <= 5lbs >> cat#skinny
```