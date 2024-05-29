#!/usr/bin/env python
import argparse
import logging
import numpy as np
import pandas as pd
import os
import sys
import subprocess
from functools import partial
from io import StringIO
import asyncio

from sklearn.metrics import r2_score

from util.OptunaStudy import OptunaStudy
from util.DataUtil import DataUtil
from util.CvUtilFast import do_cv_fast
import util.LGBMUtil as LGBMUtil
from util.FEUtil import FEUtil
import lightgbm as lgb

project_bucket = '<Your Bucket>'
target_variable = 'FloodProbability'
train_bucket = 'train'
train_file = 'train.csv'
test_file = 'test.csv'
model_folder = 'model'
case = 'hpo_ex1_case1'

class R2Objective:
    def __init__(self):
        pass
    @classmethod 
    def score(cls, model, X, y):
        pred = model.predict(X)
        score = r2_score(y, pred)
        return score  

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', action="store", dest='model_dir',
                        type=str, default=os.environ.get('SM_MODEL_DIR', './'))

    parser.add_argument('--output-dir', action="store", dest='output_dir',
                        type=str, default=os.environ.get('SM_OUTPUT_DIR', './'))

    parser.add_argument('--n_trials', action="store", dest='n_trials',
                        type=int, default=2)

    parser.add_argument('--n_study_jobs', action="store", dest='n_study_jobs',
                        type=int, default=2)

    parser.add_argument('--n_model_jobs', action="store", dest='n_model_jobs',
                        type=int, default=2)                        

    parser.add_argument('--training_fraction', action="store", dest='training_fraction', 
                        type=float, default=1.0)

    args, _ = parser.parse_known_args()

    logger = logging.getLogger(__name__)

    logging.basicConfig(filename=args.model_dir + '/training_' + case + '.log',
                        level=logging.DEBUG)

    print(f'Arguments: {args}')
    logger.info(f'Arguments: {args}')
    logger.info(f'Output directory: {args.model_dir}')

    try:
        subprocess.run(["pwd"])
        subprocess.run(['python', '--version'])
    except Exception as e:
        print(e)

    du = DataUtil(project_bucket,
                  train_bucket,
                  train_file,
                  target_variable,
                  test_file)

    ds = du.get_data_sagemaker(set_train_index=False,
                               include_original_data=False)

    trainX = ds['train'].sample(frac=args.training_fraction)
    testX = ds['test']
    trainy = trainX.pop(target_variable)

    cols = trainX.columns.values
    feUtil = FEUtil(cols)
    trainX = feUtil.add_fe(trainX, use_funcs=feUtil.get_all_stats())
    testX  = feUtil.add_fe(testX, use_funcs=feUtil.get_all_stats())

    lgb.register_logger(logging.Logger('CustomLogger', logging.CRITICAL))

    def lgb_factory():
        return partial(LGBMUtil.lgbm_factory, 
                       n_procs=args.n_model_jobs)

    def lgb_param_factory():
        return partial(OptunaStudy.get_lgbc_most_important_params,
                       metrics=['r2'])

    study = OptunaStudy(trainX, trainy,
                        n_folds=5,
                        model_factory=lgb_factory(),
                        params_factory=lgb_param_factory(),
                        objective_factory=R2Objective,
                        log_level=logging.DEBUG,)

    study.do_study(n_trials=args.n_trials, 
                   n_jobs=args.n_study_jobs, 
                   direction="maximize")

    logger.info('Train X dataframe:')
    buf = StringIO()
    trainX.info(buf=buf)
    logger.info(buf.getvalue())

    logger.info('Test X dataframe:')
    buf = StringIO()
    testX.info(buf=buf)
    logger.info(buf.getvalue())

    trainX.to_csv(args.model_dir + '/flood_train_' + case + '.csv')
    testX.to_csv(args.model_dir + '/flood_test_' + case + '.csv')

    logger.info('Done.')

    sys.exit(0)