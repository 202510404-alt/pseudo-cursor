package com.example.single.core;

/**
 * 실제 게임판/손패 위에 존재하는 "한 장의 카드 인스턴스"입니다.
 * - CardDef는 도감(기본값)
 * - CardInstance는 강화/버프/디버프 등으로 달라질 수 있는 실체
 */
public class CardInstance {

    public enum Owner {
        PLAYER,
        ENEMY
    }

    private final CardDef def;   // 도감 정보
    private final Owner owner;   // 소유자 (플레이어/적)

    // 강화·피해 등으로 변할 수 있는 현재 스탯
    private int currentHp;
    private int currentAtk;
    private int currentDef;

    // 이후 필요하면 속도/게이지/에너지 등을 여기서 관리

    public CardInstance(CardDef def, Owner owner) {
        this.def = def;
        this.owner = owner;
        this.currentHp = def.hp;
        this.currentAtk = def.atk;
        this.currentDef = def.def;
    }

    public CardDef getDef() {
        return def;
    }

    public Owner getOwner() {
        return owner;
    }

    public int getCurrentHp() {
        return currentHp;
    }

    public int getCurrentAtk() {
        return currentAtk;
    }

    public int getCurrentDef() {
        return currentDef;
    }

    public void setCurrentHp(int currentHp) {
        this.currentHp = currentHp;
    }

    public void setCurrentAtk(int currentAtk) {
        this.currentAtk = currentAtk;
    }

    public void setCurrentDef(int currentDef) {
        this.currentDef = currentDef;
    }
}

