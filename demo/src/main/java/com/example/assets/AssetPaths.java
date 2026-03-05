package com.example.assets;

/**
 * 게임 자산(예: CSV, 이미지 등)의 경로를 한 곳에서 관리하기 위한 헬퍼입니다.
 * 나중에 card.csv를 resources 쪽으로 옮길 때도 이 상수만 수정하면 되도록 설계합니다.
 */
public final class AssetPaths {

    private AssetPaths() {
    }

    /**
     * 카드 정의 CSV의 리소스 경로입니다.
     * 현재는 임시 값이며, 실제 파일 이동 후에 맞춰 조정합니다.
     */
    public static final String CARD_CSV = "/com/example/assets/card/card.csv";
}

