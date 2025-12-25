#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shamir Secret Sharing (t-of-n) 示例
基于拉格朗日插值，模数 PRIME = 2^127 - 1
"""

import secrets
import sys
from typing import List, Tuple

PRIME = (1 << 127) - 1           # 2^127 - 1
Share = Tuple[int, int]          # (x, y)

# ------------------------ 数学工具 ------------------------
def _modinv(a: int, p: int = PRIME) -> int:
    """模逆元，Fermat 小定理"""
    return pow(a, p - 2, p)

def lagrange_interpolate(x: int, x_s: List[int], y_s: List[int]) -> int:
    """给定 t 个点 (x_s, y_s)，计算 f(x) mod PRIME"""
    k = len(x_s)
    assert k == len(y_s) and k > 0
    res = 0
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        # 计算拉格朗日基多项式 L_i(x)
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

# ------------------------ 秘密分片 ------------------------
def generate_shares(secret: int, n: int, t: int) -> List[Share]:
    """生成 n 个分片，门限 t"""
    if not (1 < t <= n <= 255):
        raise ValueError("必须满足 1 < t <= n <= 255")
    # 随机系数 a0=secret, a1…a_{t-1}
    coeffs = [secret] + [secrets.randbelow(PRIME) for _ in range(t - 1)]
    shares = []
    for x in range(1, n + 1):
        y = 0
        # Horner 法求值，模 PRIME
        for a in reversed(coeffs):
            y = (y * x + a) % PRIME
        shares.append((x, y))
    return shares

def recover_secret(shares: List[Share]) -> int:
    """用至少 t 个分片恢复秘密"""
    if not shares:
        raise ValueError("分片列表为空")
    x_s, y_s = zip(*shares)
    return lagrange_interpolate(0, list(x_s), list(y_s))

# ------------------------ CLI ------------------------
def _interactive():
    secret = int(input("请输入要保护的秘密（整数）："))
    n = int(input("总分片数 n："))
    t = int(input("门限 t："))
    shares = generate_shares(secret, n, t)
    print("\n生成的分片：")
    for idx, (x, y) in enumerate(shares, 1):
        print(f"Share {idx}: x={x}, y={y}")

    idxs = input(f"\n请选择至少 {t} 个分片编号（空格分隔）：").strip().split()
    selected = [shares[int(i) - 1] for i in idxs]
    if len(selected) < t:
        print("分片不足，无法恢复")
        return
    recovered = recover_secret(selected)
    print("恢复结果：", recovered)
    print("✅ 一致！" if recovered == secret else "❌ 不一致！")

def _quick_demo():
    """非交互式快速演示"""
    secret = 123456789
    n, t = 5, 3
    shares = generate_shares(secret, n, t)
    print("已生成 5 个分片，门限 3")
    # 任意取 3 个
    recovered = recover_secret(shares[:3])
    print("用前 3 个分片恢复：", recovered)
    assert recovered == secret

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        _quick_demo()
    else:
        _interactive()