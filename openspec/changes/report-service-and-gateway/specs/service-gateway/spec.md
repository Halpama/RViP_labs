# Spec Delta

## Purpose

Предоставляет единую внешнюю точку входа для reader-service и report-service,
сохраняя внутренние адреса сервисов недоступными с хоста и поддерживая их
документированные API-контракты.

## ADDED Requirements

### Requirement: Gateway routes reader service requests
Gateway MUST proxy requests under `/reader-service/` to reader-service while removing the gateway prefix before forwarding.

#### Scenario: Access reader API through gateway
- **WHEN** a client requests `/reader-service/readers`
- **THEN** gateway forwards the request to reader-service `/readers` and returns its response

### Requirement: Gateway routes report service requests
Gateway MUST proxy requests under `/report-service/` to report-service while removing the gateway prefix before forwarding.

#### Scenario: Access report API through gateway
- **WHEN** a client requests `/report-service/reports/readers`
- **THEN** gateway forwards the request to report-service `/reports/readers` and returns its response

### Requirement: Gateway preserves service documentation paths
Gateway MUST make each service's Swagger UI and OpenAPI document available through its prefixed route.

#### Scenario: Open reader service Swagger through gateway
- **WHEN** a client requests `/reader-service/docs` and `/reader-service/openapi.json`
- **THEN** both requests return the reader-service documentation with gateway-prefixed URLs that remain usable

#### Scenario: Open report service Swagger through gateway
- **WHEN** a client requests `/report-service/docs` and `/report-service/openapi.json`
- **THEN** both requests return the report-service documentation with gateway-prefixed URLs that remain usable

### Requirement: Gateway reports unavailable upstreams
Gateway MUST return HTTP 502 or 504 with a human-readable response when a configured upstream service is unavailable or times out.

#### Scenario: Upstream service is unavailable
- **WHEN** a client requests a route whose service cannot be reached
- **THEN** gateway returns HTTP 502 or 504 and the response identifies the upstream failure in an understandable way
