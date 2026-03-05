package com.example.server;

import org.glassfish.tyrus.server.Server;

public class ServerStarter {

    public static void main(String[] args) {
        // 1. Render는 포트를 환경변수로 줍니다. 없으면 8080.
        String host = "0.0.0.0";
        int port = 8080;
        
        String envPort = System.getenv("PORT");
        if (envPort != null) {
            port = Integer.parseInt(envPort);
        }

        // 2. 서버 설정
        // rootPath를 "/ws" 대신 "/" 로 잡아야 클라이언트에서 접속이 편함
        // 접속 주소: ws://주소/game
        Server server = new Server(host, port, "/", null, GameWebSocketServer.class);

        try {
            server.start();
            System.out.println("✨ [GameServer] Tyrus 엔진 가동 완료! (Port: " + port + ") ✨");
            System.out.println("🚀 클라우드 서버가 죽지 않고 계속 실행됩니다...");

            // 🔥 [중요 수정] 키보드 입력을 기다리는 게 아니라,
            // 현재 쓰레드를 영원히 대기시켜서 서버가 안 꺼지게 만듦.
            Thread.currentThread().join();

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            server.stop();
            System.out.println("🛑 [GameServer] 서버가 종료되었습니다.");
        }
    }
}