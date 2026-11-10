"""Optional independent exact-symbolic adversary; requires SymPy >= 1.12."""
from fractions import Fraction as Q
import random
import sympy as sp
from algebraic_zero import source, rational_event, quadratic_event, cyclotomic, Refusal


def run() -> None:
    rng = random.Random(241)
    x = sp.symbols("x")
    for n in range(4,129,4):
        observed = cyclotomic(n)
        expected = sp.Poly(sp.cyclotomic_poly(n, x), x)
        assert list(observed) == [Q(int(expected.nth(j))) for j in range(expected.degree()+1)]
    checked, refused, unknown = 0, 0, 0
    for _ in range(240):
        t=Q(rng.randint(-9,9), rng.randint(1,9))
        offset=Q(rng.randint(-3,3),rng.randint(1,9))
        rate=Q(rng.randint(-3,3),rng.randint(1,3))
        def coeffs():
            return [Q(rng.randint(-4,4),rng.randint(1,5))
                    for _ in range(rng.randint(0,4))]
        s=source(coeffs(),cos=(coeffs(),coeffs()),sin=(coeffs(),coeffs()),
                 phase_offset=offset,phase_rate=rate)
        try:
            result=rational_event(s,t)["result"]
        except Refusal:
            refused += 1
            continue
        qt=sp.Rational(t.numerator,t.denominator)
        phase=offset+rate*t
        angle=sp.pi*sp.Rational(phase.numerator,phase.denominator)
        def poly(p):
            return sum(sp.Rational(v.numerator,v.denominator)*qt**j
                       for j,v in enumerate(p))
        value=poly(s.c0)+sum(poly(c)*sp.cos((j+1)*angle)+poly(v)*sp.sin((j+1)*angle)
                             for j,(c,v) in enumerate(zip(s.cos,s.sin)))
        symbolic=sp.simplify(sp.expand_trig(value)).equals(0)
        if symbolic is None:
            unknown += 1
        else:
            assert (result in ("EXACT_ZERO","IDENTICAL_ZERO_PIECE")) == symbolic
            checked += 1
    for _ in range(120):
        d=rng.randint(2,32)
        while sp.integer_nthroot(d,2)[1]:
            d += 1
        M=sp.Poly(x*x-d,x)
        multiplicity=rng.randint(0,3)
        channels=[]
        for _ in range(5):
            poly=sp.Poly(rng.randint(-3,3)+rng.randint(-3,3)*x+rng.randint(-3,3)*x*x,x)*M**multiplicity
            channels.append([int(poly.nth(j)) for j in range(poly.degree()+1)] if poly else [])
        s=source(channels[0],cos=(channels[1],channels[2]),sin=(channels[3],channels[4]))
        outcome=quadratic_event(s,1,0,-d)
        if any(channels):
            assert outcome["multiplicity_at_both"] == multiplicity
    print("PASS: 32 exact cyclotomic polynomials;"
          f" {checked} checked rational symbolic controls, {refused} budget refusals,"
          f" {unknown} symbolic unknowns; 120 quadratic valuation checks")


if __name__ == "__main__":
    run()
