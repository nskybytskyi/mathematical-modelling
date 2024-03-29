#!/usr/bin/env python
import scipy.integrate as integrate
import typing as tp
import numpy as np


# section 1 subsection 1 problem 1
def solve_system(
        a: np.matrix,
        b: np.array) -> np.array:
    """
    :param a: m times n real matrix
    :param b: m-dimensional real vector
    :return: n-dimensional real vector x,
        least squares solution to A x = b.
    """
    return np.linalg.pinv(a) * b


# section 1 subsection 2 problem 1
def solve_summed_system(
        as_list: tp.List[np.matrix],
        b: np.array,
) -> tp.List[np.array]:
    """
    :param as_list: list of length N,
        consisting of m times n real matrices A_i
    :param b: m-dimensional real vector
    :return: list x of length N,
        consisting of n-dimensional real vectors x_i,
        least squares solution to sum_{i = 1}^N A_i x_i = b.
    """
    p_1 = sum(a_i * a_i.T for a_i in as_list)
    return [a_i.T * np.linalg.pinv(p_1) * b for a_i in as_list]


# section 1 subsection 2 problem 2
def solve_time_summed_system(
        a: tp.Callable[[float], np.matrix],
        b: np.array,
        t: tp.List[float],
) -> tp.List[np.array]:
    """
    :param a: matrix-valued function of time.
        Maps t_i to m times n real matrix A(t_i)
    :param b: m-dimensional real vector
    :param t: list of length N,
        consisting of time moments, t_i
    :return: list x of length N,
        consisting of n-dimensional real vectors x(t_i),
        least squares solution to sum_{i = 1}^N A(t_i) x(t_i) = b.
    """
    as_list = [a(t_i) for t_i in t]
    return solve_summed_system(as_list, b)


# section 1 subsection 3 problem 1
def solve_distributed_system(
        as_list: tp.List[np.matrix],
        bs_list: tp.List[np.array],
) -> np.array:
    """
    :param as_list: list of length N,
        consisting of m times n real matrices A_i
    :param bs_list: list of length N,
        consisting of m-dimensional real vectors b_i
    :return: n-dimensional real vector x,
        least squares solution to A_i x = b_i, i = 1..N.
    """
    a_b = sum(a_i.T * b_i for a_i, b_i in zip(as_list, bs_list))
    p_2 = sum(a_i.T * a_i for a_i in as_list)
    return np.linalg.pinv(p_2) * a_b


# section 1 subsection 3 problem 2
def solve_time_distributed_system(
        a: tp.Callable[[float], np.matrix],
        b: tp.Callable[[float], np.array],
        t: tp.List[float],
) -> np.array:
    """
    :param a: matrix-valued function of time.
        Maps t_i to m times n real matrix A(t_i)
    :param b: vector-valued function of time.
        Maps t_i to m-dimensional real vector b(t_i)
    :param t: list of length N,
        consisting of time moments, t_i
    :return: n-dimensional real vector x,
        least squares solution to A(t_i) x = b(t_i), i = 1..N.
    """
    as_list = [a(t_i) for t_i in t]
    bs_list = [b(t_i) for t_i in t]
    return solve_distributed_system(as_list, bs_list)


# section 1 subsection 4 problem 1
def solve_integral_system(
        a: tp.Callable[[float], np.matrix],
        b: np.array,
        T: float,
) -> tp.Callable[[float], np.array]:
    """
    :param a: matrix-valued function of time.
        Maps t to m times n real matrix A(t)
    :param b: m-dimensional real vector
    :param T: end time
    :return: vector-valued function of time.
        Maps t to n-dimensional real vector x(t),
        least squares solution to int_0^T A(t) x(t) dt = b.
    """
    m, _ = (a(0) * a(0).T).shape

    p_1 = np.matrix([[integrate.quad(
        lambda t: (a(t) * a(t).T)[i, j], 0, T
    )[0] for j in range(m)] for i in range(m)])

    def x(t: float) -> np.array:
        return a(t).T * np.linalg.pinv(p_1) * b

    return x


# section 1 subsection 4 problem 2
def solve_functional_system(
        a: tp.Callable[[float], np.matrix],
        b: tp.Callable[[float], np.array],
        T: float,
) -> np.array:
    """
    :param a: matrix-valued function of time.
        Maps t to m times n real matrix A(t)
    :param b: vector-valued function of time.
        Maps t to m-dimensional real vector b(t)
    :param T: end time
    :return: n-dimensional real vector x,
        least squares solution to A(t) x = b(t), t in [0, T].
    """
    n, _ = (a(0).T * b(0)).shape

    a_b = np.array([[integrate.quad(
        lambda t: (a(t).T * b(t))[i], 0, T
    )[0]] for i in range(n)])

    p_2 = np.matrix([[integrate.quad(
        lambda t: (a(t).T * a(t))[i, j], 0, T
    )[0] for j in range(n)] for i in range(n)])

    return np.linalg.pinv(p_2) * a_b


# section 1 subsection 5 problem 1 dimensionality 1
def solve_1d_space_distributed_integral_system(
        g: tp.Callable[[float, float], float],
        us_list: tp.List[float],
        xts_list: tp.List[tp.Tuple[float, float]],
        a: float,
        b: float,
        T: float,
) -> tp.Callable[[float, float], float]:
    """
    :param g: real-valued function of space and time.
        Maps x, t to G(x, t)
    :param us_list: list of N real values, u(x_i, t_i)
    :param xts_list: list of length N,
        consisting of space-time points (x_i, t_i).
        The equation is optimized at these points
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param T: end time
    :return: real-valued function f of space and time,
        least squares solutions to
        int_a^b int_0^T G(x - x_i, t - t_i) f(x, t) dt dx
            = u(x_i, t_i), i = 1..N.
    """

    class GfuncComputer:
        def __init__(self, x: float, t: float) -> None:
            self._x, self._t = x, t

        def __call__(self, x: float, t: float) -> float:
            return g(self._x - x, self._t - t)

    g_1 = [GfuncComputer(x_i, t_i) for x_i, t_i in xts_list]

    vec_u = np.array([[u_i] for u_i in us_list])

    p_1 = np.matrix([[integrate.dblquad(
        lambda t, x: g_i(x, t) * g_j(x, t), a, b, 0, T
    )[0] for g_j in g_1] for g_i in g_1])

    def f(x: float, t: float) -> float:
        g_1_local = np.array([g_i(x, t) for g_i in g_1])
        return (g_1_local * np.linalg.pinv(p_1) * vec_u)[0, 0]

    return f


