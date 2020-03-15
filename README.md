# Simulation of leader selection algorithm for vehicular ad-hoc network:
This is the simulation for leader selection algorithm, to see more details on the algorithm, visit the paper:
https://arxiv.org/abs/1912.06776

# Citing
To cite this code, you can use the following bibtex:
```
@misc{leaderselectionrepo,
  author = {Rusheng Zhang and Baptiste Jacquemot},
  title = {Leader Selection Algorithm Repo},
  year = {2019},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/beedrill/leader-selection-simulation}},
}
```
# prerequisites
- SUMO version > 1.0
- __SUMO_HOME__ environment parameter specified correctly
- python packages: numpy, scipy, matplotlib, pandas

# Execute
To execute the code, simply do:
```bash
python runner.py
```

Algorithm parameters can be specified by checking:
```bash
python runner.py -h
```