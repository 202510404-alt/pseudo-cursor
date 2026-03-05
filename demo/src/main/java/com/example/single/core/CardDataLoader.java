package com.example.single.core;

import com.example.assets.AssetPaths;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * resources에 있는 card.csv를 읽어서 CardDef 목록으로 변환합니다.
 * - card.csv의 컬럼 순서를 그대로 신뢰합니다.
 * - UTF-8 인코딩을 사용합니다.
 */
public final class CardDataLoader {

    private CardDataLoader() {
    }

    /**
     * card.csv의 모든 카드를 로드합니다.
     */
    public static List<CardDef> loadAll() {
        List<CardDef> result = new ArrayList<>();

        InputStream in = CardDataLoader.class.getResourceAsStream(AssetPaths.CARD_CSV);
        if (in == null) {
            throw new IllegalStateException("card.csv 리소스를 찾을 수 없습니다: " + AssetPaths.CARD_CSV);
        }

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(in, StandardCharsets.UTF_8))) {

            String line;
            boolean first = true;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) {
                    continue;
                }
                // 첫 줄(헤더) 스킵
                if (first) {
                    first = false;
                    continue;
                }

                String[] parts = line.split(",");
                if (parts.length < 13) {
                    // desc까지 포함하면 13개 이상이어야 함
                    continue;
                }

                try {
                    int idx = 0;
                    int no = Integer.parseInt(parts[idx++].trim());
                    String name = parts[idx++].trim();
                    int grade = Integer.parseInt(parts[idx++].trim());
                    int costType = Integer.parseInt(parts[idx++].trim());
                    int costVal = Integer.parseInt(parts[idx++].trim());
                    int atk = Integer.parseInt(parts[idx++].trim());
                    int hp = Integer.parseInt(parts[idx++].trim());
                    int def = Integer.parseInt(parts[idx++].trim());
                    int spd = Integer.parseInt(parts[idx++].trim());
                    int turnGauge = Integer.parseInt(parts[idx++].trim());
                    int energyTick = Integer.parseInt(parts[idx++].trim());
                    int trait = Integer.parseInt(parts[idx++].trim());

                    // 나머지 전체를 desc로 취급 (콤마가 들어가도 이어붙게끔)
                    StringBuilder descBuilder = new StringBuilder();
                    while (idx < parts.length) {
                        if (descBuilder.length() > 0) {
                            descBuilder.append(",");
                        }
                        descBuilder.append(parts[idx++]);
                    }
                    String desc = descBuilder.toString().trim();

                    result.add(new CardDef(
                            no,
                            name,
                            grade,
                            costType,
                            costVal,
                            atk,
                            hp,
                            def,
                            spd,
                            turnGauge,
                            energyTick,
                            trait,
                            desc
                    ));
                } catch (NumberFormatException e) {
                    // 잘못된 숫자 형식이 있으면 해당 줄만 스킵하고 계속 진행
                    // (필요하면 나중에 로깅 추가 가능)
                }
            }
        } catch (IOException e) {
            throw new RuntimeException("card.csv를 읽는 중 오류가 발생했습니다.", e);
        }

        return result;
    }
}

