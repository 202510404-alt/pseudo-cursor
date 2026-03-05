package com.example.single.core;

/**
 * 하나의 이벤트 정의를 나타냅니다.
 * events.csv의 한 줄과 1:1로 매핑됩니다.
 */
public class EventDefinition {

    public final int id;
    public final EventGrade grade;
    public final String name;
    public final String desc;

    public EventDefinition(int id, EventGrade grade, String name, String desc) {
        this.id = id;
        this.grade = grade;
        this.name = name;
        this.desc = desc;
    }
}

