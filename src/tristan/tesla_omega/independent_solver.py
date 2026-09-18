from __future__ import annotations


def solve_lu_partial_pivot(matrix: list[list[complex]], rhs: list[complex]) -> tuple[complex,...]:
    n=len(matrix)
    if n==0 or len(rhs)!=n or any(len(row)!=n for row in matrix):
        raise ValueError("invalid linear system")
    a=[row[:] for row in matrix]
    b=rhs[:]
    for k in range(n):
        pivot=max(range(k,n),key=lambda i: abs(a[i][k]))
        if abs(a[pivot][k])<1e-18:
            raise ValueError("singular matrix")
        if pivot!=k:
            a[k],a[pivot]=a[pivot],a[k]
            b[k],b[pivot]=b[pivot],b[k]
        for i in range(k+1,n):
            factor=a[i][k]/a[k][k]
            a[i][k]=factor
            for j in range(k+1,n):
                a[i][j]-=factor*a[k][j]
            b[i]-=factor*b[k]
    x=[0j]*n
    for i in range(n-1,-1,-1):
        x[i]=(b[i]-sum(a[i][j]*x[j] for j in range(i+1,n)))/a[i][i]
    return tuple(x)


def max_solution_delta(a: tuple[complex,...], b: tuple[complex,...]) -> float:
    if len(a)!=len(b):
        raise ValueError("solution size mismatch")
    return max((abs(x-y) for x,y in zip(a,b)), default=0.0)
