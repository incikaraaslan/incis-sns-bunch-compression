# Analysis

This pipeline processes data from the `../data` directory.


## Organization

* `00_proc_bcm.py`: 
* `config.yml`: Stores info on beam/accelerator state during experiment, as well as diagnostic settigns.
* `environment.yml`: To create conda environment with specific python version and dependencies.
* `make-run.sh`: Bash script to run analysis pipeline.
* `make-clean.sh` Bashs script to remove analysis outputs and annoying hidden files.
* `requirements.txt`: Lists Python packages required for the analysis.


## Run analysis

Create new conda environment:
```
conda env create --file environment.yml 
conda activate analysis-250216
```

Run everything:
```
./make-clean.sh
./make-run.sh
```

