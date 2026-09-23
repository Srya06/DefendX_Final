# Database Architecture

## Overview
DEFEND-X utilizes a hybrid database approach:
1. **PostgreSQL**: For transactional, relational candidate data and application state.
2. **Neo4j**: For the defense knowledge graph, enabling semantic relationships between syllabus, defense requirements, and concepts.

## PostgreSQL Conceptual Entities

### Authentication & Authorization
- `users`: Core identity (stores username/user_id, Argon2id password hash).
- `roles`: RBAC roles (CANDIDATE, ADMIN).
- `sessions`: Session tracking tokens.
- `credentials`: Specialized authentication history.

### Candidate Domain
- `profiles`: Personal details (logically separated from `users`).
- `candidate_metrics`: Aggregated stats over time.
- `dri_scores`: Defense Readiness Index historical tracking.

### Recruitment & Academics
- `forces`: Target forces/branches.
- `exams`: Entrance exams.
- `subjects`: Syllabus breakdown.
- `mock_tests` / `mock_attempts`: Testing history.
- `questions`: Question bank.

### Fitness & Resources
- `fitness_sessions`: Records of CV-assessed workouts.
- `resources`: Study material.
- `recommendations`: AI-generated guidance.
- `notifications`: System alerts.
- `audit_logs`: Critical action tracking.

## Neo4j Concepts
The graph database models semantic connections, for example:
`(Concept) -[:PREREQUISITE_FOR]-> (Concept)`
`(Force) -[:REQUIRES_COMPETENCY]-> (Skill)`
