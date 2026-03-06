package com.example.single.core;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class EventDataLoader {

    private final String filePath;

    public EventDataLoader(String filePath) {
        this.filePath = filePath;
    }

    public List<EventDefinition> loadEventDefinitions() {
        List<EventDefinition> eventDefinitions = new ArrayList<>();
        // getClass().getResourceAsStream()을 사용하여 JAR 내의 리소스도 읽을 수 있게 합니다.
        try (InputStream is = getClass().getResourceAsStream(filePath);
             BufferedReader reader = new BufferedReader(new InputStreamReader(is))) {

            String line;
            boolean isFirstLine = true; // CSV 헤더 스킵을 위한 플래그
            while ((line = reader.readLine()) != null) {
                if (isFirstLine) {
                    isFirstLine = false;
                    continue; // 헤더 스킵
                }
                String[] parts = line.split(",");
                if (parts.length >= 4) { // 최소 4개의 필드 (type, name, desc, grade_code)
                    String type = parts[0].trim();
                    String name = parts[1].trim();
                    String description = parts[2].trim();
                    int gradeCode = Integer.parseInt(parts[3].trim());

                    // EventGrade.fromCode() 메서드 사용
                    EventGrade grade = EventGrade.fromCode(gradeCode);
                    eventDefinitions.add(new EventDefinition(type, name, description, grade));
                }
            }
        } catch (IOException | NumberFormatException e) {
            System.err.println("Error loading event definitions from " + filePath + ": " + e.getMessage());
            e.printStackTrace();
        }
        return eventDefinitions;
    }
}