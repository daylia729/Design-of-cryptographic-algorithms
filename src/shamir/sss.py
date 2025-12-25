#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shamir + Feldman VSS  (t-of-n)
运行：python3 sss_feldman.py
"""
import secrets
import sys
from typing import List, Tuple

# -------------------- 基本参数 --------------------
PRIME = (1 << 127) - 1          # 2^127 - 1
G_FELDMAN = 3                   # 公开生成元，模 PRIME
Share = Tuple[int, int]         # (x, y)

# -------------------- 数学工具 --------------------
def _modinv(a: int, p: int = PRIME) -> int:
    return pow(a, p - 2, p)

def lagrange_interpolate(x: int, x_s: List[int], y_s: List[int]) -> int:
    """拉格朗日插值求 f(x) mod PRIME"""
    k = len(x_s)
    assert k == len(y_s) and k > 0
    res = 0
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        num, den = 1, 1
        for j in range(k):
            if i == j:
                continue
            num = num * (x - x_s[j]) % PRIME
            den = den * (xi - x_s[j]) % PRIME
        inv_den = _modinv(den)
        Li = num * inv_den % PRIME
        res = (res + yi * Li) % PRIME
    return res

# -------------------- 秘密分片 + Feldman --------------------
def generate_shares(secret: int, n: int, t, feldman: bool = False):
    if not (1 < t <= n <= 255):
        raise ValueError("1 < t <= n <= 255")
    coeffs = [secret] + [secrets.randbelow(PRIME) for _ in range(t - 1)]
    shares = []
    for x in range(1, n + 1):
        y = 0
        for a in reversed(coeffs):
            y = (y * x + a) % PRIME
        shares.append((x, y))
    if not feldman:
        return shares
    commitments = [pow(G_FELDMAN, a, PRIME) for a in coeffs]
    return shares, commitments

# -------------------- Feldman 验证 --------------------
def verify_share(x: int, y: int, commitments: List[int]) -> bool:
    """验证 g^y == prod C_j^{x^j} mod PRIME"""
    t = len(commitments)
    rhs = 1
    for j in range(t):
        exponent = pow(x, j)
        rhs = rhs * pow(commitments[j], exponent, PRIME) % PRIME
        print(f"exponent(x^{j} % PRIME): {exponent}, rhs:{rhs}")
    lhs = pow(G_FELDMAN, y, PRIME)
    print(f"lhs:{lhs}, rhs:{rhs}")
    return lhs == rhs

# -------------------- 恢复 --------------------
def recover_secret(shares: List[Share], commitments: List[int] = None):
    if commitments:
        for x, y in shares:
            if not verify_share(x, y, commitments):
                raise ValueError(f"Share x={x} y={y} 未通过 Feldman 验证！")
    x_s, y_s = zip(*shares)
    return lagrange_interpolate(0, list(x_s), list(y_s))

# -------------------- CLI --------------------
def main():
    secret = int(input("请输入要保护的秘密（整数）："))
    n = int(input("总分片数 n："))
    t = int(input("门限 t："))
    use_feldman = input("是否启用 Feldman VSS？(y/n) ").lower() == 'y'

    if use_feldman:
        shares, commitments = generate_shares(secret, n, t, feldman=True)
        print("\nFeldman 承诺（公开，可贴在公告栏）:")
        for j, c in enumerate(commitments):
            print(f"C_{j}: {c}")
    else:
        shares = generate_shares(secret, n, t, feldman=False)
        commitments = None

    print("\n生成的分片：")
    for idx, (x, y) in enumerate(shares, 1):
        print(f"Share {idx}: x={x}, y={y}")

    idxs = input(f"\n请选择至少 {t} 个分片编号（空格分隔）：").strip().split()
    selected = [shares[int(i) - 1] for i in idxs]
    if len(selected) < t:
        print("分片不足，无法恢复")
        sys.exit(1)

    try:
        recovered = recover_secret(selected, commitments)
        print("恢复结果：", recovered)
        print("✅ 一致！" if recovered == secret else "❌ 不一致！")
    except ValueError as e:
        print("恢复失败：", e)

if __name__ == "__main__":
    main()