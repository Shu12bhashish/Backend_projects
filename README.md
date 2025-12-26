## Lyftr Backend Assignment

### Run
make up

### Endpoints
/webhook  
/messages  
/stats  
/health/live  
/health/ready  
/metrics  

### Design
- Idempotency via SQLite primary key
- HMAC-SHA256 webhook validation
- Structured JSON logging
- Prometheus metrics

### Setup Used
VSCode + ChatGPT
