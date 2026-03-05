package com.example.single.core;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 적이 보유하는 카드 목록입니다.
 * 플레이어처럼 내부 번호 시스템은 필요 없고,
 * 단순 리스트와 랜덤 선택 정도만 담당합니다.
 */
public class EnemyCardBag {

    private final List<CardInstance> cards = new ArrayList<>();

    public void add(CardInstance instance) {
        cards.add(instance);
    }

    public int size() {
        return cards.size();
    }

    public CardInstance get(int index) {
        return cards.get(index);
    }

    public CardInstance remove(int index) {
        return cards.remove(index);
    }

    public List<CardInstance> asReadOnlyList() {
        return Collections.unmodifiableList(cards);
    }
}