def solve_1d_space_distributed_integral_system_ufunc(
        g: tp.Callable[[float, float], float],
        u: tp.Callable[[float, float], float],
        xts_list: tp.List[tp.Tuple[float, float]],
        a: float,
        b: float,
        T: float,
) -> tp.Callable[[float, float], float]:
    """
    :param g: real-valued function of space and time.
        Maps x, t to G(x, t)
    :param u: real-valued function of space and time.
        Maps x, t to u(x, t)
    :param xts_list: list of length N,
        consisting of space-time points (x_i, t_i).
        The equation is optimized at these points
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param T: end time
    :return: real-valued function f of space and time,
        least squares solutions to
        int_a^b int_0^T G(x - x_i, t - t_i) f(x, t) dt dx
            = u(x_i, t_i), i = 1..N.
    """
    us_list = [u(x_i, t_i) for x_i, t_i in xts_list]

    return solve_1d_space_distributed_integral_system(
        g, us_list, xts_list, a, b, T)


# section 1 subsection 5 problem 1 dimensionality 2
def solve_2d_space_distributed_integral_system(
        g: tp.Callable[[float, float, float], float],
        us_list: tp.List[float],
        xyts_list: tp.List[tp.Tuple[float, float, float]],
        a: float,
        b: float,
        c: float,
        d: float,
        T: float,
) -> tp.Callable[[float, float, float], float]:
    """
    :param g: real-valued function of space and time.
        Maps x, y, t to G(x, y, t)
    :param us_list: list of length N,
        consisting of real values u(x_i, y_i, t_i)
    :param xyts_list: list of length N,
        consisting of space-time points (x_i, y_i, t_i).
        The equation is optimized at these points
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param c: lower bound of the y-domains of g and u
    :param d: upper bound of the y-domains of g and u
    :param T: end time
    :return: real-valued function f of space and time,
        least squares solutions to
        int_c^d int_a^b int_0^T G(x - x_i, y - y_i, t - t_i) f(x, y, t) dt dx dy
            = u(x_i, y_i, t_i), i = 1..N.
    """

    class GfuncComputer:
        def __init__(self, x: float, y: float, t: float) -> None:
            self._x, self._y, self._t = x, y, t

        def __call__(self, x: float, y: float, t: float) -> float:
            return g(self._x - x, self._y - y, self._t - t)

    g_1 = [GfuncComputer(x_i, y_i, t_i) for x_i, y_i, t_i in xyts_list]

    vec_u = np.array([[u_i] for u_i in us_list])

    p_1 = np.matrix([[integrate.tplquad(
        lambda t, x, y: g_i(x, y, t) * g_j(x, y, t), c, d, a, b, 0, T
    )[0] for g_j in g_1] for g_i in g_1])

    def f(x: float, y: float, t: float) -> float:
        g_1_local = np.array([g_i(x, y, t) for g_i in g_1])
        return (g_1_local * np.linalg.pinv(p_1) * vec_u)[0, 0]

    return f


def solve_2d_space_distributed_integral_system_ufunc(
        g: tp.Callable[[float, float, float], float],
        u: tp.Callable[[float, float, float], float],
        xyts_list: tp.List[tp.Tuple[float, float, float]],
        a: float,
        b: float,
        c: float,
        d: float,
        T: float,
) -> tp.Callable[[float, float, float], float]:
    """
    :param g: real-valued function of space and time.
        Maps x, y, t to G(x, y, t)
    :param u: real-valued function of space and time.
        Maps x, y, t to u(x, y, t)
    :param xyts_list: list of length N,
        consisting of space-time points (x_i, y_i, t_i).
        The equation is optimized at these points
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param c: lower bound of the y-domains of g and u
    :param d: upper bound of the y-domains of g and u
    :param T: end time
    :return: real-valued function f of space and time,
        least squares solutions to
        int_c^d int_a^b int_0^T G(x - x_i, y - y_i, t - t_i) f(x, y, t) dt dx dy
            = u(x_i, y_i, t_i), i = 1..N.
    """
    us_list = [u(x_i, y_i, t_i) for x_i, y_i, t_i in xyts_list]

    return solve_2d_space_distributed_integral_system(
        g, us_list, xyts_list, a, b, c, d, T)


# section 1 subsection 5 problem 2 dimensionality 1
def solve_1d_space_distributed_functional_system(
        g: tp.Callable[[float, float], float],
        u: tp.Callable[[float, float], float],
        xts_list: tp.List[tp.Tuple[float, float]],
        a: float,
        b: float,
        T: float,
) -> np.array:
    """
    :param g: real-valued function of space and time.
        Maps x, t to G(x, t)
    :param u: real-valued function of space and time.
        Maps x, t to u(x, t)
    :param xts_list: list of length N,
        consisting of space-time points (x_i, t_i).
        The equation is optimized at these points
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param T: end time
    :return: N-dimensional real vector, f(x_i, t_i), i = 1..N,
        least squares solutions to
        G(x - x_i, t - t_i) f(x_i, t_i) = u(x, t), x in [a, b], t in [0, T].
    """

    class GfuncComputer:
        def __init__(self, x: float, t: float) -> None:
            self._x, self._t = x, t

        def __call__(self, x: float, t: float) -> float:
            return g(self._x - x, self._t - t)

    g_2 = [GfuncComputer(x_i, t_i) for x_i, t_i in xts_list]

    p_2 = np.matrix([[integrate.dblquad(
        lambda t, x: g_i(x, t) * g_j(x, t), a, b, 0, T
    )[0] for g_j in g_2] for g_i in g_2])

    g_u = np.array([[integrate.dblquad(
        lambda t, x: g_i(x, t) * u(x, t), a, b, 0, T
    )[0]] for g_i in g_2])

    return np.linalg.pinv(p_2) * g_u


