package com.example.single.core;

/**
 * 게임에 전달되는 명령의 기본 형태입니다.
 * 아직 구체적인 종류는 정하지 않고, 이후 확장 가능한 뼈대만 정의합니다.
 */
public class GameCommand {

    public enum Type {
        END_TURN,
        PLACE_CARD,
        ATTACH_CARD,
        REQUEST_INFO
        // 필요해지면 여기서 계속 추가
    }

    private final Type type;

    // 나중에 좌표, 카드 ID, 대상 슬롯 등 상세 필드를 추가할 예정입니다.

    public GameCommand(Type type) {
        this.type = type;
    }

    public Type getType() {
        return type;
    }
}

