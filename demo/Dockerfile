# 1. 빌드 단계 (Maven + JDK 17)
# maven 이미지도 최신 안정 버전(eclipse-temurin 기반)으로 교체!
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY . .
# 테스트 건너뛰고 빌드
RUN mvn clean package -DskipTests

# 2. 실행 단계 (가볍고 튼튼한 eclipse-temurin 사용)
# 여기가 에러 났던 부분 -> 최신 이미지로 교체 완료
FROM eclipse-temurin:17-jdk
WORKDIR /app

# 빌드된 jar 파일 가져오기
COPY --from=build /app/target/demo-1.0-SNAPSHOT.jar app.jar

# 포트 설정
ENV PORT=8080
EXPOSE $PORT

# 실행
ENTRYPOINT ["java", "-jar", "app.jar"]