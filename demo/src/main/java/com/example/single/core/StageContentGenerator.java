package com.example.single.core;

import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;

public class StageContentGenerator {

    private final List<EventDefinition> allEventDefinitions;
    private final Random random;

    // 이벤트 등급별 확률 임계치 (0.0 ~ 1.0 사이, 누적 확률)
    // 예: COMMON (0.0~0.5), RARE (0.5~0.8), EPIC (0.8~0.95), LEGENDARY (0.95~0.99), MYTHIC (0.99~1.0)
    // 이 맵을 사용하여 generateEventDefinition에서 등급을 결정합니다.
    private static final Map<EventGrade, Double> EVENT_GRADE_THRESHOLDS = Map.of(
        EventGrade.COMMON, 0.50,
        EventGrade.RARE, 0.80,
        EventGrade.EPIC, 0.95,
        EventGrade.LEGENDARY, 0.99,
        EventGrade.MYTHIC, 1.00 // MYTHIC, EPIC 등 EventGrade 상수 사용
    );

    // 생성자 수정: EventDataLoader를 통해 로드된 EventDefinition 리스트를 받도록 합니다.
    public StageContentGenerator(List<EventDefinition> eventDefinitions) {
        this.allEventDefinitions = eventDefinitions;
        this.random = new Random();
    }

    // 시드와 현재 층 번호를 기반으로 StageContent를 생성하는 메서드
    public StageContent generateStageContent(long seed, int currentFloor) {
        this.random.setSeed(seed + currentFloor); // 시드와 층을 기반으로 랜덤 시드 설정
        EventDefinition event = generateEventDefinition();
        return new StageContent(event);
    }

    // 무작위 EventDefinition을 선택하고 등급 확률에 따라 조정하는 로직
    private EventDefinition generateEventDefinition() {
        if (allEventDefinitions.isEmpty()) {
            throw new IllegalStateException("Event definitions are not loaded.");
        }

        // 0.0 이상 1.0 미만의 랜덤 값 생성
        double gradeRoll = random.nextDouble();

        EventGrade selectedGrade = EventGrade.COMMON; // 기본값
        for (Map.Entry<EventGrade, Double> entry : EVENT_GRADE_THRESHOLDS.entrySet()) {
            if (gradeRoll < entry.getValue()) {
                selectedGrade = entry.getKey();
                break;
            }
        }
        
        // 선택된 등급의 이벤트만 필터링
        List<EventDefinition> filteredEvents = allEventDefinitions.stream()
                .filter(event -> event.getGrade() == selectedGrade)
                .collect(Collectors.toList());

        // 해당 등급의 이벤트가 없으면, 전체 이벤트에서 무작위 선택 또는 기본 이벤트 반환
        if (filteredEvents.isEmpty()) {
            System.err.println("Warning: No events found for grade " + selectedGrade + ". Selecting from all events.");
            filteredEvents = allEventDefinitions;
        }

        // 필터링된 이벤트 중 무작위로 하나 선택
        int randomIndex = random.nextInt(filteredEvents.size());
        return filteredEvents.get(randomIndex);
    }
}