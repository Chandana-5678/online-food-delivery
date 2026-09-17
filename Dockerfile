FROM python:3.12-alpine
ARG APP_COMMIT
ENV APP_COMMIT=$APP_COMMIT PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
LABEL org.opencontainers.image.title="Jenkins sample app" org.opencontainers.image.revision=$APP_COMMIT
WORKDIR /app
COPY app.py version.txt /app/
RUN chmod 0444 /app/app.py /app/version.txt
USER 10001:10001
EXPOSE 8081
CMD ["python", "/app/app.py"]
