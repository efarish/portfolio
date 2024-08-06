#!/usr/bin/env python

"""
This script is assumes its being run in an AWS SKLearn container.
"""

import argparse
import logging
import os
import subprocess
import sys
from io import StringIO

import lightgbm as lgb
import numpy as np
import pandas as pd
from autogluon.tabular import TabularPredictor
from autogluon.tabular.configs.hyperparameter_configs import \
    get_hyperparameter_config
from util import DataUtil
from util.FEUtil import FEUtil

target_variable = 'FloodProbability'
project_bucket = '< YOUR S3 BUCKET HERE >'
train_bucket = 'train'
train_file = 'combined_train.csv'
test_file = 'test.csv'

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', action="store", dest='model_dir',
                        type=str, default=os.environ.get('SM_MODEL_DIR', './'))

    parser.add_argument('--output-dir', action="store", dest='output_dir',
                        type=str, default=os.environ.get('SM_OUTPUT_DIR', './'))

    parser.add_argument('--n_jobs', action="store", dest='n_jobs',
                        type=int, default=2)

    parser.add_argument('--training_fraction', action="store",
                        dest='training_fraction',
                        type=float, default=0.01)

    parser.add_argument('--time_limit', action="store", dest='time_limit',
                        type=int, default=600)

    parser.add_argument('--version', action="store", dest='version',
                        type=str, default='final')

    args, _ = parser.parse_known_args()

    logger = logging.getLogger(__name__)

    logging.basicConfig(filename=args.model_dir + '/training'
                                                + args.version + '.log',
                        level=logging.INFO)

    print(f'Arguments: {args}')
    logger.info(f'Arguments: {args}')
    logger.info(f'Output directory: {args.model_dir}')

    try:
        subprocess.run(["pwd"])
        subprocess.run(['python', '--version'])
    except Exception as e:
        print(e)

    util = DataUtil(project_bucket,
                    train_bucket,
                    train_file,
                    test_file)

    ds = util.get_data_sagemaker()
    train = ds['train']
    test = ds['test']

    train = train.sample(frac=args.training_fraction)

    cols = train.columns.values
    cols = np.delete(cols, np.argwhere(cols == target_variable))   
    feUtil = FEUtil(cols)
    train = feUtil.add_fe(train, use_funcs=feUtil.get_all_stats())
    test  = feUtil.add_fe(test, use_funcs=feUtil.get_all_stats())  

    logger.info('Train X dataframe:')
    buf = StringIO()
    train.info(buf=buf)
    logger.info(buf.getvalue())

    logger.info('Test X dataframe:')
    buf = StringIO()
    test.info(buf=buf)
    logger.info(buf.getvalue())

    train.to_csv(args.model_dir + '/train_' + args.version + '.csv')
    test.to_csv(args.model_dir + '/test_' + args.version + '.csv')

    lgb.register_logger(logging.Logger('CustomLogger', logging.WARN))

    tabPred = TabularPredictor(path=args.model_dir + '/AutoGluonBuild_'
                                                   + args.version,
                               label=target_variable,
                               problem_type='regression',
                               eval_metric='rmse',)

    params = get_hyperparameter_config('default')

    del params['NN_TORCH']
    del params['KNN']
    del params['FASTAI']
    del params['RF']
    del params['XT']

    lgb_params = {'colsample_bytree':0.837979598014033,
    'learning_rate': 0.007326357964510739, 
    'max_depth': 100,
    'min_child_samples': 125, 'n_estimators': 1200, 
    'num_leaves': 90, 'objective': 'regression', 
    'subsample': 0.9321441882060605,
    'subsample_freq': 6,}
    params['GBM'].append(lgb_params)

    xgb_params = {'alpha': 13,
    'min_child_weight': 39,
    'subsample': 0.6177279393605696,
    'eta': 0.23890325388859307,
    'n_estimators': 1257,
    'verbosity': 1}
    params['XGB'] = [{}, xgb_params]

    cat_params = {
        'learning_rate':   0.019893529354730797,
        'depth':           7,
        'l2_leaf_reg':     5,
        'random_strength': 5,
        'iterations':      1950,
        'verbose':         False
        }
    params['CAT'] = [{}, cat_params]

    predictor = tabPred.fit(train_data=train,
                            time_limit=args.time_limit,
                            presets="best_quality",
                            hyperparameters=params,
                            num_cpus=args.n_jobs,)

    # Refit best model with all data.
    predictor.refit_full()

    logger.info('Get predictions from test data...')
    pred = predictor.predict(test)
    df_results = pd.DataFrame(data={target_variable: pred},
                              index=test.index)
    df_results.index.name = "id"
    df_results.to_csv(args.model_dir + '/flood_ag_' + args.version + '.csv')
    logger.info('Done.')

    sys.exit(0)