# section 1 subsection 5 problem 2 dimensionality 2
def solve_2d_space_distributed_functional_system(
        g: tp.Callable[[float, float, float], float],
        u: tp.Callable[[float, float, float], float],
        xyts_list: tp.List[tp.Tuple[float, float, float]],
        a: float,
        b: float,
        c: float,
        d: float,
        T: float,
) -> np.array:
    """
    :param g: real-valued function of space and time.
        Maps x, y, t to G(x, y, t)
    :param u: real-valued function of space and time.
        Maps x, y, t to u(x, y, t)
    :param xyts_list: list of length N,
        consisting of space-time points (x_i, y_i, t_i).
        The equation is optimized at these points
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param c: lower bound of the y-domains of g and u
    :param d: upper bound of the y-domains of g and u
    :param T: end time
    :return: N-dimensional real vector, f(x_i, y_i, t_i), i = 1..N,
        least squares solutions to
        G(x - x_i, y - y_i, t - t_i) f(x_i, y_i, t_i) = u(x, y, t),
        x in [a, b], y in [c, d], t in [0, T].
    """

    class GfuncComputer:
        def __init__(self, x: float, y: float, t: float) -> None:
            self._x, self._y, self._t = x, y, t

        def __call__(self, x: float, y: float, t: float) -> float:
            return g(self._x - x, self._y - y, self._t - t)

    g_2 = [GfuncComputer(x_i, y_i, t_i) for x_i, y_i, t_i in xyts_list]

    p_2 = np.matrix([[integrate.tplquad(
        lambda t, x, y: g_i(x, y, t) * g_j(x, y, t), c, d, a, b, 0, T
    )[0] for g_j in g_2] for g_i in g_2])

    g_u = np.array([[integrate.tplquad(
        lambda t, x, y: g_i(x, y, t) * u(x, y, t), c, d, a, b, 0, T
    )[0]] for g_i in g_2])

    return np.linalg.pinv(p_2) * g_u


# discrete observations discrete modelling functions dimensionality 1
def solve_1d_discrete_observations_discrete_modelling(
        cond_x0s_list: tp.List[float],
        cond_xtGammas_list: tp.List[tp.Tuple[float, float]],
        cond_f0s_list: tp.List[float],
        cond_fGammas_list: tp.List[float],
        model_xtInfs_list: tp.List[tp.Tuple[float, float]],
        model_x0s_list: tp.List[float],
        model_xtGammas_list: tp.List[tp.Tuple[float, float]],
        f: tp.Callable[[float, float], float],
        g: tp.Callable[[float, float], float],
) -> tp.Callable[[float, float], float]:
    """
    :param cond_x0s_list: list of space points for initial conditions:
        u(cond_x0_i, 0) = cond_f0_i
    :param cond_xtGammas_list: list of space-time for boundary conditions:
        u(cond_xGamma_i, cond_tGamma_i) = cond_fGamma_i
    :param cond_f0s_list: list of real values for initial conditions:
        cond_f0_i = u(cond_x0_i, 0)
    :param cond_fGammas_list: list of real values for boundary conditions:
        cond_fGamma_i = u(cond_xGamma_i, cond_tGamma_i)
    :param model_xtInfs_list: list of modelling space-time points for f_infty
    :param model_x0s_list: list of modelling space points for f_0
    :param model_xtGammas_list: list of modelling points space-time for f_Gamma
    :param f: real-valued function of space and time,
        represents external perturbations in the system.
    :param g: Green's function of the linear differential operator L
    :return: real-valued function u of space and time,
        least squares solution to L u(x, t) = f(x, t)
        under initial conditions u(cond_x0_i, 0) = cond_f0_i,
        and boundary conditions u(cond_xGamma_i, cond_tGamma_i) = cond_fGamma_i.
    """

    def u_infty(x: float, t: float) -> float:
        return sum(
            g(x - model_xInf_i, t - model_tInf_i) * f(model_xInf_i, model_tInf_i)
            for model_xInf_i, model_tInf_i in model_xtInfs_list
        )

    vec_u0 = np.array([[
        cond_f0_i - u_infty(cond_x0_i, 0.0)
    ] for cond_f0_i, cond_x0_i in zip(cond_f0s_list, cond_x0s_list)])

    vec_uGamma = np.array([[
        cond_fGamma_i - u_infty(cond_xtGamma_i[0], cond_xtGamma_i[1])
    ] for cond_fGamma_i, cond_xtGamma_i in zip(cond_fGammas_list, cond_xtGammas_list)])

    vec_u = np.vstack((vec_u0, vec_uGamma))

    A11 = np.matrix([[g(
        cond_x0_i - model_x0_i,
        0.0 - 0.0,
    ) for model_x0_i in model_x0s_list] for cond_x0_i in cond_x0s_list])

    A12 = np.matrix([[g(
        cond_x0_i - model_xtGamma_i[0],
        0.0 - model_xtGamma_i[1],
    ) for model_xtGamma_i in model_xtGammas_list] for cond_x0_i in cond_x0s_list])

    A21 = np.matrix([[g(
        cond_xtGamma_i[0] - model_x0_i,
        cond_xtGamma_i[1] - 0.0,
    ) for model_x0_i in model_x0s_list] for cond_xtGamma_i in cond_xtGammas_list])

    A22 = np.matrix([[g(
        cond_xtGamma_i[0] - model_xtGamma_i[0],
        cond_xtGamma_i[1] - model_xtGamma_i[1],
    ) for model_xtGamma_i in model_xtGammas_list] for cond_xtGamma_i in cond_xtGammas_list])

    A = np.vstack((np.hstack((A11, A12)), np.hstack((A21, A22))))

    vec_f = np.linalg.pinv(A) * vec_u

    len0, lenGamma = len(model_x0s_list), len(model_xtGammas_list)

    vec_f0, vec_fGamma = vec_f[:len0], vec_f[-lenGamma:]

    def u_0(x: float, t: float) -> float:
        s = 0.0
        for model_x0_i, f0_i in zip(model_x0s_list, vec_f0):
            s += g(x - model_x0_i, t - 0.0) * float(f0_i)
        return s

    def u_Gamma(x: float, t: float) -> float:
        s = 0.0
        for model_xtGamma_i, fGamma_i in zip(model_xtGammas_list, vec_fGamma):
            s += g(x - model_xtGamma_i[0], t - model_xtGamma_i[1]) * float(fGamma_i)
        return s

    def u(x: float, t: float) -> float:
        return u_infty(x, t) + u_0(x, t) + u_Gamma(x, t)

    return u


