package com.example.single.core;

/**
 * 플레이어 4칸 vs 적 4칸(총 8칸) 보드입니다.
 * 실제 전투 로직은 GameEngine이 담당하고, 이 클래스는 위치와 배치만 관리합니다.
 */
public class Board4x4 {

    public enum Side {
        PLAYER,
        ENEMY
    }

    // 0~3번: 각 칸에 올라간 카드 인스턴스(없으면 null)
    private final CardInstance[] playerSlots = new CardInstance[4];
    private final CardInstance[] enemySlots = new CardInstance[4];

    public CardInstance[] getPlayerSlots() {
        return playerSlots;
    }

    public CardInstance[] getEnemySlots() {
        return enemySlots;
    }

    public boolean isEmpty(Side side, int index) {
        checkIndex(index);
        return getArray(side)[index] == null;
    }

    public CardInstance get(Side side, int index) {
        checkIndex(index);
        return getArray(side)[index];
    }

    public void place(Side side, int index, CardInstance instance) {
        checkIndex(index);
        getArray(side)[index] = instance;
    }

    public void remove(Side side, int index) {
        checkIndex(index);
        getArray(side)[index] = null;
    }

    private CardInstance[] getArray(Side side) {
        return (side == Side.PLAYER) ? playerSlots : enemySlots;
    }

    private void checkIndex(int index) {
        if (index < 0 || index >= 4) {
            throw new IllegalArgumentException("보드 인덱스는 0~3 이어야 합니다: " + index);
        }
    }
}


