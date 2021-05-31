# Bayesian-sequential-data-assimilation-method
This repository contains the code and data to make forecasts with data of COVID-19 from all Mexican states and Mexico City’s metropolitan area using the Bayesian sequential data assimilation model proposed in Daza-Torres et al., https://arxiv.org/abs/2103.06152.


## Data needed: 
-  Configuracion.csv
This file contains the population, code, and initial date outbreaks for the Mexican States and Mexico City’s metropolitan.
 
Code*.csv’s  files provide records of deaths and confirmed cases for the Mexican States and Mexico City’s metropolitan from February 27, 2020, to May 5, 2021.
(*) e.g., AS.csv corresponds to the data of Aguascalientes, see code list in Configuracion.csv


## To run:
- AnalisisZMs.py
This is the master program, here all the routines are called, and the output is generated.
 
 
## Auxiliar files:
In these files,  we define the transmission model and its numerical solution as well the functions used for the mcmc for being called by AnalisisZMs.py and don't need to run.

- covid_fm.py
- fm_matrix.py 
- covid_mcmc.py


## Output:

### Files
Code*_post_params.pkl 
Code*court_samples.pkl
Code*court_solns.pkl
Code*court_solns_plain.pkl

### Figures
Code*court_*_I.png
Code*court_*_D.png
Code*court_*_cono_I.png
Code*court_*_cono_D.png



## Note:
The MCMC use the t-walk implementation. https://www.cimat.mx/~jac/twalk/
- pytwalk.py

