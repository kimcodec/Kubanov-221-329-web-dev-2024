CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_name     VARCHAR(64) NOT NULL,
    first_name    VARCHAR(64) NOT NULL,
    middle_name   VARCHAR(64),
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    role_id       INT,
    CONSTRAINT fk_users_role_id
        FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE INDEX role_id
    ON users(role_id);
