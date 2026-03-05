package com.example.single.core;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 로그 함수 기반 시드를 이용해 스테이지의 성격(전투/이벤트)과
 * 이벤트 등급/내용을 결정하는 유틸리티입니다.
 *
 * get_stage_content(mixed_log_seed) 형태의 정적 메서드를 제공합니다.
 */
public final class StageContentGenerator {

    // 전투 vs 이벤트 비율: 3 : 7 (30% : 70%)
    private static final double BATTLE_PROBABILITY = 30.0;

    // 이벤트 등급 누적 확률 테이블 (0~10000)
    // Rank 4 (<50), Rank 3 (<300), Rank 2 (<1000), Rank 1 (<4000), Rank 0 (나머지)
    // 인덱스: 0=COMMON, 1=RARE, 2=EPIC, 3=LEGENDARY, 4=MYTHIC
    private static final int[] EVENT_GRADE_THRESHOLDS = {
            10000, // COMMON (나머지 구간용, 실제 로직에서는 else 처리로 사용)
            4000,  // RARE
            1000,  // EPIC
            300,   // LEGENDARY
            50     // MYTHIC
    };

    // 이벤트 데이터 캐시
    private static Map<EventGrade, List<EventDefinition>> cachedEvents;

    private StageContentGenerator() {
    }

    private static Map<EventGrade, List<EventDefinition>> getEventTable() {
        if (cachedEvents == null) {
            cachedEvents = EventDataLoader.loadByGrade();
        }
        return cachedEvents;
    }

    /**
     * mixed_log_seed는 로그 함수를 섞어 만든 소수값이라고 가정합니다.
     * 여기서는 소수부 문자열을 기준으로 구역 A/B를 나눠 사용합니다.
     */
    public static StageContent get_stage_content(double mixed_log_seed) {
        // 1. 소수부 문자열 추출
        BigDecimal bd = new BigDecimal(mixed_log_seed);
        BigDecimal fractional = bd.abs().remainder(BigDecimal.ONE);
        String fracStr = fractional.toPlainString(); // "0.xxxxx"

        int dotIndex = fracStr.indexOf('.');
        String digits;
        if (dotIndex >= 0 && dotIndex + 1 < fracStr.length()) {
            digits = fracStr.substring(dotIndex + 1);
        } else {
            digits = "";
        }

        // 부족하면 30자리 정도까지 패딩
        StringBuilder sb = new StringBuilder(digits);
        while (sb.length() < 30) {
            sb.append('0');
        }
        digits = sb.toString();

        // 구역 A: 소수점 1~2자리 사용 (3:7 비율로 전투/이벤트 결정)
        String aStr = digits.substring(0, 2); // 0~99
        int aVal = Integer.parseInt(aStr);
        double aPercent = (aVal / 100.0) * 100.0; // 0~99 -> 0~99.xx%

        boolean isBattle = aPercent < BATTLE_PROBABILITY;

        // 전투 스테이지면 이벤트 정보는 null, 등급은 COMMON으로 채우고 반환
        if (isBattle) {
            return new StageContent(true, EventGrade.COMMON, null);
        }

        // 구역 B: 소수점 10~13자리 사용 (이벤트 등급 결정, 0~9999)
        String bStr = digits.substring(9, 13); // 10~13번째 자리 (0-based index 9~12)
        int bVal = Integer.parseInt(bStr);     // 0~9999
        EventGrade grade = pickGradeByProbability(bVal);

        // 구역 C: 소수점 14~17자리 사용 (동일 등급 내 이벤트 선택, 0~9999)
        String cStr = digits.substring(13, 17); // 14~17번째 자리 (0-based index 13~16)
        int cVal = Integer.parseInt(cStr);      // 0~9999

        EventDefinition event = pickEventOfGrade(grade, cVal);

        return new StageContent(false, grade, event);
    }

    private static EventGrade pickGradeByProbability(int value0To9999) {
        // value는 0~9999 범위
        if (value0To9999 < 50) {           // 0.5% 미만
            return EventGrade.MYTHIC;      // 4
        } else if (value0To9999 < 300) {   // 3.0% 미만
            return EventGrade.LEGENDARY;   // 3
        } else if (value0To9999 < 1000) {  // 10.0% 미만
            return EventGrade.EPIC;        // 2
        } else if (value0To9999 < 4000) {  // 40.0% 미만
            return EventGrade.RARE;        // 1
        } else {
            return EventGrade.COMMON;      // 나머지
        }
    }

    private static EventDefinition pickEventOfGrade(EventGrade grade, int sectorCValue) {
        Map<EventGrade, List<EventDefinition>> table = getEventTable();
        List<EventDefinition> list = table.get(grade);
        if (list == null || list.isEmpty()) {
            return null;
        }

        int n = list.size();
        // 4자리 값(0~9999)을 [0, n-1]로 매핑
        int idx = (sectorCValue * n) / 10000;
        if (idx < 0) idx = 0;
        if (idx >= n) idx = n - 1;
        return list.get(idx);
    }
}

