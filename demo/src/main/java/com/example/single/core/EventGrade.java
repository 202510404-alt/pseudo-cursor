package com.example.single.core;

/**
 * 이벤트 등급.
 * 0(일반), 1(희귀), 2(에픽), 3(전설), 4(신화)
 */
public enum EventGrade {
    COMMON(0),
    RARE(1),
    EPIC(2),
    LEGENDARY(3),
    MYTHIC(4);

    private final int code;

    EventGrade(int code) {
        this.code = code;
    }

    public int getCode() {
        return code;
    }

    public static EventGrade fromCode(int code) {
        for (EventGrade g : values()) {
            if (g.code == code) return g;
        }
        return COMMON;
    }
}

