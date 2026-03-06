package com.example.single.core;

import java.util.Arrays;
import java.util.Optional;

public enum EventGrade {
    COMMON(1),
    UNCOMMON(2), // 새로 추가
    RARE(3),
    EPIC(4),
    MYTHIC(5);

    private final int code;

    EventGrade(int code) {
        this.code = code;
    }

    public int getCode() {
        return code;
    }

    public static Optional<EventGrade> fromCode(int code) {
        return Arrays.stream(EventGrade.values())
                .filter(grade -> grade.getCode() == code)
                .findFirst();
    }
}