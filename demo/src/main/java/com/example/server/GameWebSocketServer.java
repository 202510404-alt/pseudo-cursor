package com.example.server;

// import com.example.game.GameRoom;    // 없음, 주석 처리
// import com.example.game.PlayerInfo;  // 없음, 주석 처리
// import com.example.game.Unit;        // 없음, 주석 처리

import javax.websocket.*;
import javax.websocket.server.ServerEndpoint;
import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

// [서버 문패]
@ServerEndpoint("/game")
public class GameWebSocketServer {

    // 🏨 [게임방 관리소] (GameRoom 없음, 간단한 맵으로 대체)
    private static Map<String, String> rooms = new ConcurrentHashMap<>();

    // 1. 입장
    @OnOpen
    public void onOpen(Session session) {
        String sessionId = session.getId();
        System.out.println("✅ [입장] 새로운 도전자 접속! ID: " + sessionId);

        try {
            // 플레이어 정보 & 게임방 생성 (GameRoom, PlayerInfo, Unit 없음, 간단히 저장)
            // PlayerInfo newPlayer = new PlayerInfo(sessionId, 1);
            // GameRoom newRoom = new GameRoom(sessionId, newPlayer);
            // newRoom.spawnPlayerUnit();
            String newRoom = "Room for " + sessionId; // 간단한 문자열로 대체
            
            // 방 명부에 등록
            rooms.put(sessionId, newRoom);

            // 생성된 유닛 정보 가져오기 (Unit 없음, 간단한 메시지)
            // Unit myUnit = newRoom.PlayerUnits.get(0);
            String unitInfo = "직업: 전사, HP:100, ATK:10, SPD:5"; // 간단한 정보로 대체

            // 클라이언트에게 환영 메시지
            sendMessage(session, "[시스템] 게임방에 입장했습니다.\n" +
                    "⚔️ 당신의 직업: " + unitInfo + "\n" +
                    "👉 전투를 진행하려면 '턴종료' 라고 입력하세요.");

        } catch (Exception e) {
            e.printStackTrace();
            sendMessage(session, "[에러] 입장 처리 중 문제가 발생했습니다.");
        }
    }

    // 2. 메시지 수신
    @OnMessage
    public void onMessage(String message, Session session) {
        String sessionId = session.getId();
        String room = rooms.get(sessionId);

        if (room == null) {
            sendMessage(session, "[에러] 게임방을 찾을 수 없습니다.");
            return;
        }

        System.out.println("📩 [" + sessionId + "] 수신: " + message);

        if (message.equals("턴종료")) {
            System.out.println("⚔️ [" + sessionId + "] 전투 시뮬레이션(Phase B) 시작!");
            
            // 전투 시뮬레이션 실행 (GameRoom 없음, 간단한 로그)
            String battleLog = "전투 결과: 승리! 다음 스테이지로 진행합니다.";
            
            // 결과 전송
            sendMessage(session, battleLog);
            
            // room.CurrentStage++; // 없음
        } 
        else if (message.equals("내정보")) {
            // if (!room.PlayerUnits.isEmpty()) {
            //     Unit u = room.PlayerUnits.get(0);
            //     sendMessage(session, "내 유닛: " + u.Name + " (HP: " + u.CurrentHP + "/" + u.MaxHP + ")");
            // }
            sendMessage(session, "내 유닛: 전사 (HP: 100/100)");
        } 
        else {
            sendMessage(session, "서버: '" + message + "'... (알 수 없는 명령어)");
        }
    }

    // 3. 퇴장
    @OnClose
    public void onClose(Session session) {
        String sessionId = session.getId();
        rooms.remove(sessionId);
        System.out.println("🚪 [퇴장] 유저 연결 해제. ID: " + sessionId);
    }

    // 4. 에러 처리
    @OnError
    public void onError(Session session, Throwable throwable) {
        System.out.println("⚠️ [오류] 통신 중 문제 발생: " + throwable.getMessage());
    }

    // [유틸] 메시지 전송
    private void sendMessage(Session session, String msg) {
        try {
            if (session.isOpen()) {
                session.getBasicRemote().sendText(msg);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}