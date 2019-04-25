from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.datasets import load_boston
model = LinearRegression(fit_intercept=True)

boston = load_boston()
print(boston)

# rng = np.random.RandomState(1)
# x = 10 * rng.rand(50)
# print(x)
# x = np.array([1,1,2,3,4,5,6,7])
# x = np.array([[1],[1],[2],[3],[4],[5],[6],[7]])
# print(x)
# y = np.array([10,11,12,13,14,15,16,17])
# lm = LinearRegression()
# lm.fit(x, y)
#
# print(lm.intercept_)
# print(lm.coef_)

