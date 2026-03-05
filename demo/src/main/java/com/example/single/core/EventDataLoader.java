package com.example.single.core;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * resources의 events.csv를 읽어 이벤트 정의 목록을 로드합니다.
 */
public final class EventDataLoader {

    private static final String PATH = "/com/example/assets/event/events.csv";

    private EventDataLoader() {
    }

    /**
     * 등급별 이벤트 목록을 로드합니다.
     */
    public static Map<EventGrade, List<EventDefinition>> loadByGrade() {
        Map<EventGrade, List<EventDefinition>> map = new HashMap<>();
        for (EventGrade g : EventGrade.values()) {
            map.put(g, new ArrayList<>());
        }

        InputStream in = EventDataLoader.class.getResourceAsStream(PATH);
        if (in == null) {
            throw new IllegalStateException("events.csv 리소스를 찾을 수 없습니다: " + PATH);
        }

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(in, StandardCharsets.UTF_8))) {

            String line;
            boolean first = true;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#") || line.startsWith("//")) {
                    continue;
                }

                if (first) {
                    // 헤더 스킵
                    first = false;
                    continue;
                }

                String[] parts = line.split(",");
                if (parts.length < 4) {
                    continue;
                }

                try {
                    int id = Integer.parseInt(parts[0].trim());
                    int gradeCode = Integer.parseInt(parts[1].trim());
                    String name = parts[2].trim();

                    StringBuilder descBuilder = new StringBuilder();
                    for (int i = 3; i < parts.length; i++) {
                        if (i > 3) descBuilder.append(",");
                        descBuilder.append(parts[i]);
                    }
                    String descRaw = descBuilder.toString().trim();
                    // '/' 이후는 주석으로 간주하고 잘라냄
                    int commentIdx = descRaw.indexOf('/');
                    String desc = (commentIdx >= 0 ? descRaw.substring(0, commentIdx) : descRaw).trim();

                    EventGrade grade = EventGrade.fromCode(gradeCode);
                    EventDefinition def = new EventDefinition(id, grade, name, desc);
                    map.get(grade).add(def);
                } catch (NumberFormatException e) {
                    // 잘못된 줄은 건너뜀
                }
            }
        } catch (IOException e) {
            throw new RuntimeException("events.csv를 읽는 중 오류가 발생했습니다.", e);
        }

        return map;
    }
}

