#BottlenoseDB
BottlenoseDB is a database system for storing [conceptual knowledge](https://github.com/BHX2/BottlenoseDB/wiki/Why-BottlenoseDB%3F). The engine is written in Python and uses a simple scripting language to streamline communication of logic while allowing compensation for robust natural language vocabularies. The goal of BottlenoseDB is to bridge the gap between naturally (for humans) interdependent expressions of hierarchical verbal knowledge with the remarkable speed, accuracy, and persistence afforded by computers. BottlenoseDB can be used out-of-the-box via CLI.py (command-line interface) or imported as a module. The following is a guide to Bottlenose scripting syntax.

###Synonyms
Use `~` to indicate synonymous words or phrases. Multiple synonyms can be defined at once if seperated by commas. All phrases should be written in *camelCase* such that spaces are removed between words, the first word is in all lower case, and all subsequent words are capitalized; capitalization of proper nouns and acronyms can be preserved. Examples: *houseCat*, *Garfield*, *LOLCat*. In general the singular form of noun phrases should be used. Also, all punctuation including single-quotes should be omitted.
```
cat ~ kitty, feline
```

###Taxonomy
Use `=/` to indicate an *is-a-type-of* relationship. Alternatively use `/=` to indicate the converse relationship. Of note, everything is a `thing` by default.
```
cat =/ mammal
animal /= mammal
```

Both taxonomy and synonyms are applied universally to all language expressed thereafter (rather than being pinned down to individual instances). While it may seem tempting, neither synonym nor taxonomy operators should be introduced in conditional expressions because of this. 

###Components
Use `.` to indicate the existence of a **Component** (*has-a*) or other type of relationship. This can be paired with `=` to assign the role to a single entity or with `+=` to add an element to a relationship that is not exclusively singular. In the latter case, multiple relationships can be added at once using commas to delimit a list of concepts. Both the **Component** expression and any assigned entities should be noun phrases. If the attribute is in the form of a verb phrase use **Actions** as described below. Again note that all phrases should be singular. To remove an entity simply use `-=`.
```
cat.owner = John
cat.favoriteFood += tuna, catnip, oatmeal, grass
cat.favoriteFood -= grass
```

###Actions
Use `.` followed by a verb phrase and parentheses to indicate an action. All verb phrases should be affirmative and in simple present tense. Comma-seperated direct objects may be placed within the parentheses. In order to indicate a negative verb phrase `!` should be prefixed before the direct object rather than introducing negatives alongside the verb component. To indicate the complete termination of an action with or without direct objects `!` should be placed alone within the parantheses.
```
cat.sleeps()
cat.sleeps(!)
cat.chases(mouse)
cat.playsWith(yarn)
cat.likes(!dog)
```

###States
Use `#` followed by an adjective to indicate the state of an entity. If the right-sided phrase is a noun phrase it should be instead assigned as a **Component** (shown above). For plural items a number can be placed after `#` and used as if the number were an adjective. `!` prefix can be used to remove a previously asserted **State**.
```
cat#furry
cat.fur#orange
cat.whiskers#long
cat#!feral
```

###Queries
BottlenoseDB also allows for entities (specifically those expressed via noun phrases) to be queried. **Queries** start with a `?` (query operator) preceding a noun phrase (subject). This is followed by an optional **Clause** (see below for explanation) between parantheses which contains the said subject. In addition to allowing users to inspect instances, **Queries** can also be used anywhere a concept is used; however, an important consideration is that they do not follow co-reference resolution rules and thus do not function intuitively within **Beliefs** (also explained below).
```
?cat
 
cat (dc075eb396)
  cat is also known as: feline, kitty
  cat is a mammal
  cat is furry
  cat (has owner) --> John
  cat (has whiskers) --> whiskers
  cat (has fur) --> fur
  cat (has favoriteFood) --> tuna
  cat (has favoriteFood) --> catnip
  cat (has favoriteFood) --> oatmeal
  cat (playsWith) --> yarn
  cat (chases) --> mouse

?owner(cat.owner)

John (68249422ec)
  cat (has owner) --> John

?mouse(thing.chases(mouse))

mouse (589fbb56d6)
  cat (chases) --> mouse

```
In the above example one may have noticed the hexadecimal strings beside concept names (ex: `03da1ffedb`). These are hashcodes for the individual instances and can be used in place of noun phrase in expressions. They are useful in command-line in circumstances where multiple conceptual instances with the same name exist; however, they should never be used within **Clauses** becaues of their ephemeral nature.

###Instantiation
By default all concepts are assumed to be previously mentioned entities; this is similar to a default definite article (*the*). If no appropriate entities are found then a new instance may be created to fulfill an assertion. If multiple instances of a referenced concept exist then BottlenoseDB will look for the most recent co-reference within the context. However, to indicate that a concept is new (even when a similar concept exists) place an `*` directly after the concept phrase. This functions similarly to an indefinite article (*a* or *an*). In the below example the use of `*` indicates that the mouse being referenced is a new mouse (not the one from the **Actions** example that is being chased by the cat).
```
mouse*.eats(cheese)
```

###Rules & Clauses
The real power of BottlenoseDB is derived from leveraging the "semantic glue" described above in forming dynamic artificial cognitive beliefs. Each **Belief** is made up of **Clauses**, which are testable statements referencing existence of a **Concept** or assertions of **Component**, **Action**, or **State**. A **Rule** follows the syntax of two **Clauses** seperated by `>>`. `A >> B` denotes *if A then B*. The second (or dependent) **Clause** is executed immediately after the first is found to be true. BottlenoseDB automatically finds and tests relevant **Rules** that have been described previously, and attempts co-reference resolution. One use of **Rules** is to hardcode more "semantic glue" than is otherwise available. Using the cat example above, we can connect the **Action** of 'owning a cat' to the **Component** relationship of 'cat having an owner'. Of note, **Beliefs** are not applied to anything asserted before codifying of said **Belief** (so they are best described first).
```
cat.owner=thing >> thing.owns(cat)
```

###Logic
A **Compound Clause** can be formed using `&` (*AND*) or `|` (*OR*) to join multiple simple **Clauses**. To supply a negative, `!` (*NOT*) can prefix a component **Clause**. `&` indicates that in order to fulfill the entire **Clause**, expressions on both sides of the `&` must be true. `|` indicates that only one **Clause** need to be true. Multiple operators may be used in which case they will be tested correctly according to order of binary operations. **Compound Clauses** do not make use of co-reference resolution and as such terms are kept at their nonspecific values.
```
cat & laserPointer >> cat.chases(laserPointer)
cat#relaxed | cat#stressed >> cat.purrs()
```

###Evidence
The second type of **Belief** is called an **Evidence**. While **Rules** represents definitive facts that can be taken at face value, **Evidence** is used to describe shifts of confidence or opinion that is fuzzy and unstable. They are seperate from the solidified knowledge model and exist in a "potential space" that cannot trigger other **Rules**, etc. **Evidence** is useful for keeping numerical tally representing summed support and opposition of an assertion. This number can be inspected via queries. The adapter symbols denoting support and opposition are `>>+` and `>>-` respectively.
```
cat.sunbathes() >>+ cat#happy
cat#wet >>- cat#happy
```

###Arithmetic
In order to describe slightly more complex patterns there is also syntax to carry out basic arithmetic operation (addition, subtraction, multiplication, and division). As described above, numbers can be applied as **States**. These values can be adjusted using `+`, `-`, `/`, or `*` followed by a number. Quantitative concepts can also be described using equations by encapsulating an arithmetic equation within `eq[` and `]`. BottlenoseDB dynamically assigns and updates these values (however both variables must already exist).
```
eq[Whiskers.age = Henry.age + 2]
Henry.age#14
Whiskers.age
?age(Whiskers.age)

age (9133b8a437)
  age is 16.0
  Whiskers (has age) --> age

Henry.age+1
?age(Whiskers.age)

age (9133b8a437)
  age is 17.0
  Whiskers (has age) --> age
```
Finally, trigger (in)equalities can function as a **Clause** using `>`, `<`, `<=`, `>=`, or `==`. Arithmetic should not be mixed in dependent *Clauses* of **Evidence** beliefs (but can be used within **Rules**)
```
cat.eats(thirtyPoundCheeseBurger) >> cat.weight+30
cat.weight > 20 >> cat#fat
cat.weight <=5 >> cat#skinny
cat.weight#10
?weight(cat.weight)

weight (5bf537c7f5)
  weight is 10
  cat (has weight) --> weight

cat.eats(thirtyPoundCheeseBurger)
?weight(cat.weight)

weight (5bf537c7f5)
  weight is 40.0
  cat (has weight) --> weight
  
?cat

cat (8ba03d85c9)
  cat is fat
  cat (has weight) --> weight
  cat (eats) --> thirtyPoundCheeseBurger
```

---
###Roadmap

1. Implement persistence via pickling as well as export/import to plain text files
2. Implement logging, data backup, and undo functionality
3. Experiment with rule-based artificial cognition
4. More rigorous testing and benchmarking