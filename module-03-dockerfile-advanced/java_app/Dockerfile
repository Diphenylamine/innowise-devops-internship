## Multi-stage Java

# Этап 1 — сборка (тяжёлый JDK)
FROM eclipse-temurin:17 AS builder
WORKDIR /app
COPY Main.java .
RUN javac Main.java

# Этап 2 — запуск (лёгкий JRE)
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/Main.class .
CMD ["java", "Main"]
