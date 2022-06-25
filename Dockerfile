FROM openjdk:17
EXPOSE 8080
ARG JAR_FILE=target/*.jar
ARG IMPORTS_SCHEMA=src/main/resources/schemas/imports.json
COPY ${JAR_FILE} app.jar
COPY ${IMPORTS_SCHEMA} ${IMPORTS_SCHEMA}
ENTRYPOINT ["java", "-jar", "/app.jar"]