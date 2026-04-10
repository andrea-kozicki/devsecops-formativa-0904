# devsecops-formativa-0904
# API Simples com FastAPI, SQLite e Pipeline de Validação

## Descrição

Este projeto apresenta uma API simples desenvolvida em **Python com FastAPI**, conforme os requisitos da atividade proposta.

A aplicação possui:

- **Endpoint de login**
- **Endpoint de healthcheck**
- **Endpoint de métricas**
- **Banco de dados SQLite simples**
- **Testes automatizados com pytest**
- **Pipeline de validação com GitHub Actions**

O objetivo é demonstrar um fluxo básico de desenvolvimento com validação automática, alinhado a uma proposta introdutória de **CI/CD** e **DevSecOps**.

---

## Tecnologias utilizadas

- Python 3.12
- FastAPI
- Uvicorn
- SQLite
- Pytest
- GitHub Actions

---

## Funcionalidades da API

### 1. Login
Endpoint responsável por validar usuário e senha consultando um banco SQLite simples.

**Rota:**
```http
POST /login