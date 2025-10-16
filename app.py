from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from flask import Flask, jsonify, request

from storage import QuizQuestion, storage

app = Flask(__name__)


RUBRIC_BANDS = {
    "fluencia": (0, 5),
    "vocabulario": (0, 5),
    "compreensao": (0, 5),
    "expressao": (0, 5),
}

EVALUATOR_REVIEW_BANDS = {
    "conhecimento_libras": (0, 5),
    "didatica": (0, 5),
    "feedback": (0, 5),
}

LEVEL_THRESHOLDS = {
    "iniciante": (0, 1.5),
    "basico": (1.5, 2.75),
    "intermediario": (2.75, 3.75),
    "avancado": (3.75, 4.5),
    "fluente": (4.5, 5.0),
}


def _serialize(obj: Any) -> Dict[str, Any]:
    data = asdict(obj)
    for key, value in list(data.items()):
        if hasattr(value, "isoformat"):
            data[key] = value.isoformat()
    return data


def _validate_scores(payload: Dict[str, Any], bands: Dict[str, tuple]) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for category, (low, high) in bands.items():
        if category not in payload:
            raise ValueError(f"Categoria obrigatória ausente: {category}")
        score = payload[category]
        if not isinstance(score, (int, float)):
            raise ValueError(f"Pontuação inválida para {category}")
        if score < low or score > high:
            raise ValueError(f"Pontuação de {category} precisa estar entre {low} e {high}")
        scores[category] = int(score)
    return scores


def _compute_level(scores: Dict[str, int]) -> str:
    average = sum(scores.values()) / len(scores)
    for level, (low, high) in LEVEL_THRESHOLDS.items():
        if low <= average < high or (level == "fluente" and average == high):
            return level
    return "iniciante"


@app.post("/users")
def create_user():
    data = request.get_json(force=True)
    name = data.get("name")
    role = data.get("role")
    if role not in {"student", "professor", "evaluator"}:
        return {"error": "Role inválido"}, 400
    if not name:
        return {"error": "Nome é obrigatório"}, 400
    user = storage.add_user(
        name=name,
        role=role,
        bio=data.get("bio"),
        availability=data.get("availability"),
        approved=data.get("approved", False),
    )
    return jsonify(_serialize(user)), 201


@app.get("/users")
def list_users():
    role = request.args.get("role")
    users = storage.list_users(role=role)
    return jsonify([_serialize(u) for u in users])


@app.patch("/users/<int:user_id>")
def update_user(user_id: int):
    data = request.get_json(force=True)
    user = storage.update_user(user_id, **data)
    if not user:
        return {"error": "Usuário não encontrado"}, 404
    return jsonify(_serialize(user))


@app.post("/sessions")
def create_session():
    data = request.get_json(force=True)
    student_id = data.get("student_id")
    instructor_id = data.get("instructor_id")
    scheduled_for = data.get("scheduled_for")
    if not (student_id and instructor_id and scheduled_for):
        return {"error": "Campos obrigatórios ausentes"}, 400
    session = storage.create_session(
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_for=scheduled_for,
        notes=data.get("notes"),
    )
    return jsonify(_serialize(session)), 201


@app.get("/sessions")
def list_sessions():
    user_id = request.args.get("user_id", type=int)
    sessions = storage.list_sessions(user_id=user_id)
    return jsonify([_serialize(s) for s in sessions])


@app.patch("/sessions/<int:session_id>")
def update_session(session_id: int):
    data = request.get_json(force=True)
    status = data.get("status")
    if status not in {"scheduled", "completed", "cancelled"}:
        return {"error": "Status inválido"}, 400
    session = storage.update_session_status(session_id, status)
    if not session:
        return {"error": "Sessão não encontrada"}, 404
    return jsonify(_serialize(session))


