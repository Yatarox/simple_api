CREATE DATABASE IF NOT EXISTS event_management
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE event_management;



CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    picture_url VARCHAR(255),
    visibility ENUM('public', 'private', 'secret') NOT NULL DEFAULT 'public',
    members_can_publish BOOLEAN NOT NULL DEFAULT FALSE,
    members_can_create_events BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('member', 'admin') NOT NULL DEFAULT 'member',
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);




CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    picture_url VARCHAR(255),
    visibility ENUM('public', 'private') NOT NULL DEFAULT 'public',
    group_id INT NULL,                                
    created_by INT NOT NULL,
    shopping_list_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    carpooling_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    ticketing_enabled BOOLEAN NOT NULL DEFAULT FALSE, 
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_time > start_time),
    FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_organizers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    UNIQUE (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    status ENUM('invited', 'attending', 'not_attending') NOT NULL DEFAULT 'invited',
    UNIQUE (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);




CREATE TABLE IF NOT EXISTS threads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NULL UNIQUE,
    event_id INT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- MySQL interdit un CHECK sur des colonnes ayant un ON DELETE CASCADE,
-- donc la règle "groupe XOR événement" est imposée par des triggers.
DELIMITER //

CREATE TRIGGER threads_xor_insert BEFORE INSERT ON threads
FOR EACH ROW
BEGIN
    IF (NEW.group_id IS NULL) = (NEW.event_id IS NULL) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un thread doit être lié à un groupe OU à un événement (pas les deux)';
    END IF;
END//

CREATE TRIGGER threads_xor_update BEFORE UPDATE ON threads
FOR EACH ROW
BEGIN
    IF (NEW.group_id IS NULL) = (NEW.event_id IS NULL) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un thread doit être lié à un groupe OU à un événement (pas les deux)';
    END IF;
END//

DELIMITER ;

-- Un message peut être un commentaire d'un autre message (parent_message_id)
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    thread_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    parent_message_id INT NULL,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_message_id) REFERENCES messages(id) ON DELETE CASCADE
);


-- 2.5 ALBUMS PHOTO

CREATE TABLE IF NOT EXISTS photo_albums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,                 -- 1 album = 1 événement
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    album_id INT NOT NULL,
    user_id INT NOT NULL,                  -- participant qui poste la photo
    url VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (album_id) REFERENCES photo_albums(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS photo_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    photo_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- 2.6 SONDAGES (sondage > questions > réponses possibles, 1 choix par question)

CREATE TABLE IF NOT EXISTS polls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    created_by INT NOT NULL,               -- un organisateur
    title VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS poll_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    poll_id INT NOT NULL,
    question TEXT NOT NULL,
    FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS poll_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text VARCHAR(255) NOT NULL,
    UNIQUE (id, question_id),              -- nécessaire pour la FK composite de poll_answers
    FOREIGN KEY (question_id) REFERENCES poll_questions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS poll_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_id INT NOT NULL,
    user_id INT NOT NULL,
    UNIQUE (question_id, user_id),         -- une seule réponse par question et par participant
    FOREIGN KEY (option_id, question_id) REFERENCES poll_options(id, question_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- 2.7 BILLETTERIE

CREATE TABLE IF NOT EXISTS ticket_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    quantity INT NOT NULL CHECK (quantity >= 0),   -- quantité limitée (stock restant à contrôler côté API)
    UNIQUE (id, event_id),                         -- nécessaire pour la FK composite de tickets
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Acheteur = personne extérieure, donc pas de FK vers users
CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    ticket_type_id INT NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,                   -- identifie la personne pour la règle "1 seul billet"
    address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    purchase_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (event_id, email),                      -- 1 seul billet par personne et par événement
    FOREIGN KEY (ticket_type_id, event_id) REFERENCES ticket_types(id, event_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);


-- 2.8 SHOPPING LIST

CREATE TABLE IF NOT EXISTS shopping_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,                  -- qui l'apporte
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    arrival_time DATETIME NOT NULL,
    UNIQUE (event_id, name),               -- chaque chose apportée est unique par événement
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- 3. COVOITURAGE (bonus)

CREATE TABLE IF NOT EXISTS carpoolings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    driver_id INT NOT NULL,
    departure_location VARCHAR(255) NOT NULL,
    departure_time DATETIME NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    available_seats INT NOT NULL CHECK (available_seats > 0),
    max_detour_minutes INT NOT NULL DEFAULT 0 CHECK (max_detour_minutes >= 0),  -- écart max (ex : 30)
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES users(id) ON DELETE CASCADE
);