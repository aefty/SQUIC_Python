from ctypes import *
import numpy as np
#import os
from scipy.sparse import csr_matrix, identity
from pathlib import Path

# QUICK FIX OMP ERROR
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

dll = None

def set_path(libSQUIC_path):

    global shared_lib_path
    global dll

    shared_lib_path = libSQUIC_path

    try:
        dll = CDLL(shared_lib_path)
        print("libSQUIC Successfully loaded!", dll)
        return True
    except Exception:
        return False

def check_if_exists(dll):
    return os.path.exists(dll)

def check_path():

    if dll != None:
        if check_if_exists(dll._name):
            print(dll)
            print("libSQUIC already loaded.")
            return True
        else:
            print(f"libSQUIC not found : {dll}")
            return False
    else:
        home_dir = str(Path.home())
        file_name_dylib = "/libSQUIC.dylib"
        file_name_so = "/libSQUIC.so"

        if set_path(home_dir + file_name_dylib) or set_path(home_dir + file_name_so):

            return True
        else:
            print("libSQUIC path not set correctly or library not yet downloaded. Add path by calling: set_path(libSQUIC_path).")
            return False

def get_path():
	print("current libSQUIC path:")
	print(dll)

def SQUIC(Y, l, max_iter=100, inv_tol=1e-3, term_tol=1e-3,verbose=1, M=None, X0=None, W0=None):
	"""
	:param Y: Data matrix p x p consisting of p>2 random variables and n>1 samples.
	:param l: Sparsity parameter as a nonzero positive scalar.
	:param max_iter: [default 100] Maximum number of Newton iterations as a nonnegative integer
	:param inv_tol: [default 1e-3] Termination tolerance as a nonzero positive scalar.
	:param term_tol: [default 1e-3] Dropout tolerance as a nonzero positive scalar.
	:param verbose: [default 1] Verbosity level as 0 or 1.
	:param M: [default None] Sparsity structure matrix as a sparse p x p matrix.
	:param X0: [default None] Initial value of precision matrix as a sparse p x p matrix.
	:param W0: [default None] Initial value of inverse precision matrix as a sparse p x p  matrix.
	:return: [X,W,info_times,info_objective,info_logdetX,info_trSX]
		:return: X: Precision matrix as a sparse p x p matrix.
		:return: W: Inverse precision matrix as a sparse p x p matrix.
		:return: info_times: List of different compute times.
		:return: info_objective: List of objective function values at each Newton iteration.
		:return: info_logdetX: Log-determinant of the final precision matrix.
		:return: info_trSX: Trace of sample covariance matrix times the final precision matrix.
	"""

	if not check_path():
		return

	# if mode = [0,1,2,3,4] we Block-SQUIC or [5,6,7,8,9] Scalar-SQUIC
	mode = c_int(0)

	p,n= Y.shape

	# The data needs to be fortran (column major)
	Y=np.array(Y,order='F')
	Y_ptr   = Y.ctypes.data_as(POINTER(c_double))

	#################################################
	# Matricis
	#################################################
	
	# X Matrix
	if(X0==None):
		X0= identity(p, dtype='float64', format='csr')

	X_rinx = POINTER(c_long)()
	X_cptr = POINTER(c_long)()
	X_val  = POINTER(c_double)()
	X_nnz  = c_long(X0.nnz)	

	# Use the SQUIC_CPP utility functino for creating and populating data buffers. 
	# This makes creating and delete buffers consistent.
	# All SQUIC datastructions are 64 bit! Thus we need to cast the CSR index buffers to int64
	dll.SQUIC_CPP_UTIL_memcopy_integer(byref(X_rinx) , np.int64(X0.indices).ctypes.data_as(POINTER(c_long))  , X_nnz       )
	dll.SQUIC_CPP_UTIL_memcopy_integer(byref(X_cptr) , np.int64(X0.indptr).ctypes.data_as(POINTER(c_long))   , c_long(p+1) )
	dll.SQUIC_CPP_UTIL_memcopy_double( byref(X_val)  , X0.data.ctypes.data_as(POINTER(c_double))             , X_nnz       )

	# W Matrix
	if(W0==None):
		W0= identity(p, dtype='float64', format='csr')

	W_rinx = POINTER(c_long)()
	W_cptr = POINTER(c_long)()
	W_val  = POINTER(c_double)()
	W_nnz  = c_long(W0.nnz)

	dll.SQUIC_CPP_UTIL_memcopy_integer(byref(W_rinx) , np.int64(W0.indices).ctypes.data_as(POINTER(c_long))  , W_nnz       )
	dll.SQUIC_CPP_UTIL_memcopy_integer(byref(W_cptr) , np.int64(W0.indptr).ctypes.data_as(POINTER(c_long))   , c_long(p+1) )
	dll.SQUIC_CPP_UTIL_memcopy_double( byref(W_val)  , W0.data.ctypes.data_as(POINTER(c_double))             , W_nnz       )

	# M Matrix
	M_rinx = POINTER(c_long)()
	M_cptr = POINTER(c_long)()
	M_val  = POINTER(c_double)()
	
	if(M==None):
		M_nnz  = c_long(0)
	else:
		M_nnz  = c_long(M.nnz)
		dll.SQUIC_CPP_UTIL_memcopy_integer(byref(M_rinx) , np.int64(M.indices).ctypes.data_as(POINTER(c_long))  , M_nnz       )
		dll.SQUIC_CPP_UTIL_memcopy_integer(byref(M_cptr) , np.int64(M.indptr).ctypes.data_as(POINTER(c_long))   , c_long(p+1) )
		dll.SQUIC_CPP_UTIL_memcopy_double( byref(M_val)  , M.data.ctypes.data_as(POINTER(c_double))             , M_nnz       )


	#################################################
	# Parameters
	#################################################
	max_iter_ptr  = c_int(max_iter);
	term_tol_ptr  = c_double(term_tol);
	inv_tol_ptr  = c_double(inv_tol);
	verbose_ptr   = c_int(verbose)

	p_ptr    = c_long(p)
	n_ptr    = c_long(n)
	l_ptr    = c_double(l)

	#################################################
	# Information output buffers
	#################################################
	info_num_iter_ptr    = c_int(-1);
	info_logdetX_ptr     = c_double(-1);
	info_trSX_ptr        = c_double(-1);

	info_times_ptr = POINTER(c_double)()
	dll.SQUIC_CPP_UTIL_memset_double(byref(info_times_ptr),c_int(6))

	info_objective_ptr = POINTER(c_double)()
	dll.SQUIC_CPP_UTIL_memset_double(byref(info_objective_ptr),max_iter_ptr)

	#################################################
	# Run SQUIC
	#################################################
	dll.SQUIC_CPP(mode,
		p_ptr, n_ptr, Y_ptr,
		l_ptr, 
		M_rinx, M_cptr, M_val, M_nnz,
		max_iter_ptr, inv_tol_ptr, term_tol_ptr, verbose_ptr,
		byref(X_rinx), byref(X_cptr), byref(X_val), byref(X_nnz),
		byref(W_rinx), byref(W_cptr), byref(W_val), byref(W_nnz),
		byref(info_num_iter_ptr),
		byref(info_times_ptr),	   # length must be 6: [time_total,time_impcov,time_optimz,time_factor,time_aprinv,time_updte]
		byref(info_objective_ptr), # length must be size max_iter
		byref(info_logdetX_ptr),
		byref(info_trSX_ptr))


	#################################################
	# Transfer Restusl from C to Python
	#################################################
	
	#Convert all scalars values back python
	p               = p_ptr.value
	X_nnz           = X_nnz.value
	W_nnz           = W_nnz.value
	info_num_iter   = info_num_iter_ptr.value
	info_logdetX    = info_logdetX_ptr.value
	info_trSX       = info_trSX_ptr.value

	# Transfer Matrix from C to Python
	# First we link the C buffer to a numpy array, than we make CSR matrix using a Copy of the array.
	
	X_rinx_py	=np.ctypeslib.as_array(X_rinx,(X_nnz,))
	X_cptr_py	=np.ctypeslib.as_array(X_cptr,(p+1,))
	X_val_py	=np.ctypeslib.as_array(X_val,(X_nnz,))
	X 			=csr_matrix((X_val_py, X_rinx_py, X_cptr_py),shape=(p, p),copy=True)

	W_rinx_py	=np.ctypeslib.as_array(W_rinx,(W_nnz,))
	W_cptr_py	=np.ctypeslib.as_array(W_cptr,(p+1,))
	W_val_py	=np.ctypeslib.as_array(W_val,(W_nnz,))
	W 			=csr_matrix((W_val_py, W_rinx_py, W_cptr_py),shape=(p, p),copy=True)

	temp			=np.ctypeslib.as_array(info_objective_ptr,(info_num_iter,))
	info_objective	=np.array(temp,copy=True)

	temp			=np.ctypeslib.as_array(info_times_ptr,(6,))
	info_times   	=np.array(temp,copy=True)

	#################################################
	# Transfer Restusl from C to Python
	#################################################
	dll.SQUIC_CPP_UTIL_memfree_integer(byref(X_rinx))
	dll.SQUIC_CPP_UTIL_memfree_integer(byref(X_cptr))
	dll.SQUIC_CPP_UTIL_memfree_double(byref(X_val))
	
	dll.SQUIC_CPP_UTIL_memfree_integer(byref(W_rinx))
	dll.SQUIC_CPP_UTIL_memfree_integer(byref(W_cptr))
	dll.SQUIC_CPP_UTIL_memfree_double(byref(W_val))

	if(M!=None):
		dll.SQUIC_CPP_UTIL_memfree_integer(byref(M_rinx))
		dll.SQUIC_CPP_UTIL_memfree_integer(byref(M_cptr))
		dll.SQUIC_CPP_UTIL_memfree_double(byref(M_val))

	dll.SQUIC_CPP_UTIL_memfree_double(byref(info_objective_ptr))
	dll.SQUIC_CPP_UTIL_memfree_double(byref(info_times_ptr))

	return [X,W,info_times,info_objective,info_logdetX,info_trSX]

def SQUIC_S(Y, l,verbose=1, M=None):
	"""
	:param Y:
	:param l:
	:param verbose:
	:param M:
	:return: [S, info_times]
		:return: S: sparse(thresholded) sample covariance matrix.
		:return: info_times: List of different compute times.
	"""

	[_,S,info_times,_,_,_]=SQUIC(Y=Y, l=l, max_iter=0, verbose=verbose, M=M)

	return [S,info_times]


