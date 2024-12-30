CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    user_role TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Track when user was added
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP   -- Track updates to the user
);
CREATE INDEX idx_user_username ON User(username);
CREATE UNIQUE INDEX idx_user_username_unique ON User(username);
CREATE TABLE IF NOT EXISTS "Material" (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_name TEXT NOT NULL,
    density REAL NOT NULL -- Density in g/cm3
);
CREATE TABLE ProcessData (data_id INTEGER PRIMARY KEY AUTOINCREMENT, process_id INTEGER, frequency REAL, frequency_change REAL, thickness REAL, material_name TEXT REFERENCES Material (material_name), created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (process_id) REFERENCES Process (process_id) ON DELETE CASCADE);
CREATE TABLE SetupConstants (id INTEGER PRIMARY KEY AUTOINCREMENT, quartz_density REAL NOT NULL, quartz_shear_modulus REAL NOT NULL, quartz_area REAL NOT NULL, tooling_factor REAL NOT NULL DEFAULT 1.0, description TEXT DEFAULT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE Process (process_id INTEGER PRIMARY KEY AUTOINCREMENT, process_name TEXT DEFAULT Unnamed_process, start_time DATETIME DEFAULT CURRENT_TIMESTAMP, end_time DATETIME, material_id INTEGER DEFAULT NULL, setup_id INTEGER DEFAULT NULL, user_id INTEGER DEFAULT NULL, FOREIGN KEY (material_id) REFERENCES Material (material_id), FOREIGN KEY (setup_id) REFERENCES SetupConstants (id), FOREIGN KEY (user_id) REFERENCES User (user_id));
