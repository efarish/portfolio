import logging
from functools import partial

import numpy as np
import optuna
import pandas as pd
from optuna.trial import TrialState
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from sklearn.model_selection import KFold

def msle_loss(y_true, y_pred):
    y_pred = np.maximum(y_pred, -1+1e-6)
    metric = ((np.log1p(y_pred)-np.log1p(y_true))/(1+y_pred), 
              (1-np.log1p(y_pred)+np.log1p(y_true))/(1+y_pred)**2)
    return metric
    
class RMSEObjective:
    
    def __init__(self):
        pass
    
    @classmethod 
    def score(cls, model, X, y):
        pred = model.predict(X)
        score = np.sqrt(mean_squared_error(y, pred))
        return score      
        
class OptunaStudy:
    
    def __init__(self, X, y, 
                 n_folds=5, 
                 log_level=logging.INFO, 
                 model_factory=None,
                 params_factory=None,
                 objective_factory=None,
                 use_gpu=True,
                 seed=42):
                     
        self.X = X
        self.y = y
        self.n_folds = n_folds
        self.log = logging.getLogger('OptunaStudy') 
        logging.basicConfig(level=log_level)
        self.use_gpu = use_gpu
        self.seed = seed
        self.objective_map = {'rmsle': msle_loss}
        self.model_factory = model_factory
        self.params_factory = params_factory
        if objective_factory is None:
            self.objective_factory = RMSEObjective
        else: self.objective_factory = objective_factory

    def _do_optuna_cv(self, model_factory, trial):

        kfolds = KFold(n_splits=self.n_folds, shuffle=True, random_state=self.seed)
        fold_score = []
        
        objective = self.objective_factory()

        for idx, (train_idx, test_idx) in enumerate(kfolds.split(self.X, self.y)):
            
            X_train, X_test = self.X.values[train_idx, :],      self.X.values[test_idx, :]
            y_train, y_test = self.y.values[train_idx].ravel(), self.y.values[test_idx].ravel()

            model = model_factory()
            model.fit(X_train, y_train)
            score = objective.score(model, X_test, y_test)
            
            msg = f"Trail {trial.number}, Fold {idx}, Score: {score}"
            self.log.debug(msg)
            
            fold_score.append(score)
            
            trial.report(np.mean(fold_score), idx)

            if trial.should_prune():
                msg =  f"Trial {trial.number} pruned for Score: {score}, Mean Score: {np.mean(fold_score)}"
                self.log.warn(msg)
                raise optuna.exceptions.TrialPruned()

            trial.set_user_attr(key="best_model_tmp", value=model)

        return np.mean(fold_score)

    def _callback(self, study, trial):
        if study.best_trial.number == trial.number:
            study.set_user_attr(key="best_model", 
                                value=trial.user_attrs["best_model_tmp"])

    def _train(self, trial):
        config = self.params_factory(trial) 
        self.log.info(f"STARTING Trial {trial.number} with CONFIG: {config}")
        model_factory = partial(self.model_factory, params=config) 
        score = self._do_optuna_cv(model_factory, trial)
        self.log.info(f"Trail {trial.number} Final Score: {score}")
        return score

    def do_study(self, n_trials=10, n_jobs=-1, direction="minimize"):
        # sampler = TPESampler(seed=SEED)
        # Am not setting seed since Optuna does not support deterministic 
        # behavior when tunning with more than
        #  one job.
        study = optuna.create_study(direction=direction, 
                                    pruner=optuna.pruners.HyperbandPruner()) 
        self.last_study = study
        #optuna.logging.set_verbosity(?)
        study.optimize(
            self._train,
            n_trials=n_trials,
            timeout=None,
            callbacks=[self._callback],
            n_jobs=n_jobs,
        )

        self._report_results(study)

    def _report_results(self, study):
        pruned_trials = study.get_trials(deepcopy=False, states=[TrialState.PRUNED])
        complete_trials = study.get_trials(
            deepcopy=False, states=[TrialState.COMPLETE]
        )

        print("Study statistics: ")
        print("  Number of finished trials: ", len(study.trials))
        print("  Number of pruned trials: ", len(pruned_trials))
        print("  Number of complete trials: ", len(complete_trials))

        best_model = study.user_attrs["best_model"]
        self.log.info('Best model parameters...')
        self.log.info(best_model)

        score = self.objective_factory().score(best_model, self.X, self.y)
        self.log.info(f"Training Data Score: {score}")

        print("Best trial:")
        trial = study.best_trial

        print("  Value: ", trial.value)

        print("  Params: ")
        for key, value in trial.params.items():
            print("    {}: {}".format(key, value))

    @staticmethod
    def get_lgbc_params(trial):
        
        params  = {
        #'bagging_fraction': Real(0.1, 0.9),
        #'bagging_freq':     Integer(1, 10),
        #'class_weight':      trial.suggest_categorical('class_weight', ['balanced', None]), # weighting of positive classes in binary classification problems
        #'colsample_bytree':  trial.suggest_float('colsample_bytree', 0.1, 1.0, step=0.1), # fraction of features used for each iteration
        #'early_stopping_rounds': trial.suggest_int('early_stopping_rounds', 5, 100, step=1), # number of iterations with no improvement after which training will stop
        #'min_child_weight':  space.Real(1e-3, 1),
        #'min_split_gain':    trial.suggest_float('min_split_gain', 0, 1.0, step=0.1), #default 0,  minimum gain required to make a split
        #'min_gain_to_split': Integer(0, 15), # minimum gain required to make a split
        #'scale_pos_weight':  trial.suggest_float(0.1, 10.0, 'uniform') # control the balance of positive and negative weights
        #subsample_for_bin (int, optional (default=200000))
        #subsample_freq (int, optional (default=0)) – Frequency of subsample, <=0 means no enable.
        'boosting_type':    trial.suggest_categorical('boosting_type', ['gbdt', 'dart']), # type of boosting algorithm to use
        'feature_fraction': trial.suggest_float('feature_fraction', 0.1, 0.9, step=0.1),
        'importance_type':  trial.suggest_categorical('importance_type', ['split', 'gain']), # type of feature importance to use for feature selection
        'learning_rate':    trial.suggest_float("learning_rate", 1e-2, 5e-1, log=True), #default 0.1
        'max_bin':          trial.suggest_int('max_bin', 100, 3000, step=10),
        'max_depth':        trial.suggest_int("max_depth", 5, 500, step=5) ,
        'metrics':          trial.suggest_categorical('metrics', ['rmse']),
        'min_child_samples':trial.suggest_int('min_child_samples', 1, 200, step=1),
        'n_estimators':     trial.suggest_int('n_estimators', 500, 3000, step=50), # number of trees in the model
        'num_leaves':       trial.suggest_int("num_leaves", 10, 500, step=5), #default 31
        'objective':        trial.suggest_categorical('objective', ['regression']),
        'reg_alpha':        trial.suggest_float('reg_alpha', 0, 300, step=10), # L1 regularization term on weights
        'reg_lambda':       trial.suggest_float('reg_lambda', 0, 800, step=10), # L2 regularization term on weights
        'subsample':        trial.suggest_float('subsample', 0.1, 1.0, step=0.1), # fraction of data samples used for each iteration
        }
        
        return params

    @staticmethod
    def get_lgbc_most_important_params(trial, metrics=['rmse']):
        """
        Using AWS Suggestions for LGBM HPO:
        https://docs.aws.amazon.com/sagemaker/latest/dg/lightgbm-tuning.html
        """
        params  = {
        'subsample':        trial.suggest_float('subsample', 0.1, 1.0), #aka bagging_fraction
        'subsample_freq':   trial.suggest_int("subsample_freq", 0, 10, step=1), #aka bagging_freq   
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.1, 1.0), #feature_fraction
        'learning_rate':    trial.suggest_float("learning_rate", 1e-3, 1e-2, log=True),
        'max_depth':        trial.suggest_int("max_depth", 10, 100, step=5),
        'min_child_samples':trial.suggest_int('min_child_samples', 10, 200, step=5), #min_data_in_leaf
        'n_estimators':     trial.suggest_int('n_estimators', 500, 3000, step=50), # number of trees in the model
        'num_leaves':       trial.suggest_int("num_leaves", 10, 100, step=1), #default 31

        'metrics':          trial.suggest_categorical('metrics', metrics),
        'objective':        trial.suggest_categorical('objective', ['regression']),
        }
        
        return params

    @staticmethod
    def get_catbst_most_important_params(trial, loss_function='RMSE'):
        """
        Using AWS Suggestions for CatBoost HPO:
        https://docs.aws.amazon.com/sagemaker/latest/dg/catboost-tuning.html
        """
        params  = {
            'learning_rate':   trial.suggest_float("learning_rate", 1e-3, 2e-2, log=True),
            'depth':           trial.suggest_int("depth", 4, 10, step=1),
            'l2_leaf_reg':     trial.suggest_int("l2_leaf_reg", 2, 10, step=1),
            'random_strength': trial.suggest_int("random_strength", 0, 10, step=1),
            'random_seed':     42,
            'loss_function':   loss_function,
            'verbose':         False,
            'iterations':      trial.suggest_int("iterations", 200, 2000, step=10),
        }
        
        return params

    @staticmethod
    def get_xgb_most_important_params(trial, loss_function='RMSE'):
        """
        Using AWS Suggestions for XGBoost HPO:
        https://docs.aws.amazon.com/sagemaker/latest/dg/xgboost-tuning.html
        """
        params  = {
            'alpha':           trial.suggest_int("alpha", 0, 1000),
            'min_child_weight':trial.suggest_int("min_child_weight", 0, 120),
            'subsample':       trial.suggest_float("subsample", 0.5, 1),
            'eta':             trial.suggest_float('eta', 0.1, 0.5),
            'n_estimators':    trial.suggest_int('n_estimators', 1, 4000), #num_round
        }
        
        return params
