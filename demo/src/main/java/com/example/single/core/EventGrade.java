package com.example.single.core;

// 123
/**
 * 이벤트 등급.
 * 0(일반), 1(희귀), 2(에픽), 3(전설), 4(신화)
 * 등급 코드와 함께, 해당 등급이 선택될 bValue(0-9999)의 상한선(threshold) 및
 * 사용자에게 표시될 이름(displayName)을 포함하도록 확장되었습니다.
 */
public enum EventGrade {
    // bValue 기준: 0-9999
    // MYTHIC: bValue < 50
    // LEGENDARY: bValue < 300 (>=50)
    // EPIC: bValue < 1000 (>=300)
    // RARE: bValue < 4000 (>=1000)
    // COMMON: bValue >= 4000 (Integer.MAX_VALUE는 사실상 상한 없음 의미)
    MYTHIC(4, 50, "신화"),
    LEGENDARY(3, 300, "전설"),
    EPIC(2, 1000, "에픽"),
    RARE(1, 4000, "희귀"),
    COMMON(0, Integer.MAX_VALUE, "일반"); // COMMON은 모든 임계값을 통과한 경우에 선택되므로 가장 큰 값으로 설정

    private final int code;
    private final int threshold; // 해당 등급이 선택될 bValue의 배타적 상한선 (exclusive upper bound)
    private final String displayName; // UI에 표시될 이름

    EventGrade(int code, int threshold, String displayName) {
        this.code = code;
        this.threshold = threshold;
        this.displayName = displayName;
    }

    public int getCode() {
        return code;
    }

    /**
     * 이 등급이 선택될 확률 값(bValue)의 상한선을 반환합니다.
     * 예를 들어 MYTHIC의 경우 50을 반환하며, bValue가 0 이상 50 미만일 때 MYTHIC이 됩니다.
     * COMMON의 경우 Integer.MAX_VALUE를 반환하여, 다른 등급의 조건에 맞지 않을 경우 기본적으로 선택되도록 합니다.
     * @return 해당 등급에 대한 bValue의 상한선 (exclusive)
     */
    public int getThreshold() {
        return threshold;
    }

    /**
     * 이 등급을 사용자에게 표시할 친근한 이름을 반환합니다.
     * @return 등급의 표시 이름 (예: "신화", "전설")
     */
    public String getDisplayName() {
        return displayName;
    }

    /**
     * 주어진 코드(int)에 해당하는 EventGrade를 찾습니다.
     * 코드가 유효하지 않으면 COMMON 등급을 반환합니다.
     * @param code 찾을 이벤트 등급 코드
     * @return 해당 코드의 EventGrade 또는 COMMON
     */
    public static EventGrade fromCode(int code) {
        for (EventGrade g : values()) {
            if (g.code == code) return g;
        }
        return COMMON;
    }

    /**
     * bValue(0-9999 범위의 정수)에 따라 적절한 EventGrade를 결정합니다.
     * StageContentGenerator의 등급 결정 로직을 이 열거형 안으로 이동시켜 중앙화합니다.
     * MYTHIC부터 COMMON 순서로 임계값을 확인하여 가장 먼저 조건을 만족하는 등급을 반환합니다.
     * @param bValue 로그 시드의 소수부에서 추출된 0-9999 범위의 값
     * @return bValue에 따라 결정된 EventGrade
     */
    public static EventGrade fromBValue(int bValue) {
        // MYTHIC -> LEGENDARY -> EPIC -> RARE -> COMMON 순으로 임계값을 확인합니다.
        // Enum의 선언 순서가 MYTHIC부터 COMMON까지 내려오므로, values() 순회로 쉽게 처리 가능합니다.
        for (EventGrade grade : values()) {
            if (bValue < grade.getThreshold()) {
                return grade;
            }
        }
        // 이론적으로는 COMMON의 threshold가 Integer.MAX_VALUE이기 때문에 여기까지 도달하지 않아야 합니다.
        // 하지만 혹시 모를 상황을 대비해 COMMON을 반환합니다.
        return COMMON;
    }
}