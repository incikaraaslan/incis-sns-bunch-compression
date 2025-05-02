#!/bin/sh

# Should replace this with a python script...

set -x

# Process BCM data
python 00_proc_ring_bcm.py --experiment=exp01 --filename=ring-bcm/RingBCM_250216_104155.txt
python 00_proc_ring_bcm.py --experiment=exp02/case01 --filename=ring-bcm/RingBCM_250216_134510.txt
python 00_proc_ring_bcm.py --experiment=exp02/case02 --filename=ring-bcm/RingBCM_250216_132651.txt
python 00_proc_ring_bcm.py --experiment=exp02/case03 --filename=ring-bcm/RingBCM_250216_112004.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan-phase-01 --filename=ring-bcm/RingBCM_250216_121043.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan-phase-02 --filename=ring-bcm/RingBCM_250216_123848.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan-phase-03 --filename=ring-bcm/RingBCM_250216_123634.txt
python 00_proc_ring_bcm.py --experiment=exp02/case04/scan-phase-04 --filename=ring-bcm/RingBCM_250216_124130.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan-amp-01 --filename=ring-bcm/RingBCM_250216_142012.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan-amp-02 --filename=ring-bcm/RingBCM_250216_142227.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan-amp-03 --filename=ring-bcm/RingBCM_250216_142308.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan-amp-04 --filename=ring-bcm/RingBCM_250216_142349.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan-amp-05 --filename=ring-bcm/RingBCM_250216_142524.txt
python 00_proc_ring_bcm.py --experiment=exp07/scan-amp-06 --filename=ring-bcm/RingBCM_250216_142552.txt
python 00_proc_ring_bcm.py --experiment=exp08/case01 --filename=ring-bcm/RingBCM_250216_145232.txt
python 00_proc_ring_bcm.py --experiment=exp08/case02 --filename=ring-bcm/RingBCM_250216_145453.txt
python 00_proc_ring_bcm.py --experiment=exp09/case01 --filename=ring-bcm/RingBCM_250216_151932.txt
python 00_proc_ring_bcm.py --experiment=exp09/case02 --filename=ring-bcm/RingBCM_250216_153559.txt
python 00_proc_ring_bcm.py --experiment=exp09/case03 --filename=ring-bcm/RingBCM_250216_154825.txt

# Process LLRF data
python 01_proc_ring_llrf.py --experiment=exp01
python 01_proc_ring_llrf.py --experiment=exp01/beam-off
python 01_proc_ring_llrf.py --experiment=exp02/case01
python 01_proc_ring_llrf.py --experiment=exp02/case01/beam-off
python 01_proc_ring_llrf.py --experiment=exp02/case02
python 01_proc_ring_llrf.py --experiment=exp02/case02/beam-off
python 01_proc_ring_llrf.py --experiment=exp02/case03
python 01_proc_ring_llrf.py --experiment=exp02/case03/beam-off
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan-phase-01
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan-phase-01
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan-phase-02
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan-phase-03
python 01_proc_ring_llrf.py --experiment=exp02/case04/scan-phase-04
python 01_proc_ring_llrf.py --experiment=exp07/scan-amp-01
python 01_proc_ring_llrf.py --experiment=exp07/scan-amp-02
python 01_proc_ring_llrf.py --experiment=exp07/scan-amp-03
python 01_proc_ring_llrf.py --experiment=exp07/scan-amp-04
python 01_proc_ring_llrf.py --experiment=exp07/scan-amp-05
python 01_proc_ring_llrf.py --experiment=exp07/scan-amp-06

# Plot BCM data
python 02_plot_ring_bcm.py --experiment=exp01                 
python 02_plot_ring_bcm.py --experiment=exp02/case01
python 02_plot_ring_bcm.py --experiment=exp02/case02
python 02_plot_ring_bcm.py --experiment=exp02/case03
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan-phase-01
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan-phase-02
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan-phase-03
python 02_plot_ring_bcm.py --experiment=exp02/case04/scan-phase-04
python 02_plot_ring_bcm.py --experiment=exp07/scan-amp-01
python 02_plot_ring_bcm.py --experiment=exp07/scan-amp-02
python 02_plot_ring_bcm.py --experiment=exp07/scan-amp-03
python 02_plot_ring_bcm.py --experiment=exp07/scan-amp-04
python 02_plot_ring_bcm.py --experiment=exp07/scan-amp-05
python 02_plot_ring_bcm.py --experiment=exp07/scan-amp-06
python 02_plot_ring_bcm.py --experiment=exp08/case01
python 02_plot_ring_bcm.py --experiment=exp08/case02
python 02_plot_ring_bcm.py --experiment=exp09/case01
python 02_plot_ring_bcm.py --experiment=exp09/case02
python 02_plot_ring_bcm.py --experiment=exp09/case03

# Plot LLRF data
python 03_plot_ring_llrf.py --experiment=exp01
python 03_plot_ring_llrf.py --experiment=exp01/beam-off
python 03_plot_ring_llrf.py --experiment=exp02/case01
python 03_plot_ring_llrf.py --experiment=exp02/case02
python 03_plot_ring_llrf.py --experiment=exp02/case03
python 03_plot_ring_llrf.py --experiment=exp02/case01/beam-off
python 03_plot_ring_llrf.py --experiment=exp02/case02/beam-off
python 03_plot_ring_llrf.py --experiment=exp02/case03/beam-off
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan-phase-01
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan-phase-01
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan-phase-02
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan-phase-03
python 03_plot_ring_llrf.py --experiment=exp02/case04/scan-phase-04
python 03_plot_ring_llrf.py --experiment=exp07/scan-amp-01
python 03_plot_ring_llrf.py --experiment=exp07/scan-amp-02
python 03_plot_ring_llrf.py --experiment=exp07/scan-amp-03
python 03_plot_ring_llrf.py --experiment=exp07/scan-amp-04
python 03_plot_ring_llrf.py --experiment=exp07/scan-amp-05
python 03_plot_ring_llrf.py --experiment=exp07/scan-amp-06