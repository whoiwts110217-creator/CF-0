#!/usr/bin/env python3
"""Caveman Focus RH-008: reproducible finite prime-power error diagnostic.
NO RH conclusion: every value computed is finite data.
Standard Python only, no external packages.
"""
from math import log, sqrt

def von_mangoldt_array(limit):
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0:2] = b'\x00\x00'
    weights = [0.0] * (limit + 1)
    for p in range(2, limit + 1):
        if not sieve[p]:
            continue
        # Stamp all powers p^k with log(p), by the definition of Lambda.
        v = p
        while v <= limit:
            weights[v] = log(p)
            if v > limit // p:
                break
            v *= p
        if p*p <= limit:
            sieve[p*p:limit+1:p] = b'\x00' * (((limit - p*p)//p) + 1)
    return weights

def run(limit=1000000):
    weights = von_mangoldt_array(limit)
    snapshots = set([10, 100, 1000, 10000, 100000, 1000000])
    psi = 0.0
    peak = (0.0, 0, 0.0)
    lines = []
    for x in range(1, limit+1):
        psi += weights[x]
        if x<10:
            continue
        err = psi - x
        r = abs(err)/(sqrt(x)*log(x)**2)
        if r>peak[0]:
            peak=(r,x,err)
        if x in snapshots:
            lines.append((x,round(psi,8),round(err,8),round(r,10),round(peak[0],10)))
    print('RH-008 PRIME-POWER DISCREPANCY: FINITE RANGE ONLY')
    print('n | psi(n) | psi(n)-n | |error|/(sqrt(n) log^2 n) | peak over 10<=x<=n')
    for row in lines:
        print(*row,sep=' | ')
    print('Final finite peak:',peak)
    print('Limit:',limit)
    print('WARNING: finite samples do not establish the asymptotic exponent or RH.')
    return lines, peak

if __name__ == '__main__':
    run()

# This appended routine is intentionally independent of the first sieve computation.
# It demonstrates how an altered q-factor can preserve all first-X Dirichlet
# coefficients while introducing zeros off the line and extra prime-power weights.
def audit_finite_prefix_impostor(q=1009, beta=0.75, cutoff=1000):
    from math import pi
    import cmath
    assert q > cutoff
    # Explicit q-factor 1 + q^(beta-s) vanishes at s=beta + (2k+1)pi*i/log(q)
    off_zero = complex(beta, pi/log(q))
    factor_value = 1+cmath.exp((beta-off_zero)*log(q))
    # Coefficients of zeta(s)*(1+q^(beta-s)) for n<q remain 1.
    first_mismatch = q
    a=q**beta
    print('\nARITHMETIC-IMPOSTOR AUDIT (does NOT preserve the zeta functional equation)')
    print(f'q={q} beta={beta} cutoff={cutoff}; first modified Dirichlet coefficient n={first_mismatch}')
    print('Constructed off-line zero:',off_zero)
    print('Absolute altered-factor value at zero:',abs(factor_value))
    # Additional -F'/F coefficients at q^k are (-1)^(k-1) log(q)*q^(k*beta).
    discrepancy = 0.0
    for k in range(1, 5):
        extra_weight = ((-1)**(k-1))*log(q)*a**k
        discrepancy += extra_weight
        print(f'k={k} sign={"+" if extra_weight>0 else "-"} added_prime_power_weight={extra_weight:.6e} ' 
              f'cumulative={discrepancy:.6e} ratio_to_x^beta={discrepancy/a**k:.6g}')
    assert abs(factor_value) < 1e-12

if __name__ == '__main__':
    audit_finite_prefix_impostor()