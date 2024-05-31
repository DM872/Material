Data and Readers for post-enrollment exam scheduling.


To run the readers execute from this directory:
```
python3 src/main.py data/F23/biologi.json -o output_file
```

or:

```
python3 src/main.py -h
```

## Verifier

```
python ../src/verifier.py -a F23/solution.json F23/all.json -o .
```

For the documentation of the input data see the readme file inside `data/`.