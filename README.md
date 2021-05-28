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


### Example

if libSQUIC(.dylib/.so) is in home directory 
package will find it, otherwise set

```angular2
import SQUICpy as sp
pyS.set_path("/path/to/libSQUIC")
```

To run tests:

```angular2
import SQUICpy.test 
SQUICpy.test.run_SQUIC_S()
SQUICpy.test.run_SQUIC()
SQUICpy.test.run_SQUIC_M()
```

For regular SQUIC calls:

```angular2
import SQUICpy as sp
import SQUICpy.test
Y = SQUICpy.test.generate_sample(8, 200)
l = 0.5
sp.SQUIC_S(Y,l)
sp.SQUIC(Y,l)
```

optional parameters ...