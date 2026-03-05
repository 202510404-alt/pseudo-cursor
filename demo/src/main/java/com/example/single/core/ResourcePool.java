package com.example.single.core;

/**
 * Gold, Energy, Blood 같은 자원을 관리하는 뼈대입니다.
 * 싱글에서는 로컬에서만 쓰고, 멀티에서는 서버와 동기화하는 형태로 확장할 예정입니다.
 */
public class ResourcePool {

    private int gold;
    private int energy;
    private int blood;

    public int getGold() {
        return gold;
    }

    public int getEnergy() {
        return energy;
    }

    public int getBlood() {
        return blood;
    }

    public void addGold(int amount) {
        gold += amount;
        if (gold < 0) gold = 0;
    }

    public void addEnergy(int amount) {
        energy += amount;
        if (energy < 0) energy = 0;
    }

    public void addBlood(int amount) {
        blood += amount;
        if (blood < 0) blood = 0;
    }

}

