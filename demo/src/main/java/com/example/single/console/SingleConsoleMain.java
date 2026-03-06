package com.example.single.console;

import com.example.single.core.EventDataLoader;
import com.example.single.core.EventDefinition;
// import com.example.single.core.EventGrade; // 사용되지 않아 제거
import com.example.single.core.SeedGenerator;
import com.example.single.core.StageContent;
import com.example.single.core.StageContentGenerator;

import java.util.List;
import java.util.Scanner; // 사용자 입력을 위해 필요

public class SingleConsoleMain {

    public static void main(String[] args) {
        System.out.println("--- Pseudo Cursor - Single Player Console ---");

        // 1. Seed 생성
        SeedGenerator seedGenerator = new SeedGenerator();
        long gameSeed = seedGenerator.generateSeed();
        System.out.println("게임 시작 시드: " + gameSeed);

        // 2. 이벤트 데이터 로드
        EventDataLoader eventDataLoader = new EventDataLoader();
        List<EventDefinition> eventDefinitions = eventDataLoader.loadEventDefinitions("events.csv");

        if (eventDefinitions.isEmpty()) {
            System.err.println("오류: 이벤트 정의를 로드할 수 없습니다. 'events.csv' 파일이 올바른 경로에 있는지 확인하세요.");
            return;
        }
        System.out.println("로드된 이벤트 수: " + eventDefinitions.size());

        // 3. 스테이지 콘텐츠 생성기 초기화
        StageContentGenerator contentGenerator = new StageContentGenerator(eventDefinitions);

        int currentFloor = 1;
        final int MAX_FLOOR = 5; // 임시로 5층까지 진행

        // 사용자 입력을 위한 Scanner를 try-with-resources 구문으로 감싸 자원 누수 방지
        try (Scanner scanner = new Scanner(System.in)) {
            while (currentFloor <= MAX_FLOOR) {
                System.out.println("\n--- 현재 층: " + currentFloor + " ---");

                // 층에 따른 스테이지 콘텐츠 생성
                StageContent stageContent = contentGenerator.generateStageContent(gameSeed, currentFloor);
                EventDefinition event = stageContent.getEventDefinition();

                System.out.println("이벤트 발생! 종류: " + event.getType() + ", 이름: " + event.getName());
                System.out.println("설명: " + event.getDescription());
                System.out.println("등급: " + event.getGrade().getDescription()); // EventGrade의 getDescription() 사용

                // TODO: 실제 이벤트 처리 로직 구현 (예: 플레이어 HP 회복, 카드 획득 등)
                // 현재는 단순히 이벤트 정보를 출력하는 것으로 만족합니다.
                System.out.println("이벤트 처리 로직 (TODO): 플레이어 상태 변화가 여기에 반영됩니다.");

                System.out.print("다음 층으로 진행하려면 Enter를 누르세요...");
                scanner.nextLine(); // 사용자 입력 대기

                currentFloor++;

                // TODO: 층 진행 시 게임 상태 업데이트 로직 추가 (예: 플레이어 상태 변화, 적 등장 등)
                // 이 부분은 게임 상태를 관리하는 별도의 클래스가 필요할 수 있습니다.
            }
        } // try-with-resources에 의해 Scanner는 여기서 자동 닫힘

        System.out.println("\n--- 모든 층을 완료했습니다! 게임 종료 ---");
    }
}