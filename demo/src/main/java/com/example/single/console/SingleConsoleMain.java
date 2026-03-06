package com.example.single.console;

import com.example.single.core.Board4x4;
import com.example.single.core.CardDataLoader;
import com.example.single.core.CardDef;
import com.example.single.core.CardInstance;
import com.example.single.core.CardLibrary;
import com.example.single.core.EnemyCardBag;
import com.example.single.core.PlayerCardBag;
// NEW IMPORTS
import com.example.single.core.SeedGenerator;
import com.example.single.core.StageContent; // StageContent 추가
import com.example.single.core.StageContentGenerator; // StageContentGenerator 추가

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.Scanner;

/**
 * 싱글 모드를 콘솔에서 테스트하기 위한 간단한 프로토타입입니다.
 * - 시작 시 card.csv에서 카드 10장을 랜덤으로 뽑아 플레이어 배낭에 넣습니다.
 * - 플레이어는 숫자(1~10)를 눌러 손패에서 카드를 고르고,
 *   이어서 1~4를 눌러 자신의 보드 슬롯에 배치할 수 있습니다.
 * - 보드는 위에 적 4칸, 아래에 플레이어 4칸을 0/1로 표시합니다.
 *   (0 = 비어 있음, 1 = 카드 존재)
 * - 맵을 생성하고 각 노드 타입에 따라 게임이 진행됩니다.
 * - 전투 시 배치와 간단한 전투 로직이 적용됩니다.
 */
public class SingleConsoleMain {

