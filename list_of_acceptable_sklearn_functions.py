import sklearn
import sklearn.linear_model as lin
import sklearn.ensemble as ens
import sklearn.preprocessing as pre
import sklearn.neural_network as neu
import sklearn.tree as tre

class SklearnAcceptableFunctions():
    REGRESSORS_LINEAR = [
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
    ]
    REGRESSORS_ENSEMBLE = [
        ens.AdaBoostRegressor,
        ens.BaggingRegressor,
        ens.ExtraTreesRegressor,
        ens.GradientBoostingRegressor,
        ens.HistGradientBoostingRegressor,
        ens.RandomForestRegressor,
        ens.StackingRegressor,
    ]
    REGRESSORS_NEURAL_NETWORK = [
        neu.MLPRegressor
    ]
    REGRESSORS_TREE = [
        tre.DecisionTreeRegressor,
        tre.ExtraTreeRegressor
    ]

    CLASSIFIERS_LINEAR = [
        lin.LogisticRegression,
        lin.PassiveAggressiveClassifier,
        lin.Perceptron,
        lin.RidgeClassifier,
        lin.SGDClassifier,
    ]

    CLASSIFIERS_ENSEMBLE = [
        ens.AdaBoostClassifier,
        ens.BaggingClassifier,
        ens.ExtraTreesClassifier,
        ens.GradientBoostingClassifier,
        ens.HistGradientBoostingClassifier,
        ens.RandomForestClassifier,
    ]

    CLASSIFIERS_NEURAL = [
        neu.MLPClassifier
    ]

    CLASSIFIERS_TREE = [
        tre.DecisionTreeClassifier,
        tre.ExtraTreeClassifier
    ]