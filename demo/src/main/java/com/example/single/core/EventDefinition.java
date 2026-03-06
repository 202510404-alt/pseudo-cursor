package com.example.single.core;

public class EventDefinition {
    private final String type;
    private final String name;
    private final String description;
    private final EventGrade grade; // EventGrade 타입 사용

    // 생성자 추가
    public EventDefinition(String type, String name, String description, EventGrade grade) {
        this.type = type;
        this.name = name;
        this.description = description;
        this.grade = grade;
    }

    // Getter 메서드 추가
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