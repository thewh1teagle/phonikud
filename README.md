# Setup

Install foma: `brew install foma`

# Running

Running:

```shell
foma -f phonikud.xfst
flookup -i phonikud.fst < inputs.txt | tee predictions.txt
```

```shell
foma -l phonikud.xfst
apply down
apply down> הַמָּלֵא
```

# Todo

- [ ] Handle [alphabetic presentation form block](https://en.wikipedia.org/wiki/Alphabetic_Presentation_Forms) -- add initial rule to xfst that normalizes them.