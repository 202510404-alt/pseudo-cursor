package com.example.single.core;

public enum EventGrade {
    COMMON(1, "일반"),
    RARE(2, "희귀"),
    EPIC(3, "영웅"),
    LEGENDARY(4, "전설"),
    MYTHIC(5, "신화"); // MYTHIC, EPIC 등 상수 추가 및 정의

    private final int code;
    private final String description;

    EventGrade(int code, String description) {
        this.code = code;
        this.description = description;
    }

    public int getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    // 코드를 통해 EventGrade를 찾아주는 static 메서드 추가
    public static EventGrade fromCode(int code) {
        for (EventGrade grade : EventGrade.values()) {
            if (grade.code == code) {
                return grade;
            }
        }
        // 적절한 등급을 찾지 못했을 경우 기본값 또는 예외 처리
        // 여기서는 COMMON을 기본값으로 반환하도록 합니다.
        System.err.println("Warning: Unknown EventGrade code: " + code + ". Returning COMMON.");
        return COMMON; 
    }
}