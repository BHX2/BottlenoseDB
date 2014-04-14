#Bottlenose
**Bottlenose** is a command-line program written in Python that allows a user to store semantic knowledge representations as a graph network. It uses a simple scripting language for data entry called **Cogscript**. The most basic operations are as follows:

1. **Synonyms**
```
cat = kitty, feline
```
2. **Taxonomy**
```
mammal /= cat
```
OR
```
cat =/ mammal
```
3. **Components / Relationships**
```
cat.owner = John
```
4. **Actions**
```
cat.eats(mouse)
```

4. **States**
```
cat#lazy
cat.fur#orange
cat.whiskers#long
```
