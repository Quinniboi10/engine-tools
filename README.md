## Engine Tools
This repository aims to make chess engines easier to debug

### Requirements
For dependencies, see [requirements.txt](requirements.txt).

It is expected that all engines support the basic UCI spec, plus several non-standard commands as documented below.

For movegen related tests, the engine should respond to `perft/bulk <depth>` in the below format  
```
move1: <nodes>
move2: <nodes>
move3: <nodes>
<nodes> nodes <nps> nps
```

For search speed related tests, the engine should support standard OpenBench benchmarking, as shown below
```
$ ./Engine bench
<nodes> nodes <nps> nps
```

### Usage
When running tests, this harness uses 2 engines (both supporting the above spec), and compares their results. For CLI syntax, run `python3 main.py --help` for more information.

### Notes
Using the `bench` speedup test, the output format is `speed ± standard error`