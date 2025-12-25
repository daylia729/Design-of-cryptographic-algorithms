package com.duwei.cp.abe.attribute;

import com.duwei.cp.abe.parameter.PublicKey;
import it.unisa.dia.gas.jpbc.Element;
import it.unisa.dia.gas.jpbc.Field;
import lombok.Data;

import java.nio.charset.StandardCharsets;
import java.util.Objects;

/**
 * CP-ABE 属性对象
 * 作用：把人类可读的属性字符串（如"硕士"、"护士"）→ 映射到椭圆曲线群 G0 的元素，
 *      后续密钥生成/加密时会用该元素参与指数运算，实现“属性即群元”的密码学语义。
 */
@Data
public class Attribute {

    /* ====================== 字段 ====================== */

    /**
     * 群 G0 中的元素，代表这个属性。
     * 在密钥生成时它被拿来算：
     *      D_i = g^(α+r)/(β+H(Attr))
     * 这里 H(Attr) 就是用本字段。
     */
    private Element attributeValue;

    /**
     * 原始字符串，仅做展示、比较用，不入算法。
     */
    private String attributeName;

    /* ====================== 构造 ====================== */

    /**
     * 快捷构造：从 PublicKey 里取 G0 域。
     * 用户代码一般用这个。
     */
    public Attribute(String attributeName, PublicKey publicKey) {
        this(attributeName, publicKey.getPairingParameter().getG0());
    }

    /**
     * 核心构造：把字符串哈希（简单方式）到群 G0。
     * 步骤：
     *  1. UTF-8 转字节
     *  2. 调用 G0.newElementFromBytes → 得到随机-looking 群元
     *  3. .getImmutable() 保证线程安全、不可变
     */
    public Attribute(String attributeName, Field G0) {
        this.attributeName = attributeName;
        // 简单哈希映射：字符串 → 群元素（JPBC 内部做哈希到曲线）
        this.attributeValue = G0.newElementFromBytes(
                        attributeName.getBytes(StandardCharsets.UTF_8))
                .getImmutable();
    }

    /* ====================== 工具 ====================== */

    /**
     * 打印时只显示可读名字，方便日志。
     */
    @Override
    public String toString() {
        return attributeName;
    }

    /**
     * 按“群元素+名字”联合判等，保证集合去重正确。
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Attribute)) return false;
        Attribute other = (Attribute) o;
        return Objects.equals(attributeValue, other.attributeValue) &&
                Objects.equals(attributeName, other.attributeName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(attributeValue, attributeName);
    }
}