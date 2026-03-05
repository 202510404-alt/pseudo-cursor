package com.example.single.core;

import java.math.BigDecimal;

/**
 * 결정론적인 방식으로 게임용 시드를 생성하는 SeedGenerator 입니다.
 *
 * 요구사항 요약:
 * - 입력: 4자리 정수 masterSeed (예: 1234)
 * - 절차를 3회 반복:
 *   1) 현재 seed의 앞 2자리(d1d2)를 log10() 입력값으로 사용
 *   2) 같은 seed의 뒤 2자리(d3d4)를, 소수점 아래 자리 인덱스로 사용
 *   3) log10 결과의 소수부에서 해당 인덱스부터 일정 길이만큼 숫자를 뽑아 segment로 사용
 *   4) segment를 이어붙여 최종 gameSeed를 만든다
 *   5) 다음 반복의 seed는 방금 뽑은 segment(정수로 해석)를 사용
 *
 * - 소수부 자릿수가 부족할 경우 0으로 패딩한다.
 * - 중간 계산 과정은 콘솔 로그로 출력한다.
 */
public final class SeedGenerator {

    // 각 반복에서 뽑아낼 소수부 숫자 길이
    private static final int SEGMENT_LENGTH = 4;
    // 반복 횟수
    private static final int ITERATIONS = 3;

    private SeedGenerator() {
    }

    /**
     * masterSeed(4자리)를 기반으로 결정론적 gameSeed를 생성합니다.
     */
    public static long generateGameSeed(int masterSeed) {
        // 4자리 정수로 정규화 (음수 방지 및 0 패딩)
        int currentSeed = Math.abs(masterSeed) % 10000;

        System.out.println("=== SeedGenerator 시작 ===");
        System.out.println("입력 masterSeed: " + masterSeed + " -> 정규화: " + String.format("%04d", currentSeed));

        StringBuilder combinedDigits = new StringBuilder();

        for (int i = 1; i <= ITERATIONS; i++) {
            String seedStr = String.format("%04d", currentSeed);
            int front = Integer.parseInt(seedStr.substring(0, 2)); // d1d2
            int back = Integer.parseInt(seedStr.substring(2, 4));  // d3d4

            if (front <= 0) {
                // log10(0) 방지: 1로 대체
                front = 1;
            }

            double logVal = Math.log10(front);
            BigDecimal bd = new BigDecimal(logVal);

            // 소수부만 추출 (예: 0.3010...)
            BigDecimal fractional = bd.abs().remainder(BigDecimal.ONE);
            String fracStr = fractional.toPlainString(); // "0.xxxxx" 형태
            String digits;
            int dotIndex = fracStr.indexOf('.');
            if (dotIndex >= 0 && dotIndex + 1 < fracStr.length()) {
                digits = fracStr.substring(dotIndex + 1); // 소수점 아래 숫자만
            } else {
                digits = "";
            }

            // 뒤 2자리(back)를 시작 인덱스로 사용 (0 기반)
            int startIndex = back;
            if (startIndex < 0) startIndex = 0;

            // 필요한 길이만큼 확보되도록 0으로 패딩
            if (digits.length() < startIndex + SEGMENT_LENGTH) {
                StringBuilder padded = new StringBuilder(digits);
                while (padded.length() < startIndex + SEGMENT_LENGTH) {
                    padded.append('0');
                }
                digits = padded.toString();
            }

            String segment = digits.substring(startIndex, startIndex + SEGMENT_LENGTH);
            combinedDigits.append(segment);

            System.out.println("[반복 " + i + "]");
            System.out.println("  currentSeed  : " + seedStr);
            System.out.println("  앞 2자리(front) : " + front + " -> log10(front) = " + fracStr);
            System.out.println("  뒤 2자리(back)  : " + back + " -> 소수부 시작 인덱스");
            System.out.println("  소수부(digits)  : " + digits);
            System.out.println("  추출 segment    : " + segment);

            // 다음 반복용 seed를 segment 기반으로 갱신
            try {
                currentSeed = Integer.parseInt(segment) % 10000;
            } catch (NumberFormatException e) {
                // 혹시 숫자로 변환이 안 되면 0으로 처리
                currentSeed = 0;
            }
        }

        // 최종 gameSeed 조합
        long gameSeed;
        try {
            gameSeed = Long.parseLong(combinedDigits.toString());
        } catch (NumberFormatException e) {
            // 전부 0이거나 이상할 경우 masterSeed를 혼합
            gameSeed = Math.abs(masterSeed);
        }

        System.out.println("최종 gameSeed: " + gameSeed);
        System.out.println("=== SeedGenerator 종료 ===");

        return gameSeed;
    }
}

