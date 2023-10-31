-- Bảng User (người dùng)
CREATE TABLE Users (
    id INT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);
-- Bảng Artist (nghệ sĩ)
CREATE TABLE Artist (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL ,
    image VARCHAR(255) NOT NULL,
)
CREATE TABLE hat (
    song_id int,
    FOREIGN KEY (song_id) REFERENCES songs (id),
    arist_id int,
    FOREIGN KEY (artist_id) REFERENCES artists (id)
)
-- Bảng Song (bài hát)
CREATE TABLE Song (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_id INT REFERENCES Artist(id),
    genre_id VARCHAR (255) REFERENCES genre(id),
    region_id VARCHAR (255) REFERENCES region(id),
    link VARCHAR(255) NOT NULL
);

CREATE TABLE genre (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE region (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);


CREATE TABLE DSYT (
    user_id INT REFERENCES users(id),
    song_id INT REFERENCES Song(id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (song_id) REFERENCES Song(id)
);

