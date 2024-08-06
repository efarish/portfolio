import pandas as pd
import numpy as np
from scipy import stats


class FEUtil:
    """
    A utility class for feature engineering.
    """

    def __init__(self, features):
        self.features = features
        self.funcs_default = [FEUtil.sum_features]

    def add_fe(self, df: pd.DataFrame, use_funcs=None) -> pd.DataFrame:
        data = df.copy()
        if use_funcs is None:
            use_funcs = self.funcs_default
        for fun in use_funcs:
            data[f"EF_{fun.__name__}"] = fun(data.loc[:, self.features].values,
                                             axis=1)
        return data

    @classmethod
    def sum_features(cls, x, axis):
        return np.sum(x,  axis=axis)

    @classmethod
    def IQR(cls, x, axis):
        return np.quantile(x, 0.75, axis=axis) - np.quantile(x, 0.25, axis=axis)

    @classmethod
    def sharpe(cls, x, axis):
        return np.mean(x, axis=axis) / np.std(x, axis=axis)

    @classmethod
    def mode(cls, x, axis):
        return stats.mode(x, axis=axis, keepdims=False)[0]

    @classmethod
    def quantile01(cls, a, axis):
        return np.quantile(a, q=0.1, axis=axis)

    @classmethod
    def quantile02(cls, a, axis):
        return np.quantile(a, q=0.2, axis=axis)

    @classmethod
    def quantile08(cls, a, axis):
        return np.quantile(a, q=0.8, axis=axis)

    @classmethod
    def quantile09(cls, a, axis):
        return np.quantile(a, q=0.9, axis=axis)

    @classmethod
    def geometric(cls, x, axis):
        return np.prod(x, axis=axis)**(1/x.shape[1])

    @classmethod
    def entropy(cls, x, axis):
        return -1*(np.sum(x*np.log1p(x), axis=axis))

    @classmethod
    def get_base_stats(cls):

        return [FEUtil.sum_features, 
                np.mean, np.prod, np.std, stats.skew, stats.kurtosis,
                #FEUtil.sharpe,
                #FEUtil.mean,
                #FEUtil.max,
                #FEUtil.min,
                #FEUtil.median,
                #FEUtil.skew,
                #FEUtil.prod,
                FEUtil.geometric,
                #FEUtil.entropy
                ]


    @classmethod
    def get_quantile_stats(cls):
        """
        Removed model
        """
        return [np.min, FEUtil.quantile01, FEUtil.quantile02, np.median,
                FEUtil.quantile08,
                FEUtil.quantile09, np.max,
                FEUtil.IQR, np.ptp]

    @classmethod
    def get_all_stats(cls):
        return cls.get_base_stats() + cls.get_quantile_stats()

