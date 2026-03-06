package com.example.single.console;

import com.example.single.core.EventDataLoader;
import com.example.single.core.EventDefinition;
import com.example.single.core.EventGrade; // EventGrade import 추가
import com.example.single.core.SeedGenerator;
import com.example.single.core.StageContent;
import com.example.single.core.StageContentGenerator;

import java.util.List;
import java.util.Scanner;

public class SingleConsoleMain {

    private static final String EVENT_DATA_PATH = "/data/events.csv"; // 리소스 경로

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("====== 싱글 플레이어 게임 시작 ======");

        // 1. 시드 생성
        SeedGenerator seedGenerator = new SeedGenerator(); // public 생성자 호출
        long gameSeed = seedGenerator.generateSeed(); // generateSeed 메서드 호출
        System.out.println("게임 시드: " + gameSeed);

        // 2. 이벤트 데이터 로드
        EventDataLoader dataLoader = new EventDataLoader(EVENT_DATA_PATH);
        List<EventDefinition> eventDefinitions = dataLoader.loadEventDefinitions();

        if (eventDefinitions.isEmpty()) {
            System.err.println("이벤트 데이터를 로드하는 데 실패했습니다. 게임을 시작할 수 없습니다.");
            return;
        }
        System.out.println("총 " + eventDefinitions.size() + "개의 이벤트 정의 로드 완료.");

        // 3. 스테이지 콘텐츠 생성기 초기화
        // StageContentGenerator는 로드된 이벤트 정의 리스트를 받습니다.
        StageContentGenerator stageContentGenerator = new StageContentGenerator(eventDefinitions); 

        int currentFloor = 1;
        boolean playing = true;

        while (playing) {
            System.out.println("\n--- " + currentFloor + "층 ---");

            // 4. 현재 층의 콘텐츠 생성
            // generateStageContent 메서드 호출
            StageContent stageContent = stageContentGenerator.generateStageContent(gameSeed, currentFloor);

            // 5. 생성된 콘텐츠 정보 출력 (StageContent에서 getEventDefinition() 사용)
            EventDefinition currentEvent = stageContent.getEventDefinition();

            System.out.println("이벤트 발생!");
            System.out.println("유형: " + currentEvent.getType());       // getType() 호출
            System.out.println("이름: " + currentEvent.getName());       // getName() 호출
            System.out.println("설명: " + currentEvent.getDescription()); // getDescription() 호출
            System.out.println("등급: " + currentEvent.getGrade().getDescription()); // getGrade().getDescription() 호출

            // TODO: 실제 이벤트 처리 로직 구현 (예: 플레이어 HP 회복, 카드 획득 등)
            System.out.println("[이벤트 처리 로직 Placeholder]");

            System.out.print("다음 층으로 진행하시겠습니까? (y/n): ");
            String input = scanner.nextLine();

            if (input.equalsIgnoreCase("y")) {
                currentFloor++;
                // TODO: 층 진행 시 게임 상태 업데이트 로직 추가 (예: 플레이어 상태 변화, 적 등장 등)
                System.out.println("[게임 상태 업데이트 Placeholder]");
            } else {
                playing = false;
                System.out.println("게임을 종료합니다.");
            }
        }

        scanner.close();
        System.out.println("====== 게임 종료 ======");
    }
}