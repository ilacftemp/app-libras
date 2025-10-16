# Plataforma Libras Online

Aplicação Flask que oferece endpoints para gerir aulas particulares de Libras, agendamentos, provas/treinamentos em formato de quiz e avaliações conduzidas por avaliadores certificados.

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

A API ficará disponível em `http://127.0.0.1:5000`.

## Recursos principais

### Usuários
- `POST /users`: cria estudantes, professores ou avaliadores (avaliadores possuem flag `approved`).
- `GET /users`: lista usuários filtrando por `role`.
- `PATCH /users/<id>`: atualiza dados básicos, disponibilidade ou aprovação.

### Aulas particulares
- `POST /sessions`: agenda sessões entre estudantes e instrutores com notas opcionais.
- `GET /sessions`: lista sessões, podendo filtrar por `user_id`.
- `PATCH /sessions/<id>`: atualiza o status (`scheduled`, `completed`, `cancelled`).

### Treinamentos/Quizzes
- `POST /quizzes`: avaliadores criam quizzes com perguntas de múltipla escolha e suporte a mídia.
- `GET /quizzes`: lista quizzes, com filtro opcional por nível.
- `GET /quizzes/<id>`: obtém detalhes de um quiz específico.
- `POST /quiz-submissions`: estudantes enviam respostas e recebem nota percentual.
- `GET /quiz-submissions`: lista submissões filtradas por quiz ou estudante.

### Avaliações de proficiência
- `POST /assessments`: avaliadores atribuem notas padronizadas (fluência, vocabulário, compreensão, expressão). A média determina o nível sugerido.
- `GET /assessments`: consulta avaliações por estudante ou avaliador.

### Auditoria de avaliadores
- `POST /evaluator-reviews`: registra avaliações estruturadas dos avaliadores antes da aprovação.
- `GET /evaluator-reviews`: lista avaliações dos avaliadores.

## Próximos passos sugeridos
- Persistência em banco de dados.
- Fluxo de autenticação/autorização.
- Interface web para estudantes, professores e avaliadores.
- Notificações de agendamento e relatórios de desempenho.
