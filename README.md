#Bottlenose
Bottlenose is a platform for building artificially intelligent programs. The engine is written in Python and uses a simple scripting language to streamline communication of logic while allowing compensation for robust natural language vocabularies.

###Synonyms
Use `~` to indicate synonymous words or phrases. Multiple synonyms can be defined at once if seperated by commas. All phrases should be written in *camelCase* such that spaces are removed between words, the first word is in all lower case, and all subsequent words are capitalized; capitilazation of proper nouns and acronyms can be preserved. Examples: *houseCat*, *Garfield*, *LOLCat*. In general the singular form of noun phrases should be used. Also, all punctuation including single-quotes should be omitted.
```
cat ~ kitty, feline
```

###Taxonomy
Use `=/` to indicate an *is-a-type-of* relationship. Alternatively use `/=` to indicate the converse relationship. 
```
cat =/ mammal
animal /= mammal
```

Both taxonomy and synonyms are applied universally to all language expressed thereafter rather than being pinned down to individual instances. The following scripting elements apply to particular instances of concepts.

###Components / Relationships
Use `.` to indicate the existence of a component or relationship. This can be paired with `=` to assign the role to a single entity or with `+=` to add a relationship that is not exclusively singular. In the latter case multiple relationships can be added at once using commas to delimit a list of concepts. Both the component/relationship and any assigned entities should be noun phrases. If the attribute is in the form of a verb phrase use **Actions** as described below. Again note that all phrases should be singular.
```
cat.owner = John
cat.favoriteFood += tuna, catnip, oatmeal
```

###Actions
Use `.` followed by a verb phrase and parentheses to indicate an action. All verb phrases should be affirmative and in the present tense. Comma-seperated direct objects may be placed within the parentheses. In order to indicate a negative verb phrase `!` should be prefixed before the direct object rather than introducing negatives alongside the verb component. To indicate the complete termination of an action with or without direct objects `!` should be placed alone within the parantheses
```
cat.sleeps()
cat.sleeps(!)
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

###Queries
Bottlenose also allows for concepts (specifically those expressed via noun phrases) to be queried. Queries are denoted with a preceding `?` (query operator). Queries can be used anywhere a concept is used; they can also be used on their own to inspect conceptual instances from the command-line interface (as shown in the below example). A basic query can be a noun phrase alone or a component (in which case the component rather than the parent concept is returned). Within a **Statement** or **Clause** these basic queries function the same as their counterparts without `?`; thus, their primary utility is inspection from command-line. More complex queries allow one to filter by state using the appropriate **State** expression with preceding `?`. To filter to subjects associated with a particular verb (with or without direct-object as additional filtering criteria) simply use the query operator before a normal **Action** expression. If the subject and `.` are omitted (to leave only verb, parentheses, and direct object) then the query returns direct objects. Queries are particularly useful within **Clauses** (described below) to narrow down concepts before asserting statements. Of note, negatives (`!`) cannot be used within queries.
```
?cat

  cat (03da1ffedb)
    cat is a mammal, cat
    cat is also known as: feline, kitty
    cat is furry
    cat (has favoriteFood) --> oatmeal
    cat (has whisker) --> unspecifiedWhisker
    cat (has favoriteFood) --> tuna
    cat (has fur) --> unspecifiedFur
    cat (has favoriteFood) --> catnip
    cat (has owner) --> John
    cat (eats) --> mouse
    cat (plays with) --> yarn

?cat.owner

  John (9d39a2110d)
    cat (has owner) --> John

?eats(mouse)

  mouse (b1d350ffaa)
    mouse is a mouse
    cat (eats) --> mouse
