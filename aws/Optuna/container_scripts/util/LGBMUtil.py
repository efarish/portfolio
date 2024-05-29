import lightgbm as lgb
from sklearn.ensemble import BaggingRegressor
import logging

def lgbm_factory(params=None, objective=None, n_procs=-1,
                 bagging=None, 
                 bag_max_samples=1.0, bag_max_features=1.0):

  lgb.register_logger(logging.Logger('CustomLogger', logging.CRITICAL))
    
  if params is None:
    params = {'verbose':-1, 'n_jobs': n_procs,
              #'device_type':"gpu", 'device':"cuda",
              'seed':42,}

  params['n_jobs'] = n_procs

  if objective is not None:
    params['objective'] = objective

  gbm = lgb.LGBMRegressor(**params)

  if bagging is not None:
    gbm = BaggingRegressor(gbm, n_estimators=bagging,
                           max_samples=bag_max_samples, max_features=bag_max_features,
                           random_state=42, n_jobs=n_procs)

  return gbm