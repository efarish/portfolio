# Project: XGBRegressor and LightGBM

This project performs regression with [XGBoost](https://xgboost.readthedocs.io/en/stable/python/python_api.html) and [LightGBM](https://lightgbm.readthedocs.io/en/stable/) utilizing [scikit-optimize Bayesian optimization](https://scikit-optimize.github.io/stable/) to tune hyperparameter. 

The dataset used is the Abalone dataset and can be found [here](https://www.kaggle.com/competitions/playground-series-s4e4/submissions).

These models will be evaluated based on their performance and the best model will be used to determine the features most important for estimating the target. In this case, the target is the number of rings on an [abalone](https://en.wikipedia.org/wiki/Abalone).  

See the notebook [here](https://github.com/efarish/portfolio/blob/main/research/abalone/Boosting.ipynb) for details.


