from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class User:
    id: int
    name: str
    role: str  # "student", "professor", "evaluator"
    bio: Optional[str] = None
    availability: List[str] = field(default_factory=list)
    approved: bool = False  # for evaluators


@dataclass
class Session:
    id: int
    student_id: int
    instructor_id: int
    scheduled_for: str
    status: str = "scheduled"
    notes: Optional[str] = None


@dataclass
class QuizQuestion:
    prompt: str
    options: List[str]
    answer_index: int
    media_url: Optional[str] = None


@dataclass
class Quiz:
    id: int
    title: str
    level: str
    questions: List[QuizQuestion]
    created_by: int  # evaluator id


@dataclass
class QuizSubmission:
    id: int
    quiz_id: int
    student_id: int
    answers: List[int]
    score: float
    submitted_at: datetime


@dataclass
class SkillAssessment:
    id: int
    student_id: int
    evaluator_id: int
    session_id: Optional[int]
    rubric_scores: Dict[str, int]
    comments: Optional[str]
    overall_level: str
    assessed_at: datetime


@dataclass
class EvaluatorReview:
    id: int
    evaluator_id: int
    reviewer_id: int
    scores: Dict[str, int]
    comments: Optional[str]
    created_at: datetime


class InMemoryStorage:
    def __init__(self) -> None:
        self._users: Dict[int, User] = {}
        self._sessions: Dict[int, Session] = {}
        self._quizzes: Dict[int, Quiz] = {}
        self._quiz_submissions: Dict[int, QuizSubmission] = {}
        self._assessments: Dict[int, SkillAssessment] = {}
        self._reviews: Dict[int, EvaluatorReview] = {}
        self._ids = {
            "users": 0,
            "sessions": 0,
            "quizzes": 0,
            "quiz_submissions": 0,
            "assessments": 0,
            "reviews": 0,
        }

    def _next_id(self, key: str) -> int:
        self._ids[key] += 1
        return self._ids[key]

    # Users
    def add_user(self, name: str, role: str, bio: Optional[str] = None, availability: Optional[List[str]] = None, approved: bool = False) -> User:
        user = User(
            id=self._next_id("users"),
            name=name,
            role=role,
            bio=bio,
            availability=availability or [],
            approved=approved,
        )
        self._users[user.id] = user
        return user

    def list_users(self, role: Optional[str] = None) -> List[User]:
        if role:
            return [u for u in self._users.values() if u.role == role]
        return list(self._users.values())

    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def update_user(self, user_id: int, **updates) -> Optional[User]:
        user = self._users.get(user_id)
        if not user:
            return None
        for key, value in updates.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        return user

    # Sessions
    def create_session(self, student_id: int, instructor_id: int, scheduled_for: str, notes: Optional[str] = None) -> Session:
        session = Session(
            id=self._next_id("sessions"),
            student_id=student_id,
            instructor_id=instructor_id,
            scheduled_for=scheduled_for,
            notes=notes,
        )
        self._sessions[session.id] = session
        return session

    def list_sessions(self, user_id: Optional[int] = None) -> List[Session]:
        sessions = list(self._sessions.values())
        if user_id is not None:
            sessions = [s for s in sessions if s.student_id == user_id or s.instructor_id == user_id]
        return sessions

    def update_session_status(self, session_id: int, status: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.status = status
        return session

    # Quizzes
    def create_quiz(self, title: str, level: str, questions: List[QuizQuestion], created_by: int) -> Quiz:
        quiz = Quiz(
            id=self._next_id("quizzes"),
            title=title,
            level=level,
            questions=questions,
            created_by=created_by,
        )
        self._quizzes[quiz.id] = quiz
        return quiz

    def list_quizzes(self, level: Optional[str] = None) -> List[Quiz]:
        quizzes = list(self._quizzes.values())
        if level:
            quizzes = [q for q in quizzes if q.level == level]
        return quizzes

    def get_quiz(self, quiz_id: int) -> Optional[Quiz]:
        return self._quizzes.get(quiz_id)

    # Quiz submissions
    def add_quiz_submission(self, quiz_id: int, student_id: int, answers: List[int], score: float) -> QuizSubmission:
        submission = QuizSubmission(
            id=self._next_id("quiz_submissions"),
            quiz_id=quiz_id,
            student_id=student_id,
            answers=answers,
            score=score,
            submitted_at=datetime.utcnow(),
        )
        self._quiz_submissions[submission.id] = submission
        return submission

    def list_quiz_submissions(self, quiz_id: Optional[int] = None, student_id: Optional[int] = None) -> List[QuizSubmission]:
        submissions = list(self._quiz_submissions.values())
        if quiz_id is not None:
            submissions = [s for s in submissions if s.quiz_id == quiz_id]
        if student_id is not None:
            submissions = [s for s in submissions if s.student_id == student_id]
        return submissions

    # Assessments
    def add_assessment(
        self,
        student_id: int,
        evaluator_id: int,
        session_id: Optional[int],
        rubric_scores: Dict[str, int],
        comments: Optional[str],
        overall_level: str,
    ) -> SkillAssessment:
        assessment = SkillAssessment(
            id=self._next_id("assessments"),
            student_id=student_id,
            evaluator_id=evaluator_id,
            session_id=session_id,
            rubric_scores=rubric_scores,
            comments=comments,
            overall_level=overall_level,
            assessed_at=datetime.utcnow(),
        )
        self._assessments[assessment.id] = assessment
        return assessment

    def list_assessments(self, student_id: Optional[int] = None, evaluator_id: Optional[int] = None) -> List[SkillAssessment]:
        assessments = list(self._assessments.values())
        if student_id is not None:
            assessments = [a for a in assessments if a.student_id == student_id]
        if evaluator_id is not None:
            assessments = [a for a in assessments if a.evaluator_id == evaluator_id]
        return assessments

    # Evaluator reviews
    def add_evaluator_review(
        self,
        evaluator_id: int,
        reviewer_id: int,
        scores: Dict[str, int],
        comments: Optional[str],
    ) -> EvaluatorReview:
        review = EvaluatorReview(
            id=self._next_id("reviews"),
            evaluator_id=evaluator_id,
            reviewer_id=reviewer_id,
            scores=scores,
            comments=comments,
            created_at=datetime.utcnow(),
        )
        self._reviews[review.id] = review
        return review

    def list_evaluator_reviews(self, evaluator_id: Optional[int] = None) -> List[EvaluatorReview]:
        reviews = list(self._reviews.values())
        if evaluator_id is not None:
            reviews = [r for r in reviews if r.evaluator_id == evaluator_id]
        return reviews


storage = InMemoryStorage()
