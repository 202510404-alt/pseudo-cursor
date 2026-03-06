package com.example.single.core;

import java.util.Random;

public class SeedGenerator {

    private final Random random;

    // 생성자를 public으로 변경하여 외부에서 접근 가능하도록 합니다.
    public SeedGenerator() {
        this.random = new Random();
    }

    // 현재 시간을 기반으로 시드를 생성하는 메서드
    public long generateSeed() {
        return System.nanoTime(); // 현재 시간을 시드로 사용
    }

    // 특정 범위 내의 정수를 생성하는 메서드 (필요에 따라 추가)
    public int generateRandomInt(int min, int max) {
        return random.nextInt((max - min) + 1) + min;
    }
}