    public static void main(String[] args) {
        // 1. 카드 도감 로드 및 랜덤 객체 초기화
        List<CardDef> allCards = CardDataLoader.loadAll();
        CardLibrary library = new CardLibrary(allCards); // 현재 메인에서는 직접 사용되지 않지만, 도감 역할
        Random rng = new Random(); // 카드 분배 및 적 AI에 사용

        // 2. 시드 생성 및 맵 시스템 초기화
        System.out.println("=== 새 게임 시작 ===");
        int masterSeedInput = 1234; // 기본 마스터 시드
        System.out.print("게임 마스터 시드(4자리 숫자)를 입력하세요 (기본값: 1234): ");
        
        try (Scanner scanner = new Scanner(System.in)) { // Scanner는 try-with-resources로 안전하게 관리
            String seedLine = scanner.nextLine();
            if (!seedLine.isEmpty()) {
                try {
                    masterSeedInput = Integer.parseInt(seedLine);
                } catch (NumberFormatException e) {
                    System.out.println("유효하지 않은 시드 입력입니다. 기본값 1234를 사용합니다.");
                }
            }

            long gameSeed = SeedGenerator.generateGameSeed(masterSeedInput); // 마스터 시드로 게임 시드 생성
            // SeedManager seedManager = new SeedManager(gameSeed); // 게임 시드를 바탕으로 SeedManager 초기화 (없음, 주석 처리)
            // MapSystem mapSystem = new MapSystem(seedManager); // SeedManager를 이용해 MapSystem 초기화 (없음, 주석 처리)

            // mapSystem.generateMap(); // 맵 생성 및 콘솔에 출력 (없음, 주석 처리)

            // 3. 게임 상태 초기화
            Board4x4 board = new Board4x4(); // 게임 보드
            PlayerCardBag playerBag = new PlayerCardBag(); // 플레이어 카드 덱 (손패)

            // 플레이어에게 초기 카드 10장 랜덤 지급
            for (int i = 0; i < 10; i++) {
                CardDef def = allCards.get(rng.nextInt(allCards.size()));
                CardInstance instance = new CardInstance(def, CardInstance.Owner.PLAYER);
                playerBag.add(instance);
            }

            // 전역 저울 HP (게임 전체에 걸쳐 플레이어와 적의 누적 HP)
            int playerScale = 100;
            int enemyScale = 100;

            // 현재 맵 진행도 (층과 해당 층 내의 노드 인덱스)
            int currentFloor = 0; // 0부터 시작하는 층 인덱스
            // int currentPathIndex = 0; // 현재 층에서 선택된 경로의 인덱스 (간단화를 위해 항상 0으로 고정) - 더 이상 사용하지 않음
            final int TOTAL_FLOORS = 5; // 총 5층으로 고정 (MapSystem 없음)

            System.out.println("\n--- 게임 시작! ---");
            System.out.println("규칙: 누적 100 대미지를 먼저 맞는 쪽이 패배.\n");

            // 4. 메인 게임 루프 (맵 진행)
            outerGameLoop:
            while (true) {
                // 게임 종료 조건 확인 (플레이어 패배 또는 모든 층 클리어)
                if (playerScale <= 0) {
                    System.out.println("\n===================================");
                    System.out.println("플레이어 저울 HP가 0이 되어 패배했습니다.");
                    System.out.println("===================================\n");
                    break outerGameLoop;
                }
                if (currentFloor >= TOTAL_FLOORS) {
                    System.out.println("\n===================================");
                    System.out.println("축하합니다! 모든 층을 클리어했습니다!");
                    System.out.println("===================================\n");
                    break outerGameLoop;
                }

                // 현재 층과 노드 정보 가져오기 (MapSystem 없음, StageContentGenerator 활용)
                // StageContentGenerator는 double을 인자로 받으므로 long 타입의 gameSeed를 double로 캐스팅합니다.
                // 이 시드로부터 각 층의 콘텐츠가 결정됩니다.
                StageContent stageContent = StageContentGenerator.get_stage_content((double)gameSeed);
                String currentNodeType = stageContent.isBattle ? "BATTLE" : "EVENT"; // 동적으로 노드 타입 결정

                System.out.println("\n===================================");
                System.out.printf("[ 현재 층: %02d ] [ 노드 타입: %s ]\n", currentFloor + 1, currentNodeType);
                System.out.println("플레이어 저울 HP: " + playerScale + ", 적 저울 HP: " + enemyScale);
                System.out.println("===================================\n");

                // 노드 타입에 따른 처리
                if (stageContent.isBattle) { // 전투 스테이지
                        System.out.println("--- " + currentNodeType + " 전투 시작! ---");
                        
                        // 각 전투 시작 시 보드를 초기화 (이전 전투의 카드 제거)
                        board = new Board4x4();
                        // 적 카드 덱을 전투마다 새로 채우기
                        EnemyCardBag enemyBagForBattle = new EnemyCardBag(); // 이 전투에서만 사용할 적 카드 덱
                        for (int i = 0; i < 4; i++) { // 각 전투마다 4장의 적 카드를 지급
                            CardDef def = allCards.get(rng.nextInt(allCards.size()));
                            CardInstance instance = new CardInstance(def, CardInstance.Owner.ENEMY);
                            enemyBagForBattle.add(instance);
                        }

                        battleLoop:
                        while (playerScale > 0 && enemyScale > 0) {
                            printBoard(board, playerScale, enemyScale); // 현재 보드 상태 출력
                            printPlayerHand(playerBag); // 플레이어 손패 출력

                            System.out.print("손패에서 낼 카드 번호 선택 (1~" + playerBag.size() + ", t=턴 종료, q=게임 종료): ");
                            String line = scanner.nextLine().trim();

                            if (line.equalsIgnoreCase("q")) {
                                break outerGameLoop; // 전체 게임 종료
                            }
                            if (line.equalsIgnoreCase("t")) {
                                // 턴 종료: 적이 카드 1장 랜덤 배치 후 전투 진행
                                enemyPlayRandom(board, enemyBagForBattle, rng); // 적 배치
                                int[] result = resolveBattleStep(board); // 전투 계산
                                int damageToPlayer = result[0];
                                int damageToEnemy = result[1];

                                playerScale -= damageToPlayer; // 플레이어 전역 저울 HP 감소
                                enemyScale -= damageToEnemy;   // 적 전역 저울 HP 감소

                                System.out.println("이번 턴 피해량 - 플레이어:" + damageToPlayer + " 적:" + damageToEnemy);
                                System.out.println("현재 저울 HP - 플레이어:" + playerScale + " 적:" + enemyScale + "\n");

                                if (playerScale <= 0) {
                                    System.out.println("플레이어 저울 HP가 0이 되어 패배했습니다.");
                                    break outerGameLoop; // 게임 오버
                                }
                                if (enemyScale <= 0) {
                                    System.out.println("적 저울 HP가 0이 되어 " + currentNodeType + " 전투에서 승리했습니다!");
                                    break battleLoop; // 현재 전투 승리, 다음 층으로 이동
                                }
                                continue; // 전투 루프 계속
                            }
                            if (line.isEmpty()) {
                                continue;
                            }

                            // 플레이어 카드 배치 로직
                            int handIndex;
                            try {
                                handIndex = Integer.parseInt(line);
                            } catch (NumberFormatException e) {
                                System.out.println("숫자, 't' 또는 'q'만 입력할 수 있습니다.");
                                continue;
                            }

                            if (handIndex < 1 || handIndex > playerBag.size()) {
                                System.out.println("손패 범위를 벗어났습니다.");
                                continue;
                            }

                            CardInstance selected = playerBag.get(handIndex);
                            if (selected == null) {
                                System.out.println("해당 번호의 카드를 찾을 수 없습니다.");
                                continue;
                            }

                            System.out.println("선택한 카드: " + selected.getDef().name +
                                    " (ATK:" + selected.getCurrentAtk() +
                                    " HP:" + selected.getCurrentHp() +
                                    " DEF:" + selected.getCurrentDef() + ")");

                            System.out.print("배치할 칸 선택 (1~4, 0=취소): ");
                            String slotLine = scanner.nextLine().trim();
                            if (slotLine.equals("0")) {
                                System.out.println("배치를 취소했습니다.\n");
                                continue;
                            }

                            int slot;
                            try {
                                slot = Integer.parseInt(slotLine);
                            } catch (NumberFormatException e) {
                                System.out.println("숫자만 입력할 수 있습니다.\n");
                                continue;
                            }

                            if (slot < 1 || slot > 4) {
                                System.out.println("슬롯 번호는 1~4만 가능합니다.\n");
                                continue;
                            }

                            int slotIndex = slot - 1; // 내부 인덱스 0~3
                            if (!board.isEmpty(Board4x4.Side.PLAYER, slotIndex)) {
                                System.out.println("해당 칸에는 이미 카드가 있습니다.\n");
                                continue;
                            }

                            // 손패에서 꺼내어 보드에 올리기
                            CardInstance fromBag = playerBag.removeAndGet(handIndex);
                            CardInstance toPlace = (fromBag != null) ? fromBag : selected; // 방어적 코드
                            board.place(Board4x4.Side.PLAYER, slotIndex, toPlace);

                            System.out.println("카드를 " + slot + "번 칸에 배치했습니다.\n");
                        } // End of battleLoop
                        // 전투 루프가 끝났으나 playerScale이 0이 되어 게임 오버된 경우를 다시 확인
                        if (playerScale <= 0) {
                            break outerGameLoop;
                        }
                } else { // 이벤트 스테이지
                    System.out.println("--- " + currentNodeType + " 스테이지: " + stageContent.eventGrade.getDisplayName() + " 등급 이벤트 ---");
                    if (stageContent.eventDefinition != null) {
                        System.out.println("  이벤트 이름: " + stageContent.eventDefinition.name);
                        System.out.println("  이벤트 설명: " + stageContent.eventDefinition.desc); // 'description' -> 'desc'로 수정
                        // TODO: 실제 이벤트 처리 로직 구현 (예: 플레이어 HP 회복, 카드 획득 등)
                        System.out.println("  (현재 이벤트 기능은 구현되지 않아, 다음 층으로 바로 넘어갑니다.)\n");
                    } else {
                        System.out.println("  이벤트 내용이 없습니다. 다음 층으로 넘어갑니다.\n");
                    }
                }

                // 다음 층으로 이동
                currentFloor++;
                // currentPathIndex = 0; // 더 이상 사용하지 않음
            } // End of outerGameLoop
        } // Scanner가 try-with-resources에 의해 자동으로 닫힙니다.

        System.out.println("게임을 종료합니다.");
    }

