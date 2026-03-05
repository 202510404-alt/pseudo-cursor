package com.example.single.core;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * CardDef들을 번호(no) 기준으로 조회하기 위한 간단한 카드 도감입니다.
 * - 게임 시작 시 card.csv를 한 번 읽어 들여 Map에 저장해 둡니다.
 */
public class CardLibrary {

    private final Map<Integer, CardDef> byNo = new HashMap<>();

    public CardLibrary(List<CardDef> cards) {
        for (CardDef def : cards) {
            byNo.put(def.no, def);
        }
    }

    /**
     * 카드 번호로 도감 정보를 조회합니다.
     * 없으면 null을 반환합니다.
     */
    public CardDef getByNo(int no) {
        return byNo.get(no);
    }
}

