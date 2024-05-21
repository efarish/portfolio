#!/usr/bin/env python
import argparse
import logging
import os
import sys
import subprocess
import pickle

from autogluon.tabular import TabularPredictor
from autogluon.tabular.configs.hyperparameter_configs import get_hyperparameter_config

import lightgbm as lgb

from util import DataUtil

target_variable = '<Dataset target variable>'
project_bucket = '<A S3 bucket>'
train_bucket = 'train'
train_file = 'train.csv'

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', action="store", dest='model_dir',
                        type=str, default=os.environ['SM_MODEL_DIR'])

    parser.add_argument('--output-dir', action="store", dest='output_dir',
                        type=str, default=os.environ['SM_OUTPUT_DIR'])

    parser.add_argument('--n_jobs', action="store", dest='n_jobs',
                        type=int, default=2)

    parser.add_argument('--training_fraction', action="store", dest='training_fraction',
                        type=float, default=1.0)

    parser.add_argument('--time_limit', action="store", dest='time_limit',
                        type=int, default=600)

    args, _ = parser.parse_known_args()

    logger = logging.getLogger(__name__)

    logging.basicConfig(filename=args.model_dir + '/training.log',
                        level=logging.INFO)

    print(f'Arguments: {args}')
    logger.info(f'Arguments: {args}')
    logger.info(f'Output directory: {args.model_dir}')

    util = DataUtil(project_bucket,
                    train_bucket,
                    train_file)

    train = util.get_data_sagemaker()['train']

    if args.training_fraction < 1.0:
        train = train.sample(frac=args.training_fraction)

    lgb.register_logger(logging.Logger('CustomLogger', logging.WARN))

    tabPred = TabularPredictor(path=args.model_dir + '/AutoGluonBuild',
                               label=target_variable,
                               problem_type='regression',
                               eval_metric='rmse',)

    params = get_hyperparameter_config('default')

    del params['NN_TORCH']
    del params['KNN']
    del params['FASTAI']
    del params['RF']
    del params['XT']

    predictor = tabPred.fit(train_data=train,
                            time_limit=args.time_limit,
                            presets="best_quality",
                            hyperparameters=params,
                            num_cpus=args.n_jobs,)


    sys.exit(0)