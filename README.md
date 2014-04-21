#Bottlenose
**Bottlenose** is a platform for building artificially intelligent programs. The engine is written in Python and uses a simple scripting language called **Cogscript** to streamline communication of logic while allowing compensation for robust natural language vocabularies.

###Synonyms
Use `=` to indicate synonymous words or phrases. Multiple synonyms can be defined at once if seperated by commas. All phrases should be written in *camelCase* such that spaces are removed between words, the first word is in all lower case, and all subsequent words are capitalized; capitilazation of proper nouns and acronyms can be preserved. Examples: *houseCat*, *Garfield*, *LOLCat*. When possible the singular form of noun phrases should be used. Also, all punctuation including single-quotes should be omitted.
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
Use `.` to indicate the existence of a component or relationship. This can be paired with `=` to assign the role. Both the component/relationship and any assigned entities should be noun phrases. If the attribute is in the form of a verb phrase use **Actions** as described below. Again note that all phrases should be singular.
```
cat.owner = John
cat.hobby = eating, sleeping, sunbathing
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
Use `#` followed by an adjective to indicate the state of the entity or a component entity. If the right-sided phrase is a noun phrase it should be instead assigned as a **Component** (shown above). For plural items a number can be placed after `#` and used as if the number were an adjective. `!` can denote the absence of a state. States (adverbs) can also be applied after actions.
```
cat#furry
cat.fur#orange
cat.whiskers#long
cat#!feral
```

---
###Rules & Clauses
The real power of Bottlenose is derived from leveraging the "semantic glue" described above in forming dynamic artificial cognitive beliefs. Each **Belief** is made up of **Clauses**, which ar testable statements referencing existence of a **Concept** or assertions of **Relationship**, **Action**, or **State**. The weakest type of **Belief** is a **Rule**. A Cogscript **Rule** is not a rule in a  strict sense; it does not have to be correct all the time and there need not be any true causation, directionality, or temporal seperation. Instead, its purpose is to describe a reflexive cognitive association or potential co-occurence. Each **Rule** follows the syntax of two **Clauses** seperated by `>>`.
```
cat.speaks() >> cat=/LOLCat
LOLCat.speaks(comment) >> comment#misspelled
```

####Logic
A **Compound Clause** can be formed using `&` (*AND*), `,` (*inclusive OR*), or `|` (*exclusive OR*) to join multiple simple **Clauses**. To supply a negative, `!` (*NOT*) can prefix a component **Clause**. `&` indicates that in order to fulfill the entire **Clause**, expressions on both sides of the `&` must be true. Selecting `,` versus `|` is a more intricate decision. One can think of a compound **Rule** with `,` as expanding into two **Rules**. As an example: `A >> B , C` can be thought of as `A >> B` (*if A is true, then B could be true*) and `A >> C` (*if A is true, then C could be true*). Contrarily, the statement `A >> B | C` might translate *if A is true, then either B or C could be true, but it is unlikely that B and C would be simultaneously true*.
```
cat & laserPointer >> cat.chases(laserPointer)
LOLCat, grumpyCat, nyanCat, keyboardCat >> computerScreen.displays(cat)
cat.location=home >> cat.sleeps() | cat.eats() | cat.plays() | cat.chills()
```

Of note, Cogscript allows for robust contextual co-referencing exemplified in the middle example above. The entity (*cat*) referenced within a **Clause** is preferentially assumed to be a reference to a suitable entity (*LOLCat, grumpyCat, nyanCat, keyboardCat*) within the given **Rule** context (even if the reference is not identical).

####Evidence
If a **Belief** is more significant then there is additional syntax that can be added to indicate **Evidence**. To denote that the **Clauses** mutually support or oppose each other `>>+` or `>>-` can be used respectively. For example: `A >>+ B` might be translated *if A is true, then it is more likely that B is true* and *if B is true, then it is more likely that A is true*. `A >>- B` might be translated *if A is true, then it is less likely that B is true* and *if B is true, then it is less likely that A is true*. 
```
cat#hungry >>+ cat.plays()
cat#old >>- cat.plays()
```

