package com.example.single.core;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional; // Optional 클래스를 사용하기 위해 임포트

public class EventDataLoader {
    private static final String CSV_FILE_PATH = "/events.csv"; // CSV 파일 경로 (resources 폴더 내)

    public List<EventDefinition> loadEvents() {
        List<EventDefinition> events = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(
                Objects.requireNonNull(EventDataLoader.class.getResourceAsStream(CSV_FILE_PATH))))) {
            String line;
            reader.readLine(); // CSV 헤더 스킵
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length == 5) { // id, type, name, description, gradeCode
                    int id = Integer.parseInt(parts[0].trim());
                    String type = parts[1].trim();
                    String name = parts[2].trim();
                    String description = parts[3].trim();
                    int gradeCode = Integer.parseInt(parts[4].trim());

                    // EventGrade.fromCode는 Optional<EventGrade>를 반환하므로, 이를 정확히 처리해야 합니다.
                    // 'Type mismatch: cannot convert from EventGrade to Optional<EventGrade>' 오류는
                    // 이전에 fromCode가 EventGrade를 반환한다고 가정했거나, Optional을 잘못 처리했을 때 발생할 수 있습니다.
                    Optional<EventGrade> optionalGrade = EventGrade.fromCode(gradeCode);
                    
                    if (optionalGrade.isPresent()) {
                         // EventDefinition 생성자가 EventGrade 타입을 받으므로, optionalGrade.get()으로 추출합니다.
                         events.add(new EventDefinition(id, type, name, description, optionalGrade.get()));
                    } else {
                        System.err.println("Warning: Unknown EventGrade code found for event ID " + id + ": " + gradeCode + ". Event skipped.");
                    }
                } else {
                    System.err.println("Warning: Malformed event data line (expected 5 parts): " + line);
                }
            }
        } catch (Exception e) {
            System.err.println("Error loading events from " + CSV_FILE_PATH + ": " + e.getMessage());
            e.printStackTrace();
        }
        return events;
    }
}