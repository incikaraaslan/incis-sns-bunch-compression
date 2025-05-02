#!/bin/sh

# Should replace this with python script...

set -x

# Process BCM data
python 00_proc_ring_bcm.py --experiment=exp01 --filename=ring_bcm/RingBCM_250216_104155.txt
python 00_proc_ring_bcm.py --experiment=exp02/case01 --filename=ring_bcm/RingBCM_250216_134510.txt
python 00_proc_ring_bcm.py --experiment=exp02/case02 --filename=ring_bcm/RingBCM_250216_132651.txt
python 00_proc_ring_bcm.py --experiment=exp02/case03 --filename=ring_bcm/RingBCM_250216_112004.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan_phase_01 --filename=ring_bcm/RingBCM_250216_121043.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan_phase_02 --filename=ring_bcm/RingBCM_250216_123848.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan_phase_03 --filename=ring_bcm/RingBCM_250216_123634.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan_phase_04 --filename=ring_bcm/RingBCM_250216_124130.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan_amp_01 --filename=ring_bcm/RingBCM_250216_142012.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan_amp_02 --filename=ring_bcm/RingBCM_250216_142227.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan_amp_03 --filename=ring_bcm/RingBCM_250216_142308.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan_amp_04 --filename=ring_bcm/RingBCM_250216_142349.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan_amp_05 --filename=ring_bcm/RingBCM_250216_142524.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan_amp_06 --filename=ring_bcm/RingBCM_250216_142552.txt
python 00_proc_ring_bcm.py --experiment=exp08/case01 --filename=ring_bcm/RingBCM_250216_145232.txt
python 00_proc_ring_bcm.py --experiment=exp08/case02 --filename=ring_bcm/RingBCM_250216_145453.txt
python 00_proc_ring_bcm.py --experiment=exp09/case01 --filename=ring_bcm/RingBCM_250216_151932.txt
python 00_proc_ring_bcm.py --experiment=exp09/case02 --filename=ring_bcm/RingBCM_250216_153559.txt
python 00_proc_ring_bcm.py --experiment=exp09/case03 --filename=ring_bcm/RingBCM_250216_154825.txt

# Process LLRF data
python 01_proc_ring_llrf.py --experiment=exp01
python 01_proc_ring_llrf.py --experiment=exp01/beam_off
python 01_proc_ring_llrf.py --experiment=exp02/case01
python 01_proc_ring_llrf.py --experiment=exp02/case01/beam_off
python 01_proc_ring_llrf.py --experiment=exp02/case02
python 01_proc_ring_llrf.py --experiment=exp02/case02/beam_off
python 01_proc_ring_llrf.py --experiment=exp02/case03
python 01_proc_ring_llrf.py --experiment=exp02/case03/beam_off
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan_phase_01
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan_phase_01
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan_phase_02
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan_phase_03
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan_phase_04
python 01_proc_ring_llrf.py --experiment=exp07/scan_amp_01
python 01_proc_ring_llrf.py --experiment=exp07/scan_amp_02
python 01_proc_ring_llrf.py --experiment=exp07/scan_amp_03
python 01_proc_ring_llrf.py --experiment=exp07/scan_amp_04
python 01_proc_ring_llrf.py --experiment=exp07/scan_amp_05
python 01_proc_ring_llrf.py --experiment=exp07/scan_amp_06

# Plot BCM data
python 02_plot_ring_bcm.py --experiment=exp01                 
python 02_plot_ring_bcm.py --experiment=exp02/case01
python 02_plot_ring_bcm.py --experiment=exp02/case02
python 02_plot_ring_bcm.py --experiment=exp02/case03
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan_phase_01
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan_phase_02
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan_phase_03
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan_phase_04
python 02_plot_ring_bcm.py --experiment=exp07/scan_amp_01
python 02_plot_ring_bcm.py --experiment=exp07/scan_amp_02
python 02_plot_ring_bcm.py --experiment=exp07/scan_amp_03
python 02_plot_ring_bcm.py --experiment=exp07/scan_amp_04
python 02_plot_ring_bcm.py --experiment=exp07/scan_amp_05
python 02_plot_ring_bcm.py --experiment=exp07/scan_amp_06
python 02_plot_ring_bcm.py --experiment=exp08/case01
python 02_plot_ring_bcm.py --experiment=exp08/case02
python 02_plot_ring_bcm.py --experiment=exp09/case01
python 02_plot_ring_bcm.py --experiment=exp09/case02
python 02_plot_ring_bcm.py --experiment=exp09/case03

# Plot LLRF data
python 03_plot_ring_llrf.py --experiment=exp01
python 03_plot_ring_llrf.py --experiment=exp01/beam_off
python 03_plot_ring_llrf.py --experiment=exp02/case01
python 03_plot_ring_llrf.py --experiment=exp02/case02
python 03_plot_ring_llrf.py --experiment=exp02/case03
python 03_plot_ring_llrf.py --experiment=exp02/case01/beam_off
python 03_plot_ring_llrf.py --experiment=exp02/case02/beam_off
python 03_plot_ring_llrf.py --experiment=exp02/case03/beam_off
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan_phase_01
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan_phase_01
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan_phase_02
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan_phase_03
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan_phase_04
python 03_plot_ring_llrf.py --experiment=exp07/scan_amp_01
python 03_plot_ring_llrf.py --experiment=exp07/scan_amp_02
python 03_plot_ring_llrf.py --experiment=exp07/scan_amp_03
python 03_plot_ring_llrf.py --experiment=exp07/scan_amp_04
python 03_plot_ring_llrf.py --experiment=exp07/scan_amp_05
python 03_plot_ring_llrf.py --experiment=exp07/scan_amp_06