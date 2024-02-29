DROP TABLE IF EXISTS users;

CREATE TABLE users 
(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    img_url TEXT NOT NULL
);

INSERT INTO flowers (flower_name, price, img_url)
VALUES 
    ('Sunflower', 10.99, 'sunflower.jpg'),
    ('Daffodil', 1.99, 'daffodil.jpg'),
    ('Dandelions', 52.99, 'dandelions.jpg'),
    ('Lilies', 17.99, 'lily.jpg'),
    ('Marigold', 42.99, 'marigold.jpg'),
    ('Lavender', 11.99, 'lavender.jpg'),
    ('Roses', 49.99, 'rose.jpg'),
    ('Carnation', 59.99, 'carnation.jpg'),
    ('Poppy', 10000.99, 'poppy.jpg');



SELECT * 
FROM flowers
WHERE flower_id = 2;


   


INSERT INTO users (username, email, password)
VALUES 
    ('administractor', 'name@email.com', 123456789),
    ('thomas', 'flowersthomas434@gmail.com', 123);


DROP TABLE IF EXISTS basket;

