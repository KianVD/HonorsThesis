"""Data analysis program to compare different fits (linear, exponential etc.) for a dataset using aic"""

import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures

# 1. Your data points
x = np.array([8, 9, 10, 11, 12, 13])
y = np.array([206, 207, 546, 1247, 2995, 7671])
x = x.reshape(-1,1)

aic_dict = {}

#fit linear model
linear_xp = PolynomialFeatures(degree=1).fit_transform(x)
linear_model = sm.OLS(y,linear_xp).fit()
aic_dict["linear"] = linear_model.aic

#fit quadratic model
quad_xp =  PolynomialFeatures(degree = 2).fit_transform(x)
quadratic_model = sm.OLS(y,quad_xp).fit()
aic_dict["quad"] = quadratic_model.aic

#fit cubic model
cubic_xp =  PolynomialFeatures(degree = 3).fit_transform(x)
cubic_model = sm.OLS(y,cubic_xp).fit()
aic_dict["cubic"] = cubic_model.aic

#fit exponential model
# transform y
log_y = np.log(y)
# add constant (intercept)
exp_x = sm.add_constant(x)
exp_model = sm.OLS(log_y, exp_x).fit()

#compare all using aic
maxaic = -np.inf
maxfunc = ""
print(aic_dict)
for k,v in aic_dict.items():
    if v > maxaic:
        maxaic = v
        maxfunc = k

print(maxfunc)
print(maxaic)