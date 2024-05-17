INSERT INTO roles(name, description) VALUES('admin', 'coolguy');
INSERT INTO roles(name, description) VALUES('user', 'looser');

INSERT INTO users(login, password_hash, last_name, first_name, role_id)
VALUES('admin', CAST(SHA256('admin') AS VARCHAR), 'adminov', 'admin', 1);
INSERT INTO users(login, password_hash, last_name, first_name, role_id)
VALUES('user', CAST(SHA256('user') AS VARCHAR), 'user', 'user', 2);