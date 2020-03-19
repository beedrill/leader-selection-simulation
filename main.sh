for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm basic --trials 10 --channel_condition ideal --stable_period 0.1  --car_flow $FLOW --heartbeat_factor 2 --saving_file_name basic_ideal_stableperiod_0.1_heartbeat_2.csv
done

for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.1  --car_flow $FLOW --heartbeat_factor 2 --saving_file_name advanced_ideal_stableperiod_0.1_heartbeat_2.csv
done

for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.2  --car_flow $FLOW --heartbeat_factor 2 --saving_file_name advanced_ideal_stableperiod_0.2_heartbeat_2.csv
done

for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.4  --car_flow $FLOW --heartbeat_factor 2 --saving_file_name advanced_ideal_stableperiod_0.4_heartbeat_2.csv
done

for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.1 --explicit_leader_switch  --car_flow $FLOW --heartbeat_factor 2 --saving_file_name advanced_ideal_leaderSwitch_stableperiod_0.1_heartbeat_2.csv
done

for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.2 --explicit_leader_switch  --car_flow $FLOW --heartbeat_factor 2 --saving_file_name advanced_ideal_leaderSwitch_stableperiod_0.2_heartbeat_2.csv
done

for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.4 --explicit_leader_switch  --car_flow $FLOW --heartbeat_factor 2 --saving_file_name advanced_ideal_leaderSwitch_stableperiod_0.4_heartbeat_2.csv
done

for FLOW in 0.25 0.35 0.45 0.55 0.65 0.75 0.85 1
do  
python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.1  --car_flow $FLOW --heartbeat_factor 2 --optimize_backward_msg_propagation --saving_file_name advanced_ideal_stableperiod_0.1_optBack_heartbeat_2.csv
done

