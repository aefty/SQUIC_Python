## SQUIC for Python
### Sparse Quadratic Inverse Covariance Estimation
This is the SQUIC algorithm, made available as a Python package.
Description
SQUIC tackles the statistical problem of estimating large sparse 
inverse covariance matrices. This estimation poses an ubiquitous 
problem that arises in many applications e.g. coming from the 
fields mathematical finance, geology and health. 
SQUIC belongs to the class of second-order L1-regularized 
Gaussian maximum likelihood methods and is especially suitable 
for high-dimensional datasets with limited number of samples. 
For further details please see the listed references.

### References

[1] Bollhöfer, M., Eftekhari, A., Scheidegger, S. and Schenk, O., 2019. Large-scale sparse inverse covariance matrix estimation. SIAM Journal on Scientific Computing, 41(1), pp.A380-A401.

[2] Eftekhari, A., Bollhöfer, M. and Schenk, O., 2018, November. Distributed memory sparse inverse covariance matrix estimation on high-performance computing architectures. In SC18: International Conference for High Performance Computing, Networking, Storage and Analysis (pp. 253-264). IEEE.

### Installation

Before using SQUIC_Python for the first time, the pre-compiled library 
libSQUIC needs to be installed from https://github.com/aefty/SQUIC_Release_Source.

The libSQUIC(.dylib/.so) file will by default be installed in your home directory. 
This way the SQUIC_Python package will find it automatically. Otherwise you can manually 
set the path using

```angular2
import SQUIC_Python as SQ
SQ.set_path("/path/to/libSQUIC(.dylib/.so)")
```

We are currently supporting Linux and MacOS distributions.

### Example

```angular2
import SQUIC_Python as SQ
import numpy as np

# generate sample from tridiagonal precision matrix

# number of covariates p
p = 1000
# number of samples n
n = 100

# define tridiagonal precision matrix iC_star
a = -0.5 * np.ones(p-1)
b = 1.25 * np.ones(p)
iC_star = np.diag(a,-1) + np.diag(b,0) + np.diag(a,1)

# compute Cholesky factorisation
L = np.linalg.cholesky(iC_star)

# sample from standard normal distribution & solve
# Y contains n samples from multivariate Gaussian distribution
# with zero mean and precision matrix iC_star
Y = np.linalg.solve(L.T,np.random.randn(p,n))

# set regularisation parameter lambda
l = 0.3
# compute sample covariance matrix
[S,info_times] = SQ.SQUIC_S(Y, l)

# compute sparse precision matrix and its inverse
[X,W,info_times,info_objective,info_logdetX,info_trSX] = SQ.SQUIC(Y,l)

# X contains estimate for iC_star
# W contains inverse of X
```

For a detailed list of all (optional) input and output parameters: 

```angular2
help(SQ.SQUIC_S)
help(SQ.SQUIC)
```
