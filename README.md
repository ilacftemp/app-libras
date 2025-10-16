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

## Deploy 100% gratuito na Render

A Render oferece um plano gratuito permanente para aplicações web que é suficiente
para colocar esta API no ar. Após criar uma conta gratuita, basta seguir os passos abaixo:

1. Faça o fork deste repositório para a sua conta do GitHub.
2. Acesse o [dashboard da Render](https://dashboard.render.com/) e clique em **New ➜ Web Service**.
3. Conecte a sua conta do GitHub e selecione o fork do projeto.
4. Na configuração inicial escolha:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Region**: escolha a mais próxima dos seus usuários.
   - **Instance Type**: `Free`.
5. Confirme a criação. A Render vai instalar as dependências, gerar a imagem e iniciar o serviço.

O arquivo `render.yaml` presente no repositório permite automatizar o provisionamento
pela opção **New ➜ Blueprint** na Render. Ao usar essa modalidade, a plataforma lê
o arquivo e cria o serviço com os comandos de build e execução corretos.

Assim que o deploy finalizar, a Render exibirá a URL pública do serviço, permitindo
que você visualize e consuma a API imediatamente sem custos.

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
