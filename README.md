# Monte-Carlo Monolayer Hashing Simulation

N.B.: This was written in 2012 and probably for Python 2.7, possibly 2.4. To get this to work in Python 3.7 may require some work.

N.B.: If there is a significant rewrite of this, I would recommend porting over to the [Bazel](https://bazel.build/) build system.

This is a Monte Carlo simluation for predicting the hashing patterns of nanoparticles deposited on a Langmuir trough.

The simulation is invoked via `./hash.py -h`.

When running with SGE (queueing supercomputers), invoke the simulation via `qsub wrap.sh`. See http://bit.ly/Hz7XTv, http://bit.ly/H3L7TA, http://bit.ly/H1FUy4.

```
prof/
        timing profiles
logs/
        simulation logs
lib/
        library calls
classes/
        classes
```

Sample calls:

```
./hash.py -m sim -c default.conf
./hash.py -m sim -c logs/<simulation>/config.conf -g logs/<timestamp>/<simulation>.txt
./hash.py -m ren -g logs/<simulation>/<step>.txt -c logs/<simulation>/config.conf
./hash.py -m lyz -g logs/<simulation>/<step>.txt
./hash.py -m log -d logs/
```

Output:

```
config.conf
        experimental constants
analysis.txt
        simulation analysis
<step>.txt
        simulation grid at <step> step
```

- Minke (minke.zhang@gmail.com)