@app.post("/quizzes")
def create_quiz():
    data = request.get_json(force=True)
    title = data.get("title")
    level = data.get("level")
    questions_payload: List[Dict[str, Any]] = data.get("questions", [])
    if not title or not level or not questions_payload:
        return {"error": "Dados obrigatórios ausentes"}, 400
    questions: List[QuizQuestion] = []
    for q in questions_payload:
        try:
            question = QuizQuestion(
                prompt=q["prompt"],
                options=q["options"],
                answer_index=q["answer_index"],
                media_url=q.get("media_url"),
            )
        except KeyError as exc:
            return {"error": f"Campo ausente em questão: {exc}"}, 400
        if question.answer_index < 0 or question.answer_index >= len(question.options):
            return {"error": "answer_index inválido"}, 400
        questions.append(question)
    quiz = storage.create_quiz(
        title=title,
        level=level,
        questions=questions,
        created_by=data.get("created_by"),
    )
    return jsonify(_serialize(quiz)), 201


@app.get("/quizzes")
def list_quizzes():
    level = request.args.get("level")
    quizzes = storage.list_quizzes(level=level)
    return jsonify([_serialize(q) for q in quizzes])


@app.get("/quizzes/<int:quiz_id>")
def get_quiz(quiz_id: int):
    quiz = storage.get_quiz(quiz_id)
    if not quiz:
        return {"error": "Quiz não encontrado"}, 404
    return jsonify(_serialize(quiz))


@app.post("/quiz-submissions")
def submit_quiz():
    data = request.get_json(force=True)
    quiz_id = data.get("quiz_id")
    student_id = data.get("student_id")
    answers = data.get("answers")
    quiz = storage.get_quiz(quiz_id)
    if not quiz:
        return {"error": "Quiz não encontrado"}, 404
    if not isinstance(answers, list) or len(answers) != len(quiz.questions):
        return {"error": "Número de respostas inválido"}, 400
    correct = 0
    for answer, question in zip(answers, quiz.questions):
        if answer == question.answer_index:
            correct += 1
    score = correct / len(quiz.questions)
    submission = storage.add_quiz_submission(quiz_id, student_id, answers, score)
    payload = _serialize(submission)
    payload["score_percent"] = round(score * 100, 2)
    return jsonify(payload), 201


@app.get("/quiz-submissions")
def list_submissions():
    quiz_id = request.args.get("quiz_id", type=int)
    student_id = request.args.get("student_id", type=int)
    submissions = storage.list_quiz_submissions(quiz_id=quiz_id, student_id=student_id)
    return jsonify([_serialize(s) for s in submissions])


@app.post("/assessments")
def create_assessment():
    data = request.get_json(force=True)
    try:
        scores = _validate_scores(data.get("rubric", {}), RUBRIC_BANDS)
    except ValueError as exc:
        return {"error": str(exc)}, 400
    overall_level = _compute_level(scores)
    assessment = storage.add_assessment(
        student_id=data.get("student_id"),
        evaluator_id=data.get("evaluator_id"),
        session_id=data.get("session_id"),
        rubric_scores=scores,
        comments=data.get("comments"),
        overall_level=overall_level,
    )
    payload = _serialize(assessment)
    payload["rubric_scores"] = scores
    payload["average_score"] = round(sum(scores.values()) / len(scores), 2)
    return jsonify(payload), 201


@app.get("/assessments")
def list_assessments():
    student_id = request.args.get("student_id", type=int)
    evaluator_id = request.args.get("evaluator_id", type=int)
    assessments = storage.list_assessments(student_id=student_id, evaluator_id=evaluator_id)
    return jsonify([_serialize(a) for a in assessments])


@app.post("/evaluator-reviews")
def review_evaluator():
    data = request.get_json(force=True)
    try:
        scores = _validate_scores(data.get("scores", {}), EVALUATOR_REVIEW_BANDS)
    except ValueError as exc:
        return {"error": str(exc)}, 400
    review = storage.add_evaluator_review(
        evaluator_id=data.get("evaluator_id"),
        reviewer_id=data.get("reviewer_id"),
        scores=scores,
        comments=data.get("comments"),
    )
    payload = _serialize(review)
    payload["scores"] = scores
    payload["average_score"] = round(sum(scores.values()) / len(scores), 2)
    return jsonify(payload), 201


@app.get("/evaluator-reviews")
def list_reviews():
    evaluator_id = request.args.get("evaluator_id", type=int)
    reviews = storage.list_evaluator_reviews(evaluator_id=evaluator_id)
    return jsonify([_serialize(r) for r in reviews])


if __name__ == "__main__":
    app.run(debug=True)
