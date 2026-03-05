package com.example.single.core;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 플레이어가 보유하는 카드 배낭입니다.
 * - 최대 100장까지 보관
 * - 내부적으로는 "플레이어 카드 번호"를 1부터 부여해서 관리
 * - 삭제 시에는 가장 마지막 카드를 앞으로 당겨와서 빈자리를 채웁니다.
 *   (번호는 내부용이므로, 겉 UI에서 이 번호를 직접 보여주지는 않습니다.)
 */
public class PlayerCardBag {

    private static final int MAX_SIZE = 100;

    // 0 기반 인덱스, 플레이어 카드 번호는 (index + 1)
    private final List<CardInstance> cards = new ArrayList<>();

    /**
     * 카드 추가.
     * @return 부여된 플레이어 카드 번호 (1부터 시작)
     */
    public int add(CardInstance instance) {
        if (cards.size() >= MAX_SIZE) {
            throw new IllegalStateException("플레이어 카드 배낭이 가득 찼습니다. (최대 " + MAX_SIZE + "장)");
        }
        cards.add(instance);
        return cards.size(); // 마지막 인덱스 + 1
    }

    /**
     * 플레이어 카드 번호로 조회 (1-based).
     * 없으면 null.
     */
    public CardInstance get(int playerCardNo) {
        int idx = playerCardNoToIndex(playerCardNo);
        if (idx < 0 || idx >= cards.size()) {
            return null;
        }
        return cards.get(idx);
    }

    /**
     * 플레이어 카드 번호로 삭제.
     * 성공 시 true, 실패(없는 번호) 시 false.
     * 삭제 시 마지막 카드를 앞으로 당겨와서 빈자리를 메웁니다.
     */
    public boolean remove(int playerCardNo) {
        int idx = playerCardNoToIndex(playerCardNo);
        if (idx < 0 || idx >= cards.size()) {
            return false;
        }

        int lastIdx = cards.size() - 1;
        if (idx != lastIdx) {
            CardInstance last = cards.get(lastIdx);
            cards.set(idx, last);
        }
        cards.remove(lastIdx);
        return true;
    }

    /**
     * 플레이어 카드 번호로 삭제하고, 삭제된 카드를 반환합니다.
     * 없으면 null.
     */
    public CardInstance removeAndGet(int playerCardNo) {
        int idx = playerCardNoToIndex(playerCardNo);
        if (idx < 0 || idx >= cards.size()) {
            return null;
        }

        CardInstance removed = cards.get(idx);

        int lastIdx = cards.size() - 1;
        if (idx != lastIdx) {
            CardInstance last = cards.get(lastIdx);
            cards.set(idx, last);
        }
        cards.remove(lastIdx);
        return removed;
    }

    /**
     * 현재 가지고 있는 카드 수.
     */
    public int size() {
        return cards.size();
    }

    /**
     * 읽기 전용 리스트를 반환합니다.
     * 인덱스 0이 플레이어 카드 번호 1에 해당합니다.
     */
    public List<CardInstance> asReadOnlyList() {
        return Collections.unmodifiableList(cards);
    }

    private int playerCardNoToIndex(int playerCardNo) {
        return playerCardNo - 1;
    }
}

