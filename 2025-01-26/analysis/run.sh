#!/bin/sh

set -x

python 00_proc_bcm.py --experiment=exp03  --filename=RingBCM_250126_210451.txt
python 00_proc_bcm.py --experiment=exp04  --filename=RingBCM_250126_215255.txt

python 01_plot_profiles.py --experiment=exp03
python 01_plot_profiles.py --experiment=exp04
