import secrets
import sys
from typing import List, Tuple

PRIME = (1 << 127) - 1  #大素数P
G_FELDMAN = 3           #这里的生成元是随意选的
Share = Tuple[int, int]

# 1、数学工具
def _modinv(a: int, p: int = PRIME) -> int:   #费马小定理求模逆，模逆元函数
    return pow(a, p - 2, p)

def lagrange_interpolate(x: int, x_s: List[int], y_s: List[int]) -> int:     #拉格朗日插值，用于恢复秘密
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

# 2、生成分片
def generate_shares(secret: int, n: int, t, feldman=False):
    if not (1 < t <= n <= 255):
        raise ValueError("1 < t <= n <= 255")
    #构造多项式
    coeffs = [secret % PRIME] + [secrets.randbelow(PRIME) for _ in range(t - 1)]
    shares = []
    #Horner法，计算f（1），f（n）
    for x in range(1, n + 1):
        y = 0
        for a in reversed(coeffs):
            y = (y * x + a) % PRIME
        shares.append((x, y))
    if not feldman:
        return shares
    commitments = [pow(G_FELDMAN, a, PRIME) for a in coeffs]
    return shares, commitments

# 3、Feldman验证
def verify_share(x: int, y: int, commitments: List[int], verbose=False) -> bool:
    t = len(commitments)
    rhs = 1
    for j in range(t):
        rhs = rhs * pow(commitments[j], pow(x, j), PRIME) % PRIME
    lhs = pow(G_FELDMAN, y, PRIME)
    if verbose:
        print(f"  x={x}  y={y}\n    lhs=g^y     ={lhs}\n    rhs=∏C_j^x^j={rhs}\n    {'✅' if lhs==rhs else '❌'}")
    return lhs == rhs

# 4、秘密恢复
def recover_secret(shares: List[Share], commitments=None, verbose=False):
    if commitments:
        for x, y in shares:
            if not verify_share(x, y, commitments, verbose=verbose):
                raise ValueError(f"Share x={x} y={y} 未通过 Feldman 验证！")
    x_s, y_s = zip(*shares)
    return lagrange_interpolate(0, list(x_s), list(y_s))

# 篡改工具
def tamper(shares: List[Share], idx: int, delta: int = 1):
    """1-base：把第 idx 份 y 加 delta"""
    x, y = shares[idx - 1]
    shares[idx - 1] = (x, (y + delta) % PRIME)

# 交互设计
def main():
    secret = int(input("请输入要保护的秘密（整数）："))
    n = int(input("总分片数 n："))
    t = int(input("门限 t："))
    use_feldman = input("是否启用 Feldman VSS？(y/n) ").lower() == 'y'

    if use_feldman:
        shares, commitments = generate_shares(secret, n, t, feldman=True)
        print("\nFeldman 承诺（公开）:")
        for j, c in enumerate(commitments):
            print(f"C_{j}: {c}")
    else:
        shares = generate_shares(secret, n, t, feldman=False)
        commitments = None

    print("\n生成的分片：")
    for i, (x, y) in enumerate(shares, 1):
        print(f"Share {i}: x={x}  y={y}")

    while True:
        print("\n=== 选项 ===\n0 直接恢复\n1 篡改某分片后再恢复\n2 退出")
        choice = input("选 0/1/2：").strip()
        if choice == "2":
            break
        if choice not in {"0", "1"}:
            continue
        if choice == "1":
            idx = int(input("要篡改第几号分片（1-base）？ "))
            delta = int(input("y 增加多少（可负）？ "))
            tamper(shares, idx, delta)
            print(f"已把 Share {idx} 的 y 加 {delta}（模 PRIME）")
            print("当前分片：")
            for i, (x, y) in enumerate(shares, 1):
                print(f"Share {i}: x={x}  y={y}")

        idxs = input(f"\n请选择至少 {t} 个分片编号（空格分隔）：").strip().split()
        selected = [shares[int(i) - 1] for i in idxs]
        if len(selected) < t:
            print("分片不足")
            continue
        try:
            rec = recover_secret(selected, commitments, verbose=True)
            print("恢复结果：", rec)
            print("✅ 一致！" if rec == secret % PRIME else "❌ 不一致！")
        except ValueError as e:
            print("恢复失败：", e)

if __name__ == "__main__":
    main()