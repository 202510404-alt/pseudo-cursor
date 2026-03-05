package com.example.single.core;

/**
 * UI/서버가 읽기용으로 사용하는 게임 상태 스냅샷입니다.
 * 현재는 필드를 비워두고, 이후 보드/자원/저울 상태를 점진적으로 추가할 예정입니다.
 */
public class GameSnapshot {

    // 간단한 4x4 보드 상태
    public final CardInstance[] playerSlots;
    public final CardInstance[] enemySlots;

    // 자원 (우상단 표시용)
    public final int gold;
    public final int energy;

    // 저울 값은 나중에 추가 예정 (지금은 보드/자원에만 집중)

    public GameSnapshot(
            CardInstance[] playerSlots,
            CardInstance[] enemySlots,
            int gold,
            int energy
    ) {
        this.playerSlots = playerSlots;
        this.enemySlots = enemySlots;
        this.gold = gold;
        this.energy = energy;
    }

}

