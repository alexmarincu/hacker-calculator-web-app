from math import *  # type: ignore
from .. import utils as ut


class ExpressionEvaluator:
    _safeTokenList = [
        # math
        'e',
        'pi',
        'inf',
        'nan',
        'tau',
        'acos',
        'acosh',
        'asin',
        'asinh',
        'atan',
        'atan2',
        'atanh',
        'cbrt',
        'ceil',
        'comb',
        'copysign',
        'cos',
        'cosh',
        'degrees',
        'dist',
        'erf',
        'erfc',
        'exp',
        'exp2',
        'expm1',
        'fabs',
        'factorial',
        'floor',
        'fmod',
        'frexp',
        'fsum',
        'gamma',
        'gcd',
        'hypot',
        'isclose',
        'isinf',
        'isfinite',
        'isnan',
        'isqrt',
        'lcm',
        'ldexp',
        'lgamma',
        'log',
        'log10',
        'log1p',
        'log2',
        'modf',
        'nextafter',
        'perm',
        'pow',
        'prod',
        'radians',
        'remainder',
        'sin',
        'sinh',
        'sumprod',
        'sqrt',
        'tan',
        'tanh',
        'trunc',
    ]
    _safeTokenDict = dict(
        [(k, globals().get(k, None)) for k in _safeTokenList]
    )
    _safeTokenDict['abs'] = abs
    _safeTokenDict['int'] = int
    _safeTokenDict['min'] = min
    _safeTokenDict['max'] = max
    _safeTokenDict['round'] = round

    @classmethod
    def getFilteredTokens(cls, substr: str) -> list[str]:
        return [
            token
            for token in cls._safeTokenDict.keys()
            if token.startswith(substr)
        ]

    def eval(self, expression: str) -> ut.Result[float]:
        result: ut.Result[float]
        try:
            result = ut.Success(
                float(
                    eval(
                        expression, {"__builtins__": None},
                        self._safeTokenDict)
                )
            )
        except Exception as e:
            result = ut.Failure(str(e))
        return result
