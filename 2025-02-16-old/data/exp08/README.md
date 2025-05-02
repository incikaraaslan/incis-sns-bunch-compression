# Experiment 08


## Description

We tested an idea to increase the beam current limit during accumulation and effectively increase the h=1 ramp time during storage. The idea is to accumulate with Cav01 and Cav02 at equal h=1 amplitude but 180 deg separation in phase during accumulation. The hope is that the cavities will work together to give a very small voltage during accumulation. Then we turn off Cav02 (which we can do instantly during the cycle) after accumulation, leaving only the h=1 cavity.


## Details

- Set PWON = 36.
- Set injected turns = 100.
- Set stored turns = 900.
- Set Cav01 voltage = 5 [kV].
- Set Cav02 voltage = 5 [kV].
- Set Cav01 phase = 118 [deg] (nominal).
- Set Cav02 phase = 100 [deg] (nominal).
- Set Cav03 short=True.
- Set Cav04 short=True.

Case 01: Baseline.
Case 02: Set Cav02 phase = -80 [deg].
Case 03: Turn off Cav02 after 100 injected turns.
Case 04: Turn off Cav02 after 10 injected turns.

