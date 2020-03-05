# To run:
conda activate leader_selection
netconvert -c map.netc.cfg
sumo -c traffic.sumocfg
```bash
python main.py
```