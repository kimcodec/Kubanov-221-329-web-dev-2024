DELETE FROM users WHERE login = 'admin' OR login = 'user';
DELETE FROM roles WHERE name = 'admin' OR name = 'user';