package com.example.single.core;

/**
 * 한 스테이지의 성격(전투/이벤트)과 선택된 이벤트 정보를 담는 DTO입니다.
 */
public class StageContent {

    public final boolean isBattle;
    public final EventGrade eventGrade;
    public final EventDefinition eventDefinition; // 전투 스테이지면 null 가능

    public StageContent(boolean isBattle, EventGrade eventGrade, EventDefinition eventDefinition) {
        this.isBattle = isBattle;
        this.eventGrade = eventGrade;
        this.eventDefinition = eventDefinition;
    }
}

