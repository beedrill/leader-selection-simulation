FOR %%G in (0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 1) DO (
    python runner.py --algorithm advanced --trials 10 --channel_condition ideal --stable_period 0.4  --car_flow %%G --heartbeat_factor 2 --saving_file_name advanced_ideal_stableperiod_0.4_heartbeat_2.csv
)
