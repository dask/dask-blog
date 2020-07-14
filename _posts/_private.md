
It's not clear to me how they missed the relevant
implementations in Dask-ML: all the implementations are in the same module,
including the basic module they test against (Dask-ML's `GridSearchCV`) and
modern techniques like Dask-ML's `HyperbandSearchCV`. These modern techniques
are featured prominently in the [Dask-ML's hyperparameter optimization
documentation][dml-hod], which clearly specifies the problems that may occur
during hyperparameter optimization.

