package com.example.single.core;

/**
 * 싱글 모드용 순수 게임 엔진의 최상위 인터페이스입니다.
 * - 네트워크나 콘솔/Unity UI에 의존하지 않고,
 * - 입력(Command)과 상태 스냅샷(Snapshot)만을 주고받도록 설계합니다.
 */
public interface GameEngine {

    /**
     * 한 틱(tick)을 진행합니다.
     * 나중에 고정 틱 간격 또는 시간 기반으로 호출할 수 있습니다.
     */
    void stepTick();

    /**
     * 플레이어 입력이나 시스템 명령을 적용합니다.
     * 예: 카드 배치, 부착, 턴 종료 등.
     */
    void applyCommand(GameCommand command);

    /**
     * 현재 게임 상태의 읽기 전용 스냅샷을 반환합니다.
     * 콘솔/Unity/서버는 이 스냅샷을 사용해 화면을 그리거나 전송하게 됩니다.
     */
    GameSnapshot getSnapshot();
}