# discrete observations discrete modelling functions dimensionality 2
def solve_2d_discrete_observations_discrete_modelling(
        cond_xy0s_list: tp.List[tp.Tuple[float, float]],
        cond_xytGammas_list: tp.List[tp.Tuple[float, float, float]],
        cond_f0s_list: tp.List[float],
        cond_fGammas_list: tp.List[float],
        model_xytInfs_list: tp.List[tp.Tuple[float, float, float]],
        model_xy0s_list: tp.List[tp.Tuple[float, float]],
        model_xytGammas_list: tp.List[tp.Tuple[float, float, float]],
        f: tp.Callable[[float, float, float], float],
        g: tp.Callable[[float, float, float], float],
) -> tp.Callable[[float, float, float], float]:
    """
    :param cond_xy0s_list: list of space points for initial conditions:
        u(cond_x0_i, cond_y0_i, 0) = cond_f0_i
    :param cond_xytGammas_list: list of space-time for boundary conditions:
        u(cond_xGamma_i, cond_yGamma_i, cond_tGamma_i) = cond_fGamma_i
    :param cond_f0s_list: list of real values for initial conditions:
        cond_f0_i = u(cond_x0_i, cond_y0_i, 0)
    :param cond_fGammas_list: list of real values for boundary conditions:
        cond_fGamma_i = u(cond_xGamma_i, cond_yGamma_i, cond_tGamma_i)
    :param model_xytInfs_list: list of modelling space-time points for f_infty
    :param model_xy0s_list: list of modelling space points for f_0
    :param model_xytGammas_list: list of modelling points space-time for f_Gamma
    :param f: real-valued function of space and time,
        represents external perturbations in the system.
    :param g: Green's function of the linear differential operator L
    :return: real-valued function u of space and time,
        least squares solution to L u(x, y, t) = f(x, y, t)
        under initial conditions u(cond_x0_i, cond_y0_i, 0) = cond_f0_i,
        and boundary conditions u(cond_xGamma_i, cond_yGamma_i, cond_tGamma_i) = cond_fGamma_i.
    """

    def u_infty(x: float, y: float, t: float) -> float:
        return sum(
            g(x - model_xInf_i, y - model_yInf_i, t - model_tInf_i) *
            f(model_xInf_i, model_yInf_i, model_tInf_i)
            for model_xInf_i, model_yInf_i, model_tInf_i in model_xytInfs_list
        )

    vec_u0 = np.array([[
        cond_f0_i - u_infty(cond_xy0_i[0], cond_xy0_i[1], 0.0)
    ] for cond_f0_i, cond_xy0_i in zip(cond_f0s_list, cond_xy0s_list)])

    vec_uGamma = np.array([[
        cond_fGamma_i - u_infty(cond_xytGamma_i[0], cond_xytGamma_i[1], cond_xytGamma_i[2])
    ] for cond_fGamma_i, cond_xytGamma_i in zip(cond_fGammas_list, cond_xytGammas_list)])

    vec_u = np.vstack((vec_u0, vec_uGamma))

    A11 = np.matrix([[g(
        cond_xy0_i[0] - model_xy0_i[0],
        cond_xy0_i[1] - model_xy0_i[1],
        0.0 - 0.0,
    ) for model_xy0_i in model_xy0s_list] for cond_xy0_i in cond_xy0s_list])

    A12 = np.matrix([[g(
        cond_xy0_i[0] - model_xytGamma_i[0],
        cond_xy0_i[1] - model_xytGamma_i[1],
        0.0 - model_xytGamma_i[2],
    ) for model_xytGamma_i in model_xytGammas_list] for cond_xy0_i in cond_xy0s_list])

    A21 = np.matrix([[g(
        cond_xytGamma_i[0] - model_xy0_i[0],
        cond_xytGamma_i[1] - model_xy0_i[1],
        cond_xytGamma_i[2] - 0.0,
    ) for model_xy0_i in model_xy0s_list] for cond_xytGamma_i in cond_xytGammas_list])

    A22 = np.matrix([[g(
        cond_xytGamma_i[0] - model_xytGamma_i[0],
        cond_xytGamma_i[1] - model_xytGamma_i[1],
        cond_xytGamma_i[2] - model_xytGamma_i[2],
    ) for model_xytGamma_i in model_xytGammas_list] for cond_xytGamma_i in cond_xytGammas_list])

    A = np.vstack((
        np.hstack((A11, A12)),
        np.hstack((A21, A22)),
    ))

    vec_f = np.linalg.pinv(A) * vec_u

    len0, lenGamma = len(model_xy0s_list), len(model_xytGammas_list)

    vec_f0, vec_fGamma = vec_f[:len0], vec_f[-lenGamma:]

    def u_0(x: float, y: float, t: float) -> float:
        s = 0.0
        for model_xy0_i, f0_i in zip(model_xy0s_list, vec_f0):
            s += g(x - model_xy0_i[0], y - model_xy0_i[1], t - 0.0) * float(f0_i)
        return s

    def u_Gamma(x: float, y: float, t: float) -> float:
        s = 0.0
        for model_xytGamma_i, fGamma_i in zip(model_xytGammas_list, vec_fGamma):
            s += g(x - model_xytGamma_i[0], y - model_xytGamma_i[1], t - model_xytGamma_i[2]) * float(fGamma_i)
        return s

    def u(x: float, y: float, t: float) -> float:
        return u_infty(x, y, t) + u_0(x, y, t) + u_Gamma(x, y, t)

    return u


