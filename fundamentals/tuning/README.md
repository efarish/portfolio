# Project: PyTorch Hyperparameter Tuning

This project tunes the hyperparameters of a simple feedforward network using Optuna. Optuna uses a configurable algorithm to search for a best model. By default it uses a Bayesian optimization algorithm called [Tree-structured Parzen Estimator algorithm](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html).

The data used for this experiment is the Abalone Dataset and it can be found [here](https://www.kaggle.com/competitions/playground-series-s4e4/overview).