####Statistical Probability
To take things even further, quantitative probabilities can be expressed. The probability of the second **Clause** given the truth of the first **Clause** can be assigned a numerical value between 0.0 (never co-occurs) and 1.0 (always co-occurs). This value would be placed between brackets, which is itself placed immediately behind the dependent/second **Clause**. 
```
coin.flips() >> coin#heads[0.5] | coin#tails[0.5]
magiciansCoin.flips() >> magiciansCoin#heads[1.0] | magiciansCoin#tails[0.0]
```

####Laws
The strongest **Belief** is a **Law**, which is a strict bi-directional correlation indicated using `>>>`. In general `A >>> B` translates *if A is true then B is ALWAYS true. AND if B is true then A is ALWAYS true*. One use of **Laws** is to hardcode more 'syntactic glue' than is otherwise available. Using the cat example above we can connect the **Action** of 'owning a cat' to the **Relationship** of 'cat having an owner'. Below, we equate the **Action** `.owns(X)` to the **Relationship** `.owner =X`. Of importance, **Laws** are immediately computed into the artificial cognitive model. 
```
cat.owner=person >>> person.owns(cat)
```

###Arithmetic
In order to describe slightly more complex patterns there are a few operators that can be used to describe basic arithmetic (addition, subtraction). The same convention can be applied to a **Component**. Units can be typed directly after the number(s) (without intervening spaces). When describing an arithmetic operation within a **Rule**, `++` or `--` should be placed after a **Component**. If a particular value for the operation is being defined then it should follow a single `+` or `-`. Also of note, trigger (in)equalities can be indicated within a **Clause** using `>`, `<`, `<=`, `>=`, or `==`. 
```
cat.weight#10lbs

cat.eats(iceCream) >> cat.weight++
cat.eats(quarterPounder) >> cat.weight+0.25lbs
cat.walks() >> cat.weight--

cat.weight > 20lbs >> cat#fat
cat.weight <= 5lbs >> cat#skinny
```

---
###Roadmap

1. ~~Write grammar rules and JSON **Translator** class for parsing Cogscript (using *parsimonious*)~~
2. ~~Design **Concept** class with class methods and objects for keeping track of taxonomy & synonyms~~
3. ~~**Concept** subclasses include **NounPhrases**, **VerbPhrases**, **Descriptors**~~
4. Design **Context** class with graph instances and methods for several types of reference lookup 
5. Context graphs include **ComponentGraph**, **ActionGraph**, **RelationshipGraph**, **StateGraph**
6. Design **Clause** class with an instance method for *test()*
7. During instantiation a **Clause** calculates implicitly dependent **Clauses** and adds appropriate rules
8. Instances of **Clause** store a Cogscript JSON object & hashcode, truth status, threshold and likelihood
9. Design **Belief** class with dictionary of clauses and class methods for clause(), *add()* and *remove()*
10. **Belief** class also holds belief graphs include **RuleGraph**, **EvidenceGraph**, **LawGraph**
11. Design **Interpreter** class that takes in Cogscript JSON and alters data structures
12. When **Interpreter** is in *universal context* makes clauses on prototype objects when given statements
13. Design **BottlenoseController** class that interfaces with command-line input and Interpreter
14. Implement persistence via pickling within **BottlenoseController**
15. Implement export/import to plain text files organized within a folder tree within **BottlenoseController**
16. Implement tabbed autocompletion using *(py)readline* & *rlcompleter*
17. Polish CLI interface: add intro, help, colors, tables, benchmarks, etc
18. Design querying engine with associated additional grammar and interpreter 
19. Implement Cogscript logging, data backup, and undo functionality within **BottlenoseController**
20. Experiment with rule-based artificial cognition