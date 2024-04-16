from skopt.space import Real, Categorical, Integer
import lightgbm as lgb
from xgboost import XGBRegressor

def get_xgb_params(_model=XGBRegressor(random_state=42)):

  params = {
    'model': [_model],
    'model__n_estimators':      Integer(500, 3000),
    'model__eta':               Real(1e-3, 1),
    'model__gamma':             Real(0.0, 100),
    'model__max_depth':         Integer(1, 10),
    'model__min_child_weight':  Real(0.1, 10),
    'model__max_delta_step':    Real(0, 10),
    'model__subsample':         Real(0.05, 1),
    'model__colsample_bytree':  Real(0.0, 1),
    'model__colsample_bylevel': Real(0.0, 1),
    'model__colsample_bynode':  Real(0.0, 1),
    'model__reg_lambda':        Real(0.0, 400.0),
    'model__reg_alpha':         Real(0.0, 200.0),
    'model__tree_method':       Categorical(['auto', 'exact', 'approx']),
    'model__grow_policy':       Categorical(['depthwise', 'lossguide']),
    }
  return params
  

def get_lgbc_params(_model=lgb.LGBMRegressor(random_state=42, verbosity=-1)):
  
  params  = {
    'model': [_model],
    'model__learning_rate': Real(0.01, 0.5, 'log-uniform'), # step size shrinkage used to prevent overfitting. Lower values = more accuracy but slower training
    'model__num_leaves': Integer(25, 250), # the maximum number of leaves in any tree
    'model__max_depth': Integer(6, 15), # the maximum depth of any tree
    'model__min_child_samples': Integer(1, 20), # minimum number of samples required in a child node to be split
    #'model__min_child_weight':  space.Real(1e-3, 1),
    'model__feature_fraction': Real(0.1, 0.9), # fraction of features used for each boosting iteration
    'model__bagging_fraction': Real(0.1, 0.9), # fraction of the training data to be used for each iteration
    'model__bagging_freq': Integer(1, 10), # number of iterations to perform bagging (sample of data to grow trees)
    'model__reg_alpha': Real(0, 100), # L1 regularization term on weights
    'model__reg_lambda': Real(0, 100), # L2 regularization term on weights
    'model__class_weight': Categorical(['balanced', None]), # weighting of positive classes in binary classification problems
    'model__boosting_type': Categorical(['gbdt', 'dart']), # type of boosting algorithm to use
    'model__objective': Categorical(['regression']), # objective function to use for training
    #'model__metric': Categorical(['aucpr']), # evaluation metric to use for early stopping and model selection
    'model__subsample': Real(0.1, 1.0, 'uniform'), # fraction of data samples used for each iteration
    #subsample_freq (int, optional (default=0)) – Frequency of subsample, <=0 means no enable. 
    #subsample_for_bin (int, optional (default=200000))
    'model__colsample_bytree': Real(0.1, 1.0, 'uniform'), # fraction of features used for each iteration
    # 'min_gain_to_split': Integer(0, 15), # minimum gain required to make a split
    'model__min_split_gain': Real(0, 1.0, 'uniform'), # minimum gain required to make a split
    'model__n_estimators': Integer(100, 3000), # number of trees in the model
    # 'early_stopping_rounds': Integer(25, 100), # number of iterations with no improvement after which training will stop
    'model__importance_type': Categorical(['split', 'gain']), # type of feature importance to use for feature selection
    'model__scale_pos_weight': Real(0.1, 10.0, 'uniform') # control the balance of positive and negative weights
  }

  return params

