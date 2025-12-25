package com.duwei.cp.abe.parameter;

import it.unisa.dia.gas.jpbc.Element;
import it.unisa.dia.gas.jpbc.Field;
import it.unisa.dia.gas.jpbc.Pairing;
import it.unisa.dia.gas.plaf.jpbc.pairing.PairingFactory;
import lombok.Getter;
import lombok.ToString;

/**
 * 双线性对参数（全局单例，不可变）
 */
@ToString
public final class PairingParameter {

    @Getter private final Pairing pairing;
    @Getter private final Field G0;
    @Getter private final Field G1;
    @Getter private final Field Zr;
    @Getter private final Element generator;

    /* ========== 单例 ========== */
    private static class Holder {
        private static final PairingParameter INSTANCE = create();
    }

    public static PairingParameter getInstance() {
        return Holder.INSTANCE;
    }

    /* ========== 私有构造 ========== */
    private PairingParameter(Pairing pairing, Field G0, Field G1, Field Zr, Element generator) {
        this.pairing   = pairing;
        this.G0        = G0;
        this.G1        = G1;
        this.Zr        = Zr;
        this.generator = generator;
    }

    /* ========== 一次性创建 ========== */
    private static PairingParameter create() {
        Pairing pairing = PairingFactory.getPairing("params/curves/a.properties");
        Field G0 = pairing.getG1();   // 注意：JPBC 里 G1 是椭圆曲线群
        Field G1 = pairing.getGT();   // GT 是目标群
        Field Zr = pairing.getZr();
        Element generator = G0.newRandomElement().getImmutable();
        return new PairingParameter(pairing, G0, G1, Zr, generator);
    }
}