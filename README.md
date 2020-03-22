# Simulation of leader selection algorithm for vehicular ad-hoc network:
This is the simulation for leader selection algorithm, to see more details on the algorithm, visit the paper:
https://arxiv.org/abs/1912.06776

# Citing
To cite the paper, use this Bibtex:
```
@inproceedings{zhang2019leader,
  title={VLeader selection in Vehicular Ad-hoc Networks: a Proactive Approach},
  author={Zhang, Rusheng and Jacquemot, Baptiste and Bakirci, Kagan and Bartholme, Sacha and Kaempf, Killian and Freydt, Baptiste and Montandon, Loic and Zhang, Shenqi and Tonguz, Ozan},
  booktitle={2020 IEEE 88th Vehicular Technology Conference (VTC-Fall)},
  year={2020},
  organization={IEEE}
}
```
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
- [SUMO](https://sumo.dlr.de/) version > 1.0
- __SUMO_HOME__ environment parameter specified correctly
- python packages: numpy, scipy, matplotlib, pandas, to install all required python packages, do:
```bash
pip install -r requirement.txt
```

# Execute
To execute the code, simply do:
```bash
python runner.py
```

Algorithm parameters can be specified, check:
```bash
python runner.py -h
```

# More details
You can specify how to run the algorithm in more details, check __multiMain.py__ for example, it contains an example of doing multiple simulations, retrieve usefule data and calculate the average

You write a batch script or bash script to use runner.py the way you want, check __main.sh__ and __main.bat__ for examples.