    // --- 기존의 헬퍼 메소드들은 변경 없이 유지합니다 ---

    private static void printBoard(Board4x4 board, int playerScale, int enemyScale) {
        StringBuilder enemyRow = new StringBuilder();
        StringBuilder playerRow = new StringBuilder();

        for (int i = 0; i < 4; i++) {
            enemyRow.append(board.isEmpty(Board4x4.Side.ENEMY, i) ? '0' : '1');
        }
        for (int i = 0; i < 4; i++) {
            playerRow.append(board.isEmpty(Board4x4.Side.PLAYER, i) ? '0' : '1');
        }

        System.out.println("적   : " + enemyRow + "   (HP:" + enemyScale + ")");
        System.out.println("플레이어: " + playerRow + "   (HP:" + playerScale + ")");
        System.out.println();
    }

    private static void printPlayerHand(PlayerCardBag bag) {
        System.out.println("[손패 목록]");
        List<CardInstance> list = bag.asReadOnlyList();
        if (list.isEmpty()) {
            System.out.println("(손패가 비어 있습니다)");
        } else {
            for (int i = 0; i < list.size(); i++) {
                CardInstance ci = list.get(i);
                int displayNo = i + 1; // 1-based 표시
                System.out.println(displayNo + ") " + ci.getDef().name +
                        " (ATK:" + ci.getCurrentAtk() +
                        " HP:" + ci.getCurrentHp() +
                        " DEF:" + ci.getCurrentDef() + ")");
            }
        }
        System.out.println();
    }

