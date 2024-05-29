import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error, mean_squared_log_error
import asyncio
from concurrent.futures import ProcessPoolExecutor


def get_score(metric, model, test_x, test_y):

    pred = pd.DataFrame(model.predict(test_x))
    score = None
    try:
      score = metric(test_y, pred)
    except Exception as error:
      print(f'Score error: {error}')

    return score

def fit_fold(fold, train_idx, test_idx, model_factory, X, y,  
             use_early_stopping, use_val_for_score,
             X_val, y_val, metric):

    X_train, X_test = X.values[train_idx, :], X.values[test_idx, :]
    y_train, y_test = y.values.ravel()[train_idx], y.values.ravel()[test_idx]

    if use_early_stopping or use_val_for_score:
        if X_val is None:
          train_x, val_x, train_y, val_y = train_test_split(X_train, y_train.ravel(), 
                                                            test_size=0.1, random_state=42)   
        else:
            val_x, val_y = X_val, y_val

    model = model_factory()

    if use_early_stopping:
      model.fit(X_train, y_train, eval_set=[(val_x, val_y)])
    else:
      model.fit(X_train, y_train)

    if use_val_for_score:
        score = get_score(metric, model, X_val, y_val)
    else:
        score = get_score(metric, model, X_test, y_test)

    print(f"Fold {fold} Score: {score}")

    return (fold, score)


async def do_cv_async(model_factory, _X, _y, folds=5, 
                      use_early_stopping=False, use_val_for_score=False,
                      _X_val=None, _y_val=None, n_procs=1, metric=mean_squared_error):

    kfolds = KFold(n_splits=folds, shuffle=True, random_state=42)
    fold_metrics = []

    if n_procs > folds: #no need from jobs than folds
        n_procs = folds

    loop = asyncio.get_event_loop()

    print("Starting CV...")
    with ProcessPoolExecutor(n_procs) as pool:

        ep = [model_factory, _X, _y, 
              use_early_stopping, use_val_for_score,
              _X_val, _y_val, metric]

        tasks = [loop.run_in_executor(pool, fit_fold, fold, train_idx, test_idx, *ep) \
                 for fold, (train_idx, test_idx) in enumerate(kfolds.split(_X, _y))]

        fold_metrics = await asyncio.gather(*tasks)

    print("Done CV")

    metrics = np.array(fold_metrics)

    means = metrics.mean(axis=0)

    print(f"Final -> Score average: {means[1]}")

    return metrics


async def do_cv_fast(model_factory, _X, _y, folds=5, 
                     use_early_stopping=False, use_val_for_score=False,
                     _X_val=None, _y_val=None, n_procs=1,
                     metric=mean_squared_error):

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():
        print('Async event loop already running. Adding coroutine to the event loop.')
        tsk = loop.create_task(do_cv_async(model_factory, _X, _y, folds, 
                                           use_early_stopping, use_val_for_score,
                                           _X_val, _y_val, n_procs, metric))

        result = await tsk
    else:
        print('Starting new event loop')
        result = asyncio.run(do_cv_async(model_factory, _X, _y, folds,
                                         use_early_stopping, use_val_for_score,
                                         _X_val, _y_val, n_procs, metric))

    return result
