CREATE TABLE Material (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_name TEXT NOT NULL,
    density REAL NOT NULL,        -- New: density of the material
    unit TEXT NOT NULL            -- New: unit for density
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE SupplementaryMaterial (
    supplement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplement_name TEXT NOT NULL
);
CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    user_role TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Track when user was added
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP   -- Track updates to the user
);
CREATE TABLE Process (
    process_id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_name TEXT,                              -- Human-readable process name
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Track when process starts
    end_time DATETIME,                              -- Track when process ends
    material_id INTEGER,                            -- Link to Material
    supplement_id INTEGER,                          -- Link to Supplementary Material
    user_id INTEGER,                                -- Link to User who started the process
    FOREIGN KEY (material_id) REFERENCES Material(material_id),
    FOREIGN KEY (supplement_id) REFERENCES SupplementaryMaterial(supplement_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);
CREATE INDEX idx_process_start_time ON Process(start_time);
CREATE INDEX idx_process_end_time ON Process(end_time);
CREATE INDEX idx_process_material_id ON Process(material_id);
CREATE INDEX idx_process_supplement_id ON Process(supplement_id);
CREATE INDEX idx_user_username ON User(username);
CREATE UNIQUE INDEX idx_user_username_unique ON User(username);
CREATE TABLE ProcessData (
    data_id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER,
    frequency REAL,
    frequency_change REAL,
    frequency_rate_of_change REAL,
    unit TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_id) REFERENCES Process(process_id) ON DELETE CASCADE
);