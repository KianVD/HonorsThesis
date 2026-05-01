"""Data analysis program to compare different fits (linear, exponential etc.) for a dataset using aic"""

import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt

x = np.array([8, 9, 10, 11, 12, 13,14])#length
y = np.array([206, 207, 546, 1247, 2995, 7671,12257])#time

#x = np.array([8, 9, 10, 11, 12, 13,14,15])#length
#y = np.array([1854,8311,36123,157974,679930,2912744,12364068,52207488])#cfnum

#x = np.array([8, 9, 10, 11, 12, 13])#length
#y = np.array([182.32362459546925,398.888,948.331,2003.137,4538.432,10018.938])#avgfs
x = x.reshape(-1,1)

class ModelComparison():
    def __init__(self):
        self.aic_dict = {}
    def fit_models(self,x,y):

        

        #fit linear model
        linear_xp = PolynomialFeatures(degree=1).fit_transform(x)
        print(linear_xp)
        linear_model = sm.OLS(y,linear_xp).fit()
        self.aic_dict["linear"] = linear_model.aic,linear_model

        #fit quadratic model
        quad_xp =  PolynomialFeatures(degree = 2).fit_transform(x)
        quadratic_model = sm.OLS(y,quad_xp).fit()
        self.aic_dict["quad"] = quadratic_model.aic,quadratic_model

        #fit cubic model
        cubic_xp =  PolynomialFeatures(degree = 3).fit_transform(x)
        cubic_model = sm.OLS(y,cubic_xp).fit()
        self.aic_dict["cubic"] = cubic_model.aic,cubic_model

        #fit exponential model
        log_y = np.log(y)
        exp_x = sm.add_constant(x)
        exp_model = sm.OLS(log_y, exp_x).fit()

        # convert predictions back to original scale
        y_hat = np.exp(exp_model.fittedvalues)

        # compute residuals in original space
        resid = y - y_hat

        n = len(y)
        sigma2 = np.mean(resid**2)

        # AIC approximation for Gaussian errors
        aic_exp = n * np.log(sigma2) + 2 * len(exp_model.params)

        self.aic_dict["exp"] = aic_exp, exp_model

    def compare(self):
        #compare all using aic
        bestaic = np.inf
        bestfunc = ""
        for k,v in self.aic_dict.items():
            print(v[0])
            if v[0] < bestaic:
                bestaic = v[0]
                bestfunc = k


        print(bestfunc)
        print(bestaic)

        model = self.aic_dict[bestfunc][1]
        x1 = np.array([[15]])
        if bestfunc == "exp":
            x1p = sm.add_constant(x1,has_constant="add")
            pred = np.exp(model.predict(x1p))
        else:
            
            degree_lib = {"linear":1,"quad":2,"cubic":3}
            x1p = PolynomialFeatures(degree = degree_lib[bestfunc]).fit_transform(x1)
            pred = model.predict(x1p)
        print(f"prediction for {x1} {pred}" )

        
        plt.scatter(x, y)
        x1p = sm.add_constant(x,has_constant="add")
        pred = np.exp(self.aic_dict["exp"][1].predict(x1p))
        plt.plot(x,pred)

        x1p = PolynomialFeatures(degree = 3).fit_transform(x)
        pred = self.aic_dict["cubic"][1].predict(x1p)
        plt.plot(x,pred)
        plt.show()

def main():
    mc = ModelComparison()
    mc.fit_models(x,y)
    mc.compare()

if __name__ == "__main__":
    main()