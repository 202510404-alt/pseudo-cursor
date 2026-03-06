package com.example.single.core;

public class StageContent {
    private final EventDefinition eventDefinition;
    // 다른 필요한 필드들을 여기에 추가할 수 있습니다.

    // 생성자 추가
    public StageContent(EventDefinition eventDefinition) {
        this.eventDefinition = eventDefinition;
    }

    // getEventDefinition 메서드 추가
    public EventDefinition getEventDefinition() {
        return eventDefinition;
    }

    @Override
    public String toString() {
        return "StageContent [eventDefinition=" + eventDefinition.getName() + 
               ", grade=" + eventDefinition.getGrade().getDescription() + "]";
    }
}