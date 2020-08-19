CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year VARCHAR NOT NULL
);

CREATE TABLE readers (
    id SERIAL PRIMARY KEY,
    cust_name VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    books_id INTEGER REFERENCES books
);
