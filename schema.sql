-- Tasks: named tasks assigned to specific year levels
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    year_level  INTEGER NOT NULL CHECK (year_level BETWEEN 4 AND 12),
    description TEXT,
    UNIQUE (name, year_level)
);

-- Rubric criteria belonging to a task
CREATE TABLE IF NOT EXISTS rubric_criteria (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    description TEXT,
    sort_order  INTEGER NOT NULL DEFAULT 0
);

-- Comments keyed to a rubric criterion and an achievement level (A–E)
CREATE TABLE IF NOT EXISTS comments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    criteria_id      INTEGER NOT NULL REFERENCES rubric_criteria(id) ON DELETE CASCADE,
    achievement_level TEXT   NOT NULL CHECK (achievement_level IN ('A','B','C','D','E')),
    comment_text     TEXT    NOT NULL,
    UNIQUE (criteria_id, achievement_level)
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_criteria_task   ON rubric_criteria(task_id);
CREATE INDEX IF NOT EXISTS idx_comments_crit   ON comments(criteria_id);
