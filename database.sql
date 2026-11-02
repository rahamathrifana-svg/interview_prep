CREATE TABLE IF NOT EXISTS users (
  uid TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT,
  photo_url TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS progress (
  uid TEXT PRIMARY KEY REFERENCES users(uid) ON DELETE CASCADE,
  xp INTEGER NOT NULL DEFAULT 0 CHECK (xp >= 0),
  challenge_started_at TEXT,
  aptitude_started_at TEXT,
  theme TEXT CHECK (theme IN ('light', 'dark')),
  state_json TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS check_ins (
  uid TEXT NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
  check_in_date TEXT NOT NULL,
  streak_type TEXT NOT NULL DEFAULT 'reasoning' CHECK (streak_type IN ('reasoning', 'aptitude')),
  PRIMARY KEY (uid, check_in_date, streak_type)
);

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
  name TEXT NOT NULL,
  live_url TEXT,
  status TEXT NOT NULL DEFAULT 'Not Started' CHECK (status IN ('Not Started', 'In Progress', 'Completed')),
  notes TEXT,
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (uid, name)
);