    /**
     * 적이 가진 카드 중 1장을 골라, 비어 있는 적 보드 칸에 랜덤 배치합니다.
     */
    private static void enemyPlayRandom(Board4x4 board, EnemyCardBag enemyBag, Random rng) {
        if (enemyBag.size() == 0) {
            System.out.println("적이 낼 카드가 없습니다."); // 추가: 적 카드가 없을 때 메시지
            return;
        }

        List<Integer> emptySlots = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            if (board.isEmpty(Board4x4.Side.ENEMY, i)) {
                emptySlots.add(i);
            }
        }
        if (emptySlots.isEmpty()) {
            System.out.println("적 보드에 빈 칸이 없습니다."); // 추가: 적 보드에 빈 칸이 없을 때 메시지
            return;
        }

        int slotIndex = emptySlots.get(rng.nextInt(emptySlots.size()));
        int enemyIndex = rng.nextInt(enemyBag.size());
        CardInstance enemyCard = enemyBag.remove(enemyIndex); // 적 손패에서 카드를 제거하고 가져옵니다.
        if (enemyCard != null) { // null 체크 추가
            board.place(Board4x4.Side.ENEMY, slotIndex, enemyCard);
            System.out.println("적이 " + (slotIndex + 1) + "번 칸에 '" + enemyCard.getDef().name + "' 카드를 배치했습니다.");
        }
    }

    /**
     * 한 번의 전투 스텝을 진행합니다.
     * 결과 배열 [0] = 플레이어가 받은 총 대미지, [1] = 적이 받은 총 대미지
     */
    private static int[] resolveBattleStep(Board4x4 board) {
        int damageToPlayerScale = 0;
        int damageToEnemyScale = 0;

        System.out.println("--- 전투 스텝 결과 ---");
        for (int i = 0; i < 4; i++) {
            CardInstance player = board.get(Board4x4.Side.PLAYER, i);
            CardInstance enemy = board.get(Board4x4.Side.ENEMY, i);

            if (player != null && enemy != null) {
                // 서로의 카드에게 공격
                int dmgToEnemyCard = calculateDamage(player.getCurrentAtk(), enemy.getCurrentDef());
                enemy.setCurrentHp(enemy.getCurrentHp() - dmgToEnemyCard);
                System.out.printf("  [플레이어] %s (ATK:%d) 가 [적] %s (DEF:%d) 에게 %d 피해\n",
                        player.getDef().name, player.getCurrentAtk(), enemy.getDef().name, enemy.getCurrentDef(), dmgToEnemyCard);

                int dmgToPlayerCard = calculateDamage(enemy.getCurrentAtk(), player.getCurrentDef());
                player.setCurrentHp(player.getCurrentHp() - dmgToPlayerCard);
                System.out.printf("  [적] %s (ATK:%d) 가 [플레이어] %s (DEF:%d) 에게 %d 피해\n",
                        enemy.getDef().name, enemy.getCurrentAtk(), player.getDef().name, player.getCurrentDef(), dmgToPlayerCard);


                if (enemy.getCurrentHp() <= 0) {
                    System.out.println("  [적 카드] '" + enemy.getDef().name + "'가 파괴되었습니다.");
                    board.remove(Board4x4.Side.ENEMY, i);
                }
                if (player.getCurrentHp() <= 0) {
                    System.out.println("  [플레이어 카드] '" + player.getDef().name + "'가 파괴되었습니다.");
                    board.remove(Board4x4.Side.PLAYER, i);
                }
            } else if (player != null) {
                // 적 보드 칸이 비어 있으면, 플레이어 카드가 적 저울 HP에 직접 피해를 줍니다.
                int dmg = player.getCurrentAtk();
                damageToEnemyScale += dmg;
                System.out.printf("  [플레이어] %s (ATK:%d) 가 적 저울에 직접 %d 피해\n", player.getDef().name, player.getCurrentAtk(), dmg);
            } else if (enemy != null) {
                // 플레이어 보드 칸이 비어 있으면, 적 카드가 플레이어 저울 HP에 직접 피해를 줍니다.
                int dmg = enemy.getCurrentAtk();
                damageToPlayerScale += dmg;
                System.out.printf("  [적] %s (ATK:%d) 가 플레이어 저울에 직접 %d 피해\n", enemy.getDef().name, enemy.getCurrentAtk(), dmg);
            }
        }

        return new int[]{damageToPlayerScale, damageToEnemyScale};
    }

    private static int calculateDamage(int atk, int def) {
        return Math.max(1, atk - def); // 최소 1 대미지 보장
    }
}