package com.example.single.core;

public class EventDefinition {
    private final int id;
    private final String type;
    private final String name;
    private final String description;
    private final EventGrade grade;

    // EventDataLoader에서 사용되는 생성자 추가
    public EventDefinition(int id, String type, String name, String description, EventGrade grade) {
        this.id = id;
        this.type = type;
        this.name = name;
        this.description = description;
        this.grade = grade;
    }

    public int getId() {
        return id;
    }

    public String getType() {
        return type;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    public EventGrade getGrade() {
        return grade;
    }
}