# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 02:23:13 2023

@author: woshi
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.model_selection import KFold, cross_validate
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.base import BaseEstimator, RegressorMixin
import matplotlib.pyplot as plt

def get_VIF(_X):
    vif_data = pd.DataFrame() 
    vif_data["feature"] = _X.columns 
    vif_data["VIF"] = [variance_inflation_factor(_X.values, i) for i in range(len(_X.columns))] 
    return vif_data

def get_VIF_columns(_X, cuttoff):
    _X = _X.copy()
    while len(_X.columns) > 1:
        vif_data = get_VIF(_X)
        feature = vif_data.sort_values(by=['VIF'], ascending=False).iloc[:1,:1].values[0][0]
        vif = vif_data.sort_values(by=['VIF'], ascending=False).iloc[:1,1:].values[0][0]
        if vif <= cuttoff:
            break
        #del_cols.append(feature)
        _X =  _X.drop(feature, axis=1)
    return _X.columns.values

class SMWrapper(BaseEstimator, RegressorMixin):
    """ A universal sklearn-style wrapper for statsmodels regressors """
    def __init__(self, model_class, fit_intercept=True):
        self.model_class = model_class
        self.fit_intercept = fit_intercept
    def fit(self, X, y):
        if self.fit_intercept:
            X = sm.add_constant(X)
        self.model_ = self.model_class(y, X)
        self.results_ = self.model_.fit()
        return self
    def predict(self, X):
        if self.fit_intercept:
            X = sm.add_constant(X)
        return self.results_.predict(X)

def do_lm_cross_validation(model_class, _X, _y, n_jobs=-1):
    all_scores = [np.asarray([]),np.asarray([])]
    for i in range(0,30):
        kf = KFold(n_splits=10, random_state=i, shuffle=True)
        scores = cross_validate(model_class, _X, _y, 
                                cv=kf, scoring=('neg_root_mean_squared_error','r2'),
                                n_jobs = n_jobs)
        all_scores[0] = np.append(all_scores[0], scores['test_neg_root_mean_squared_error'].mean() )
        r_scores = scores['test_r2']
        adj_r_scores = 1 - (1-r_scores) * (len(_y) - 1) / (len(_y) - _X.shape[1] - 1)
        all_scores[1] = np.append(all_scores[1], adj_r_scores.mean() )
        if i % 5 == 0:
            print(f'{i} tests done...')
    
    print(f'All {i+1} done.')    
    print("Avg. RMSE %0.2f with SD %0.4f, Avg. R2 %0.2f with SD %0.4f"  % (all_scores[0].mean(), 
                                                                           all_scores[0].std(),
                                                                           all_scores[1].mean(),
                                                                           all_scores[1].std())  )
def pre_process(_data):

    _data = _data.copy()
    _data["covid_19_deaths_per_100k"] = _data['covid_19_deaths']/_data['total_population']*100000    
    del_cols = ['county_fips','covid_19_deaths','total_population']   
    _data =  _data.drop(del_cols, axis=1)    
    
    return _data

def get_formula(_X):
    if np.any(_X.columns == 'covid_19_deaths_per_100k'):
        _X = _X.copy().drop('covid_19_deaths_per_100k', axis=1) 
    lm_formula = 'covid_19_deaths_per_100k ~ ' + ' + '.join(_X.columns)
    return lm_formula

def remove_insignificant(_X, _model):
    _X = _X.copy()
    for pred in _model.pvalues.index[1:]:
        if _model.pvalues[pred] > 0.05:
            _X =  _X.drop(pred, axis=1)
    return _X

param_range1 = list((x if x!=0 else 1) for x in range(0,110,10))
param_range2 = list((x if x!=0 else 1) for x in range(0,32,2))

def plot_validation_curve(train_scores, test_scores, x_label, y_label, title, param_range):
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)

    figure = plt.figure(figsize=(10,6))
    axes = figure.add_subplot(1, 1, 1)
    axes.plot(param_range, train_mean, color="steelblue", alpha=0.75, label="Training score")
    axes.plot(param_range, test_mean, color="firebrick", alpha=0.75, label="Test score")
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.set_title(title)
    plt.legend(loc="best")
    plt.show()
    plt.close()
    
def results_to_curves( curve, results):
    all_statistics = results[curve]
    keys = list( all_statistics.keys())
    keys.sort()
    mean = []
    upper = []
    lower = []
    for k in keys:
        m, s = all_statistics[ k]
        mean.append( m)
        upper.append( m + 2 * s)
        lower.append( m - 2 * s)
    return keys, lower, mean, upper
    
    
def plot_learning_curves( results, metric, desired=None, zoom=False, credible=True,
                         in_xlim=None,in_ylim=None):
    figure = plt.figure(figsize=(10,6))
    axes = figure.add_subplot(1, 1, 1)
    xs, train_lower, train_mean, train_upper = results_to_curves( "train", results)
    train_lower = np.nan_to_num(train_lower)
    train_mean = np.nan_to_num(train_mean)
    train_upper = np.nan_to_num(train_upper)
    _, test_lower, test_mean, test_upper = results_to_curves( "test", results)
    axes.plot( xs, train_mean, color="steelblue", label="train")
    axes.plot( xs, test_mean, color="firebrick", label="test")
    if credible:
        axes.fill_between( xs, train_upper, train_lower, color="steelblue", alpha=0.25)
        axes.fill_between( xs, test_upper, test_lower, color="firebrick", alpha=0.25)
    if desired:
        if type(desired) is tuple:
            axes.axhline((desired[0] + desired[1])/2.0, color="gold", label="desired")
            axes.fill_between( xs, desired[1], desired[0], color="gold", alpha=0.25)
        else:
            axes.axhline( desired, color="gold", label="desired")
    axes.legend()
    axes.set_xlabel( "training set (%)")
    axes.set_ylabel( metric)
    axes.set_title("Learning Curves")
    if zoom:
      ## Added EAF 8/8/22 #############
      axes.set_xlim(in_xlim) 
      if in_ylim != None:
        y_lower = in_ylim[0]
        y_upper = in_ylim[1]
      else:
        y_lower = int( 0.9 * np.amin([train_lower[-1], test_lower[-1]]))
        y_upper = int( 1.1 * np.amax([train_upper[-1], test_upper[-1]]))
      #################################
      axes.set_ylim((y_lower, y_upper))
    plt.show()
    plt.close()
    
    
def plot_norm_qq(model):
    
    from statsmodels.graphics.gofplots import ProbPlot
    # normalized residuals
    model_norm_residuals = model.get_influence().resid_studentized_internal
    QQ = ProbPlot(model_norm_residuals)
    plot_lm_2 = QQ.qqplot(line='45', alpha=0.5, lw=1)
    plot_lm_2.axes[0].set_title('Normal Q-Q')
    plot_lm_2.axes[0].set_xlabel('Theoretical Quantiles')
    plot_lm_2.axes[0].set_ylabel('Standardized Residuals');
    # annotations
    abs_norm_resid = np.flip(np.argsort(np.abs(model_norm_residuals)), 0)
    abs_norm_resid_top_3 = abs_norm_resid[:3]
    for r, i in enumerate(abs_norm_resid_top_3):
        plot_lm_2.axes[0].annotate(i,
                                   xy=(np.flip(QQ.theoretical_quantiles, 0)[r],
                                       model_norm_residuals[i]));


