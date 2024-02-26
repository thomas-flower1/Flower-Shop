DROP TABLE IF EXISTS users;

CREATE TABLE users 
(
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS flowers;

CREATE TABLE flowers
(
    flower_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flower_name TEXT NOT NULL,
    price REAL NOT NULL,
    img_url TEXT
);

INSERT INTO flowers (flower_name, price)
VALUES 
    ('Sunflower', 10.99),
    ('Poppy', 1000000.01),
    ('Rose', 1.99)