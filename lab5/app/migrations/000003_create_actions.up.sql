 CREATE TABLE IF NOT EXISTS user_actions (
     id SERIAL PRIMARY KEY ,
     user_id INT,
     path VARCHAR(100) NOT NULL,
     created_at TIMESTAMP NOT NULL DEFAULT NOW(),
     CONSTRAINT fk_actions_role_id
        FOREIGN KEY (user_id) REFERENCES users(id)
 );

CREATE INDEX user_id
    ON user_actions(user_id);