# discrete observations continuous modelling functions dimensionality 1
def solve_1d_discrete_observations_continuous_modelling(
        cond_x0s_list: tp.List[float],
        cond_xtGammas_list: tp.List[tp.Tuple[float, float]],
        cond_f0s_list: tp.List[float],
        cond_fGammas_list: tp.List[float],
        a: float,
        b: float,
        T: float,
        f: tp.Callable[[float, float], float],
        g: tp.Callable[[float, float], float],
) -> tp.Callable[[float, float], float]:
    """
    :param cond_x0s_list: list of space points for initial conditions:
        u(cond_x0_i, 0) = cond_f0_i
    :param cond_xtGammas_list: list of space-time for boundary conditions:
        u(cond_xGamma_i, cond_tGamma_i) = cond_fGamma_i
    :param cond_f0s_list: list of real values for initial conditions:
        cond_f0_i = u(cond_x0_i, 0)
    :param cond_fGammas_list: list of real values for boundary conditions:
        cond_fGamma_i = u(cond_xGamma_i, cond_tGamma_i)
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param T: end time
    :param f: real-valued function of space and time,
        represents external perturbations in the system.
    :param g: Green's function of the linear differential operator L
    :return: real-valued function u of space and time,
        least squares solution to L u(x, t) = f(x, t)
        under initial conditions u(cond_x0_i, 0) = cond_f0_i,
        and boundary conditions u(cond_xGamma_i, cond_tGamma_i) = cond_fGamma_i.
    """

    def u_infty(x: float, t: float) -> float:
        return integrate.dblquad(
            lambda t_, x_: g(x - x_, t - t_) * f(x_, t_), a, b, 0, T
        )[0]

    vec_u0 = np.array([[
        cond_f0_i - u_infty(cond_x0_i, 0.0)
    ] for cond_f0_i, cond_x0_i in zip(cond_f0s_list, cond_x0s_list)])

    vec_uGamma = np.array([[
        cond_fGamma_i - u_infty(cond_xtGamma_i[0], cond_xtGamma_i[1])
    ] for cond_fGamma_i, cond_xtGamma_i in zip(cond_fGammas_list, cond_xtGammas_list)])

    vec_u = np.vstack((vec_u0, vec_uGamma))

    def A11(x: float) -> np.array:
        return np.array([[g(
            cond_x0_i - x,
            0.0 - 0.0,
        )] for cond_x0_i in cond_x0s_list])

    def A12(x: float, t: float) -> np.array:
        return np.array([[g(
            cond_x0_i - x,
            0.0 - t,
        )] for cond_x0_i in cond_x0s_list])

    def A21(x: float) -> np.array:
        return np.array([[g(
            cond_xGamma_i - x,
            cond_tGamma_i - 0.0,
        )] for cond_xGamma_i, cond_tGamma_i in cond_xtGammas_list])

    def A22(x: float, t: float) -> np.array:
        return np.array([[g(
            cond_xGamma_i - x,
            cond_tGamma_i - t,
        )] for cond_xGamma_i, cond_tGamma_i in cond_xtGammas_list])

    def A(x: float, t: float) -> np.matrix:
        return np.vstack((
            np.hstack((A11(x), A12(x, t))),
            np.hstack((A21(x), A22(x, t))),
        ))

    len0, lenGamma = len(cond_x0s_list), len(cond_xtGammas_list)

    P11 = np.matrix([[(
        integrate.quad(lambda x: A11(x)[i] * A11(x)[j], a, b)[0] +
        integrate.quad(lambda t: A12(a, t)[i] * A12(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: A12(b, t)[i] * A12(b, t)[j], 0, T)[0]
    ) for j in range(len0)] for i in range(len0)])

    P12 = np.matrix([[(
        integrate.quad(lambda x: A11(x)[i] * A21(x)[j], a, b)[0] +
        integrate.quad(lambda t: A12(a, t)[i] * A22(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: A12(b, t)[i] * A22(b, t)[j], 0, T)[0]
    ) for j in range(lenGamma)] for i in range(len0)])

    P21 = np.matrix([[(
        integrate.quad(lambda x: A21(x)[i] * A11(x)[j], a, b)[0] +
        integrate.quad(lambda t: A22(a, t)[i] * A12(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: A22(b, t)[i] * A12(b, t)[j], 0, T)[0]
    ) for j in range(len0)] for i in range(lenGamma)])

    P22 = np.matrix([[(
        integrate.quad(lambda x: A21(x)[i] * A21(x)[j], a, b)[0] +
        integrate.quad(lambda t: A22(a, t)[i] * A22(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: A22(b, t)[i] * A22(b, t)[j], 0, T)[0]
    ) for j in range(lenGamma)] for i in range(lenGamma)])

    P = np.vstack((
        np.hstack((P11, P12)),
        np.hstack((P21, P22)),
    ))

    def vec_f(x: float, t: float) -> np.array:
        return A(x, t).T * np.linalg.pinv(P) * vec_u

    def vec_f0(x: float, t: float) -> float:
        return vec_f(x, t)[0]

    def vec_fGamma(x: float, t: float) -> float:
        return vec_f(x, t)[1]

    def u_0(x: float, t: float) -> float:
        return integrate.quad(
            lambda x_: g(x - x_, t - 0.0) * vec_f0(x_, 0.0), a, b
        )[0]

    def u_Gamma(x: float, t: float) -> float:
        return integrate.quad(
            lambda t_: g(x - a, t - t_) * vec_fGamma(a, t_), 0, T
        )[0] + integrate.quad(
            lambda t_: g(x - b, t - t_) * vec_fGamma(b, t_), 0, T
        )[0]

    def u(x: float, t: float) -> float:
        return u_infty(x, t) + u_0(x, t) + u_Gamma(x, t)

    return u


# discrete observations continuous modelling functions dimensionality 2
def solve_2d_discrete_observations_continuous_modelling(
        cond_xy0s_list: tp.List[tp.Tuple[float, float]],
        cond_xytGammas_list: tp.List[tp.Tuple[float, float, float]],
        cond_f0s_list: tp.List[float],
        cond_fGammas_list: tp.List[float],
        a: float,
        b: float,
        c: float,
        d: float,
        T: float,
        f: tp.Callable[[float, float, float], float],
        g: tp.Callable[[float, float, float], float],
) -> tp.Callable[[float, float, float], float]:
    """
    :param cond_xy0s_list: list of space points for initial conditions:
        u(cond_x0_i, cond_y0_i, 0) = cond_f0_i
    :param cond_xytGammas_list: list of space-time for boundary conditions:
        u(cond_xGamma_i, cond_yGamma_i, cond_tGamma_i) = cond_fGamma_i
    :param cond_f0s_list: list of real values for initial conditions:
        cond_f0_i = u(cond_x0_i, cond_y0_i, 0)
    :param cond_fGammas_list: list of real values for boundary conditions:
        cond_fGamma_i = u(cond_xGamma_i, cond_yGamma_i, cond_tGamma_i)
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param c: lower bound of the y-domains of g and u
    :param d: upper bound of the y-domains of g and u
    :param T: end time
    :param f: real-valued function of space and time,
        represents external perturbations in the system.
    :param g: Green's function of the linear differential operator L
    :return: real-valued function u of space and time,
        least squares solution to L u(x, y, t) = f(x, y, t)
        under initial conditions u(cond_x0_i, cond_y0_i, 0) = cond_f0_i,
        and boundary conditions u(cond_xGamma_i, cond_yGamma_i, cond_tGamma_i) = cond_fGamma_i.
    """

    def u_infty(x: float, y: float, t: float) -> float:
        return integrate.tplquad(lambda t_, x_, y_: g(x - x_, y - y_, t - t_) * f(x_, y_, t_), c, d, a, b, 0, T)[0]

    vec_u0 = np.array([[
        cond_f0_i - u_infty(cond_xy0_i[0], cond_xy0_i[1], 0.0)
    ] for cond_f0_i, cond_xy0_i in zip(cond_f0s_list, cond_xy0s_list)])

    vec_uGamma = np.array([[
        cond_fGamma_i - u_infty(cond_xytGamma_i[0], cond_xytGamma_i[1], cond_xytGamma_i[2])
    ] for cond_fGamma_i, cond_xytGamma_i in zip(cond_fGammas_list, cond_xytGammas_list)])

    vec_u = np.vstack((vec_u0, vec_uGamma))

    def A11(x: float, y: float) -> np.array:
        return np.array([[g(
            cond_x0_i - x,
            cond_y0_i - y,
            0.0 - 0.0,
        )] for cond_x0_i, cond_y0_i in cond_xy0s_list])

    def A12(x: float, y: float, t: float) -> np.array:
        return np.array([[g(
            cond_x0_i - x,
            cond_y0_i - y,
            0.0 - t,
        )] for cond_x0_i, cond_y0_i in cond_xy0s_list])

    def A21(x: float, y: float) -> np.array:
        return np.array([[g(
            cond_xGamma_i - x,
            cond_yGamma_i - y,
            cond_tGamma_i - 0.0,
        )] for cond_xGamma_i, cond_yGamma_i, cond_tGamma_i in cond_xytGammas_list])

    def A22(x: float, y: float, t: float) -> np.array:
        return np.array([[g(
            cond_xGamma_i - x,
            cond_yGamma_i - y,
            cond_tGamma_i - t,
        )] for cond_xGamma_i, cond_yGamma_i, cond_tGamma_i in cond_xytGammas_list])

    def A(x: float, y: float, t: float) -> np.matrix:
        return np.vstack((
            np.hstack((A11(x, y), A12(x, y, t))),
            np.hstack((A21(x, y), A22(x, y, t))),
        ))

    len0, lenGamma = len(cond_xy0s_list), len(cond_xytGammas_list)

    P11 = np.matrix([[(
        integrate.dblquad(lambda x, y: A11(x, y)[i] * A11(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: A12(a, y, t)[i] * A12(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: A12(b, y, t)[i] * A12(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: A12(x, c, t)[i] * A12(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: A12(x, d, t)[i] * A12(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(len0)] for i in range(len0)])

    P12 = np.matrix([[(
        integrate.dblquad(lambda x, y: A11(x, y)[i] * A21(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: A12(a, y, t)[i] * A22(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: A12(b, y, t)[i] * A22(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: A12(x, c, t)[i] * A22(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: A12(x, d, t)[i] * A22(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(lenGamma)] for i in range(len0)])

    P21 = np.matrix([[(
        integrate.dblquad(lambda x, y: A21(x, y)[i] * A11(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: A22(a, y, t)[i] * A12(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: A22(b, y, t)[i] * A12(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: A22(x, c, t)[i] * A12(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: A22(x, d, t)[i] * A12(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(len0)] for i in range(lenGamma)])

    P22 = np.matrix([[(
        integrate.dblquad(lambda x, y: A21(x, y)[i] * A21(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: A22(a, y, t)[i] * A22(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: A22(b, y, t)[i] * A22(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: A22(x, c, t)[i] * A22(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: A22(x, d, t)[i] * A22(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(lenGamma)] for i in range(lenGamma)])

    P = np.vstack((
        np.hstack((P11, P12)),
        np.hstack((P21, P22)),
    ))

    def vec_f(x: float, y: float, t: float) -> np.array:
        return A(x, y, t).T * np.linalg.pinv(P) * vec_u

    def vec_f0(x: float, y: float, t: float) -> float:
        return vec_f(x, y, t)[0]

    def vec_fGamma(x: float, y: float, t: float) -> float:
        return vec_f(x, y, t)[1]

    def u_0(x: float, y: float, t: float) -> float:
        return integrate.dblquad(lambda x_, y_: g(x - x_, y - y_, t - 0.0) * vec_f0(x_, y_, 0.0), c, d, a, b)[0]

    def u_Gamma(x: float, y: float, t: float) -> float:
        return integrate.dblquad(lambda t_, y_: g(x - a, y - y_, t - t_) * vec_fGamma(a, y_, t_), c, d, 0, T)[0] + \
            integrate.dblquad(lambda t_, y_: g(x - b, y - y_, t - t_) * vec_fGamma(b, y_, t_), c, d, 0, T)[0] + \
            integrate.dblquad(lambda t_, x_: g(x - x_, y - c, t - t_) * vec_fGamma(x_, c, t_), a, b, 0, T)[0] + \
            integrate.dblquad(lambda t_, x_: g(x - x_, y - d, t - t_) * vec_fGamma(x_, d, t_), a, b, 0, T)[0]

    def u(x: float, y: float, t: float) -> float:
        return u_infty(x, y, t) + u_0(x, y, t) + u_Gamma(x, y, t)

    return u


# continuous observations discrete modelling functions dimensionality 1
def solve_1d_continuous_observations_discrete_modelling(
        cond_f0: tp.Callable[[float], float],
        cond_fGamma: tp.Callable[[float, float], float],
        model_xtInfs_list: tp.List[tp.Tuple[float, float]],
        model_x0s_list: tp.List[float],
        model_xtGammas_list: tp.List[tp.Tuple[float, float]],
        a: float,
        b: float,
        T: float,
        f: tp.Callable[[float, float], float],
        g: tp.Callable[[float, float], float],
) -> tp.Callable[[float, float], float]:
    """
    :param cond_f0: right hand side of the initial conditions u(x, 0) = cond_f0(x)
    :param cond_fGamma: right hand side of the boundary conditions u(x, t) = cond_fGamma(x, t)
    :param model_xtInfs_list: list of modelling space-time points for f_infty
    :param model_x0s_list: list of modelling space points for f_0
    :param model_xtGammas_list: list of modelling points space-time for f_Gamma
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param T: end time
    :param f: real-valued function of space and time,
        represents external perturbations in the system.
    :param g: Green's function of the linear differential operator L
    :return: real-valued function u of space and time,
        least squares solution to L u(x, t) = f(x, t)
        under initial conditions u(x, 0) = cond_f0(x),
        and boundary conditions u(x, t) = cond_fGamma(x, t).
    """

    def u_infty(x: float, t: float) -> float:
        return sum(
            g(x - model_xInf_i, t - model_tInf_i) * f(model_xInf_i, model_tInf_i)
            for model_xInf_i, model_tInf_i in model_xtInfs_list
        )

    def B11(x: float) -> np.array:
        return np.array([[g(
            x - model_x0_i,
            0.0 - 0.0,
        )] for model_x0_i in model_x0s_list])

    def B12(x: float) -> np.array:
        return np.array([[g(
            x - model_xGamma_i,
            0.0 - model_tGamma_i,
        )] for model_xGamma_i, model_tGamma_i in model_xtGammas_list])

    def B21(x: float, t: float) -> np.array:
        return np.array([[g(
            x - model_x0_i,
            t - 0.0,
        )] for model_x0_i in model_x0s_list])

    def B22(x: float, t: float) -> np.array:
        return np.array([[g(
            x - model_xGamma_i,
            t - model_tGamma_i,
        )] for model_xGamma_i, model_tGamma_i in model_xtGammas_list])

    def B(x: float, t: float) -> np.matrix:
        return np.vstack((
            np.hstack((B11(x), B12(x, t))),
            np.hstack((B21(x), B22(x, t))),
        ))

    len0, lenGamma = len(model_x0s_list), len(model_xtGammas_list)

    P11 = np.matrix([[(
        integrate.quad(lambda x: B11(x)[i] * B11(x)[j], a, b)[0] +
        integrate.quad(lambda t: B21(a, t)[i] * B21(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: B21(b, t)[i] * B21(b, t)[j], 0, T)[0]
    ) for j in range(len0)] for i in range(len0)])

    P12 = np.matrix([[(
        integrate.quad(lambda x: B11(x)[i] * B12(x)[j], a, b)[0] +
        integrate.quad(lambda t: B21(a, t)[i] * B22(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: B21(b, t)[i] * B22(b, t)[j], 0, T)[0]
    ) for j in range(lenGamma)] for i in range(len0)])

    P21 = np.matrix([[(
        integrate.quad(lambda x: B12(x)[i] * B11(x)[j], a, b)[0] +
        integrate.quad(lambda t: B22(a, t)[i] * B21(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: B22(b, t)[i] * B21(b, t)[j], 0, T)[0]
    ) for j in range(len0)] for i in range(lenGamma)])

    P22 = np.matrix([[(
        integrate.quad(lambda x: B12(x)[i] * B12(x)[j], a, b)[0] +
        integrate.quad(lambda t: B22(a, t)[i] * B22(a, t)[j], 0, T)[0] +
        integrate.quad(lambda t: B22(b, t)[i] * B22(b, t)[j], 0, T)[0]
    ) for j in range(lenGamma)] for i in range(lenGamma)])

    P = np.vstack((
        np.hstack((P11, P12)),
        np.hstack((P21, P22)),
    ))

    def bar_u0(x: float) -> float:
        return cond_f0(x) - u_infty(x, 0)

    def bar_uGamma(x: float, t: float) -> float:
        return cond_fGamma(x, t) - u_infty(x, t)

    b_u1 = np.array([[
        integrate.quad(lambda x: B11(x)[i] * bar_u0(x), a, b)[0] +
        integrate.quad(lambda t: B21(a, t)[i] * bar_uGamma(a, t), 0, T)[0] +
        integrate.quad(lambda t: B21(b, t)[i] * bar_uGamma(b, t), 0, T)[0]
    ] for i in range(len0)])

    b_u2 = np.array([[
        integrate.quad(lambda x: B12(x)[i] * bar_u0(x), a, b)[0] +
        integrate.quad(lambda t: B22(a, t)[i] * bar_uGamma(a, t), 0, T)[0] +
        integrate.quad(lambda t: B22(b, t)[i] * bar_uGamma(b, t), 0, T)[0]
    ] for i in range(lenGamma)])

    b_u = np.vstack((b_u1, b_u2))

    vec_f = np.linalg.pinv(P) * b_u

    vec_f0, vec_fGamma = vec_f[:len0], vec_f[-lenGamma:]

    def u_0(x: float, t: float) -> float:
        s = 0.0
        for model_x0_i, f0_i in zip(model_x0s_list, vec_f0):
            s += g(x - model_x0_i, t - 0.0) * float(f0_i)
        return s

    def u_Gamma(x: float, t: float) -> float:
        s = 0.0
        for model_xtGamma_i, fGamma_i in zip(model_xtGammas_list, vec_fGamma):
            s += g(x - model_xtGamma_i[0], t - model_xtGamma_i[1]) * float(fGamma_i)
        return s

    def u(x: float, t: float) -> float:
        return u_infty(x, t) + u_0(x, t) + u_Gamma(x, t)

    return u


# continuous observations discrete modelling functions dimensionality 2
def solve_2d_continuous_observations_discrete_modelling(
        cond_f0: tp.Callable[[float, float], float],
        cond_fGamma: tp.Callable[[float, float, float], float],
        model_xytInfs_list: tp.List[tp.Tuple[float, float, float]],
        model_xy0s_list: tp.List[tp.Tuple[float, float]],
        model_xytGammas_list: tp.List[tp.Tuple[float, float, float]],
        a: float,
        b: float,
        c: float,
        d: float,
        T: float,
        f: tp.Callable[[float, float, float], float],
        g: tp.Callable[[float, float, float], float],
) -> tp.Callable[[float, float, float], float]:
    """
    :param cond_f0: right hand side of the initial conditions u(x, y, 0) = cond_f0(x)
    :param cond_fGamma: right hand side of the boundary conditions u(x, y, t) = cond_fGamma(x, y, t)
    :param model_xytInfs_list: list of modelling space-time points for f_infty
    :param model_xy0s_list: list of modelling space points for f_0
    :param model_xytGammas_list: list of modelling points space-time for f_Gamma
    :param a: lower bound of the x-domains of g and u
    :param b: upper bound of the x-domains of g and u
    :param c: lower bound of the y-domains of g and u
    :param d: upper bound of the y-domains of g and u
    :param T: end time
    :param f: real-valued function of space and time,
        represents external perturbations in the system.
    :param g: Green's function of the linear differential operator L
    :return: real-valued function u of space and time,
        least squares solution to L u(x, y, t) = f(x, y, t)
        under initial conditions u(x, y, 0) = cond_f0(x, y),
        and boundary conditions u(x, y, t) = cond_fGamma(x, y, t).
    """

    def u_infty(x: float, y: float, t: float) -> float:
        return sum(
            g(x - model_xInf_i, y - model_yInf_i, t - model_tInf_i) * f(model_xInf_i, model_yInf_i, model_tInf_i)
            for model_xInf_i, model_yInf_i, model_tInf_i in model_xytInfs_list
        )

    def B11(x: float, y: float) -> np.array:
        return np.array([[g(
            x - model_x0_i,
            y - model_y0_i,
            0.0 - 0.0,
        )] for model_x0_i, model_y0_i in model_xy0s_list])

    def B12(x: float, y: float) -> np.array:
        return np.array([[g(
            x - model_xGamma_i,
            y - model_yGamma_i,
            0.0 - model_tGamma_i,
        )] for model_xGamma_i, model_yGamma_i, model_tGamma_i in model_xytGammas_list])

    def B21(x: float, y: float, t: float) -> np.array:
        return np.array([[g(
            x - model_x0_i,
            y - model_y0_i,
            t - 0.0,
        )] for model_x0_i, model_y0_i in model_xy0s_list])

    def B22(x: float, y: float, t: float) -> np.array:
        return np.array([[g(
            x - model_xGamma_i,
            y - model_yGamma_i,
            t - model_tGamma_i,
        )] for model_xGamma_i, model_yGamma_i, model_tGamma_i in model_xytGammas_list])

    def B(x: float, y: float, t: float) -> np.matrix:
        return np.vstack((
            np.hstack((B11(x, y), B12(x, y, t))),
            np.hstack((B21(x, y), B22(x, y, t))),
        ))

    len0, lenGamma = len(model_xy0s_list), len(model_xytGammas_list)

    P11 = np.matrix([[(
        integrate.dblquad(lambda x, y: B11(x, y)[i] * B11(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: B21(a, y, t)[i] * B21(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: B21(b, y, t)[i] * B21(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: B21(x, c, t)[i] * B21(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: B21(x, d, t)[i] * B21(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(len0)] for i in range(len0)])

    P12 = np.matrix([[(
        integrate.dblquad(lambda x, y: B11(x, y)[i] * B12(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: B21(a, y, t)[i] * B22(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: B21(b, y, t)[i] * B22(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: B21(x, c, t)[i] * B22(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: B21(x, d, t)[i] * B22(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(lenGamma)] for i in range(len0)])

    P21 = np.matrix([[(
        integrate.dblquad(lambda x, y: B12(x, y)[i] * B11(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: B22(a, y, t)[i] * B21(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: B22(b, y, t)[i] * B21(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: B22(x, c, t)[i] * B21(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: B22(x, d, t)[i] * B21(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(len0)] for i in range(lenGamma)])

    P22 = np.matrix([[(
        integrate.dblquad(lambda x, y: B12(x, y)[i] * B12(x, y)[j], c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: B22(a, y, t)[i] * B22(a, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: B22(b, y, t)[i] * B22(b, y, t)[j], c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: B22(x, c, t)[i] * B22(x, c, t)[j], a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: B22(x, d, t)[i] * B22(x, d, t)[j], a, b, 0, T)[0]
    ) for j in range(lenGamma)] for i in range(lenGamma)])

    P = np.vstack((
        np.hstack((P11, P12)),
        np.hstack((P21, P22)),
    ))

    def bar_u0(x: float, y: float) -> float:
        return cond_f0(x, y) - u_infty(x, y, 0)

    def bar_uGamma(x: float, y: float, t: float) -> float:
        return cond_fGamma(x, y, t) - u_infty(x, y, t)

    b_u1 = np.array([[
        integrate.dblquad(lambda x, y: B11(x, y)[i] * bar_u0(x, y), c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: B21(a, y, t)[i] * bar_uGamma(a, y, t), c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: B21(b, y, t)[i] * bar_uGamma(b, y, t), c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: B21(x, c, t)[i] * bar_uGamma(x, c, t), a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: B21(x, d, t)[i] * bar_uGamma(x, d, t), a, b, 0, T)[0]
    ] for i in range(len0)])

    b_u2 = np.array([[
        integrate.dblquad(lambda x, y: B12(x, y)[i] * bar_u0(x, y), c, d, a, b)[0] +
        integrate.dblquad(lambda t, y: B22(a, y, t)[i] * bar_uGamma(a, y, t), c, d, 0, T)[0] +
        integrate.dblquad(lambda t, y: B22(b, y, t)[i] * bar_uGamma(b, y, t), c, d, 0, T)[0] +
        integrate.dblquad(lambda t, x: B22(x, c, t)[i] * bar_uGamma(x, c, t), a, b, 0, T)[0] +
        integrate.dblquad(lambda t, x: B22(x, d, t)[i] * bar_uGamma(x, d, t), a, b, 0, T)[0]
    ] for i in range(lenGamma)])

    b_u = np.vstack((b_u1, b_u2))

    vec_f = np.linalg.pinv(P) * b_u

    vec_f0, vec_fGamma = vec_f[:len0], vec_f[-lenGamma:]

    def u_0(x: float, y: float, t: float) -> float:
        s = 0.0
        for model_xy0_i, f0_i in zip(model_xy0s_list, vec_f0):
            s += g(x - model_xy0_i[0], y - model_xy0_i[1], t - 0.0) * float(f0_i)
        return s

    def u_Gamma(x: float, y: float, t: float) -> float:
        s = 0.0
        for model_xytGamma_i, fGamma_i in zip(model_xytGammas_list, vec_fGamma):
            s += g(x - model_xytGamma_i[0], y - model_xytGamma_i[1], t - model_xytGamma_i[2]) * float(fGamma_i)
        return s

    def u(x: float, y: float, t: float) -> float:
        return u_infty(x, y, t) + u_0(x, y, t) + u_Gamma(x, y, t)

    return u