```

In the above example one may have noticed the hexadecimal strings beside concept names (ex: `03da1ffedb`). These are hashcodes for the individual instances and can be used in place of noun phrase concepts in expressions. They are useful in command-line in certain circumstances where multiple conceptual instances with the same name exist; however, they should never be used within **Clauses** becaues of their ephemeral nature.

###Instantiation
By default all concepts are assumed to be previously mentioned entities; this is similar to a default definite article (*the*). If no appropriate entities are found then a new instance may be created to fulfill an assertion. If multiple instances of an entity exist then Bottlenose will look for the most recent reference within the context. However, to indicate that a concept is new (even when a similar concept exists) place an `*` directly after the concept phrase. This functions similarly to an indefinite article (*a* or *an*). In the below example the use of `*` indicates that the mouse referenced is a new mouse (not the one from the **Actions** example that is being eaten by the cat).
```
mouse*.eats(cheese)
```

###Rules & Clauses
The real power of Bottlenose is derived from leveraging the "semantic glue" described above in forming dynamic artificial cognitive beliefs. Each **Belief** is made up of **Clauses**, which are testable statements referencing existence of a **Concept** or assertions of **Relationship**, **Action**, or **State**. The weakest type of **Belief** is a **Rule**. A Bottlenose **Rule** is not a rule in a  strict sense; it does not have to be correct all the time and there need not be any true causation, or temporal seperation. Instead, its purpose is to describe a reflexive cognitive association or potential co-occurence. Each **Rule** follows the syntax of two **Clauses** seperated by `>>`. `A >> B` denotes *if A then B is more likely*. Unlike **Laws** described below, the dependent clause (B in this example) is not asserted. Instead the possibility is introduced and accessible via querying with a number indicating summation of evidence.
```
cat.speaks() >> cat=/LOLCat
LOLCat.speaks(comment) >> comment#misspelled
```

###Logic
A **Compound Clause** can be formed using `&` (*AND*) or `|` (*OR*) to join multiple simple **Clauses**. To supply a negative, `!` (*NOT*) can prefix a component **Clause**. `&` indicates that in order to fulfill the entire **Clause**, expressions on both sides of the `&` must be true. `|` indicates that only one **Clause** needs to be true. If the dependent **Clause** is multi-part comma-delimitation can be used.
```
cat & laserPointer >> cat.chases(laserPointer)
LOLCat | grumpyCat | nyanCat | keyboardCat >> computerScreen.displays(cat)
cat.location=home >> cat.sleeps(), cat.eats(), cat.plays(), cat.chills()
```

Of note, Bottlenose allows for robust contextual co-referencing exemplified in the middle example above. The entity (*cat*) referenced within a **Clause** is preferentially assumed to be a reference to a suitable entity (*LOLCat, grumpyCat, nyanCat, keyboardCat*) within the given **Rule** context (even if the reference is not identical).

###Laws
The strongest **Belief** is a **Law**, which is a strict correlation indicated using `>>>`. In general `A >>> B` translates *if A is true then B is ALWAYS true.* One use of **Laws** is to hardcode more 'syntactic glue' than is otherwise available. Using the cat example above we can connect the **Action** of 'owning a cat' to the **Relationship** of 'cat having an owner'. Below, we equate the **Action** `.owns(X)` to the **Relationship** `.owner =X`. Of importance, **Laws** are immediately computed into the artificial cognitive model. 
```
cat.owner=person >>> person.owns(cat)
```

###Arithmetic
In order to describe slightly more complex patterns there are a few operators that can be used to describe basic arithmetic (addition, subtraction). The same convention can be applied to a **Component**. Units can be typed directly after the number(s) (without intervening spaces). A simple arithmetic operation is defined with `+` or `-` followed by a quantity. Also of note, trigger (in)equalities can be indicated within a **Clause** using `>`, `<`, `<=`, `>=`, or `==`. 
```
cat.weight#10lbs
cat.eats(quarterPounderCheeseBurger) >> cat.weight+0.25lbs

cat.weight > 20lbs >> cat#fat
cat.weight <= 5lbs >> cat#skinny
```

---
###Roadmap

1. Design system for storing and dynamically testing **Clauses** with contextual accuracy
2. Design system for tracking and inspecting potentiations/evidence
3. Implement arithmetic expressions (along with comparison operators and possibly equations)
4. Implement persistence via pickling as well as export/import to plain text files
5. Implement tabbed autocompletion using *(py)readline* & *rlcompleter*
6. Polish CLI interface: add intro, help, colors, tables, benchmarks, etc
7. Implement logging, data backup, and undo functionality within
8. Experiment with rule-based artificial cognition