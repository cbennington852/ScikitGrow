import sklearn
import sklearn.linear_model as lin
import sklearn.ensemble as ens
import sklearn.preprocessing as pre
import sklearn.model_selection as val
import sklearn.neural_network as neu
import sklearn.tree as tre

class SklearnAcceptableFunctions():
    REGRESSORS_LINEAR = {
        lin.ARDRegression,
        lin.BayesianRidge,
        lin.ElasticNet,
        lin.GammaRegressor,
        lin.HuberRegressor,
        lin.Lars,
        lin.Lasso,
        lin.LassoLars,
        lin.LassoLarsIC,
        lin.LinearRegression,
        lin.PassiveAggressiveRegressor,
        lin.PoissonRegressor,
        lin.QuantileRegressor,
        lin.RANSACRegressor,
        lin.Ridge,
        lin.SGDRegressor,
        lin.TheilSenRegressor,
        lin.TweedieRegressor
    }
    REGRESSORS_ENSEMBLE = {
        ens.AdaBoostRegressor,
        ens.BaggingRegressor,
        ens.ExtraTreesRegressor,
        ens.GradientBoostingRegressor,
        ens.HistGradientBoostingRegressor,
        ens.RandomForestRegressor,
        ens.StackingRegressor,
    }
    REGRESSORS_NEURAL_NETWORK = {
        neu.MLPRegressor
    }
    REGRESSORS_TREE = {
        tre.DecisionTreeRegressor,
        tre.ExtraTreeRegressor
    }

    REGRESSORS = REGRESSORS_ENSEMBLE | REGRESSORS_LINEAR | REGRESSORS_NEURAL_NETWORK | REGRESSORS_TREE

    CLASSIFIERS_LINEAR = {
        lin.LogisticRegression,
        lin.PassiveAggressiveClassifier,
        lin.Perceptron,
        lin.RidgeClassifier,
        lin.SGDClassifier,
    }

    CLASSIFIERS_ENSEMBLE = {
        ens.AdaBoostClassifier,
        ens.BaggingClassifier,
        ens.ExtraTreesClassifier,
        ens.GradientBoostingClassifier,
        ens.HistGradientBoostingClassifier,
        ens.RandomForestClassifier,
    }

    CLASSIFIERS_NEURAL = {
        neu.MLPClassifier
    }

    CLASSIFIERS_TREE = {
        tre.DecisionTreeClassifier,
        tre.ExtraTreeClassifier
    }

    # | is union in set
    CLASSIFIERS = CLASSIFIERS_ENSEMBLE | CLASSIFIERS_LINEAR | CLASSIFIERS_NEURAL | CLASSIFIERS_TREE

    def _multi_line_lambda_for_pre_processors():
        res = set()
        for function in dir(pre):
            if function[0] != '_' and function[0].isupper():
               res.add(getattr(pre , function)) # getattr fetches the higher order function.
        return res

    PREPROCESSORS = _multi_line_lambda_for_pre_processors()

    VALIDATORS = {
        val.KFold,
        val.StratifiedKFold,
        val.RepeatedKFold,
        val.RepeatedStratifiedKFold,
        val.LeaveOneOut,
        val.LeavePOut,
        val.LeaveOneGroupOut,
        val.LeavePGroupsOut,
        val.ShuffleSplit,
        val.StratifiedShuffleSplit,
        val.GroupShuffleSplit,
        val.GroupKFold,
        val.StratifiedGroupKFold,
        val.TimeSeriesSplit,
        val.PredefinedSplit,
    }

    MODELS = CLASSIFIERS | REGRESSORS

    
