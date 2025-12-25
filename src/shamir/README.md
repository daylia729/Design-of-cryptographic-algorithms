# Shamir 秘密分享实现

本项目提供了Shamir秘密分享（SSS）和可验证秘密分享（VSS）方案的Python实现，包括Feldman VSS。

## 功能

- **Shamir 秘密分享**：将秘密分成n个份额，阈值为t，至少需要t个份额来重建秘密。
- **Feldman 可验证秘密分享**：添加验证功能，确保份额有效性而不泄露秘密。
- **交互式演示**：命令行界面，用于生成份额、验证和恢复秘密。
- **篡改演示**：在`vss_demo.py`中，您可以模拟份额篡改并查看验证效果。

## 文件

- `sharescret.py`：基本的Shamir秘密分享实现，具有交互式CLI。
- `sss.py`：Shamir + Feldman VSS实现。
- `vss_demo.py`：带有篡改模拟的高级演示。



## 使用

### 基本Shamir秘密分享

运行交互式演示：

```bash
python sharescret.py
```

或运行快速演示：

```bash
python sharescret.py --demo
```

### 可验证秘密分享

运行Feldman VSS演示：

```bash
python sss.py
```

### 带有篡改的高级演示

运行允许份额篡改的演示：

```bash
python vss_demo.py
```

## 数学背景

实现使用：
- 素数模数：2^127 - 1
- 拉格朗日插值用于秘密恢复
- Feldman承诺用于验证

## 许可证

本项目根据MIT许可证授权 - 详情请见[LICENSE](LICENSE)文件。

## 贡献

欢迎贡献！请随时提交拉取请求。

