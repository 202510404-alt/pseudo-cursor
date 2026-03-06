package com.example.single.core;

import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

public class StageContentGenerator {
    private final List<EventDefinition> eventDefinitions;
    private final Random random;

    // Event Grade Thresholds (확률)
    // 0-49: COMMON (50%)
    // 50-74: UNCOMMON (25%)
    // 75-89: RARE (15%)
    // 90-97: EPIC (8%)
    // 98-99: MYTHIC (2%)
    private static final int COMMON_THRESHOLD = 50;
    private static final int UNCOMMON_THRESHOLD = 75;
    private static final int RARE_THRESHOLD = 90;
    private static final int EPIC_THRESHOLD = 98;
    // MYTHIC은 EPIC_THRESHOLD를 초과하는 모든 값

    public StageContentGenerator(List<EventDefinition> eventDefinitions) {
        this.eventDefinitions = eventDefinitions;
        this.random = new Random(); // Random 객체 초기화
    }

    /**
     * 특정 시드와 현재 층에 기반하여 스테이지 콘텐츠를 생성합니다.
     * 이벤트 등급은 랜덤으로 결정되며, 해당 등급의 이벤트 중 하나가 선택됩니다.
     *
     * @param seed 게임의 고유 시드 (일관된 결과 생성용)
     * @param currentFloor 현재 플레이어가 있는 층 번호
     * @return 생성된 스테이지 콘텐츠 (EventDefinition을 포함)
     */
    public StageContent generateStageContent(long seed, int currentFloor) {
        // 현재 층과 시드를 결합하여 Random 객체를 시드합니다.
        // 이렇게 하면 각 층마다 고유하면서도 재현 가능한 랜덤 결과가 나옵니다.
        random.setSeed(seed + currentFloor);

        // 1. 현재 층의 이벤트를 위한 등급을 결정합니다.
        // determineEventGrade 메서드에서 EventGrade가 단일 할당되어 'effectively final' 문제가 해결됩니다.
        EventGrade selectedGrade = determineEventGrade(currentFloor);

        // 2. 결정된 등급에 맞는 이벤트 정의들을 필터링합니다.
        List<EventDefinition> candidateEvents = eventDefinitions.stream()
                .filter(event -> event.getGrade() == selectedGrade)
                .collect(Collectors.toList());

        // 3. 만약 해당 등급의 이벤트가 없으면 경고를 출력하고 다른 등급에서 임의의 이벤트를 선택합니다.
        if (candidateEvents.isEmpty()) {
            System.err.println("Warning: No events found for grade " + selectedGrade + " on floor " + currentFloor + ". Falling back to all events.");
            // Fallback: 특정 등급 이벤트가 없으면 모든 이벤트 중에서 무작위로 선택
            if (eventDefinitions.isEmpty()) {
                throw new IllegalStateException("No event definitions loaded. Cannot generate stage content.");
            }
            return new StageContent(eventDefinitions.get(random.nextInt(eventDefinitions.size())));
        }

        // 4. 필터링된 이벤트 중에서 무작위로 하나를 선택합니다.
        EventDefinition chosenEvent = candidateEvents.get(random.nextInt(candidateEvents.size()));

        return new StageContent(chosenEvent);
    }

    /**
     * 현재 층에 따라 이벤트 등급을 결정합니다.
     * (난이도 조절 로직을 여기에 추가할 수 있습니다. 예: 높은 층일수록 희귀 등급 출현율 증가)
     *
     * @param currentFloor 현재 층 번호
     * @return 결정된 이벤트 등급
     */
    private EventGrade determineEventGrade(int currentFloor) {
        // 현재는 층에 관계없이 고정된 확률을 사용하지만,
        // 필요에 따라 currentFloor를 사용하여 확률을 동적으로 조절할 수 있습니다.
        int randVal = random.nextInt(100); // 0-99

        if (randVal < COMMON_THRESHOLD) {
            return EventGrade.COMMON;
        } else if (randVal < UNCOMMON_THRESHOLD) {
            return EventGrade.UNCOMMON;
        } else if (randVal < RARE_THRESHOLD) {
            return EventGrade.RARE;
        } else if (randVal < EPIC_THRESHOLD) {
            return EventGrade.EPIC;
        } else {
            return EventGrade.MYTHIC;
        }
    }
}