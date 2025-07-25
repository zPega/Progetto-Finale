-- Questo script viene eseguito la prima volta che il container del database viene creato.

-- Crea la tabella 'directors' per memorizzare le informazioni sui registi.
CREATE TABLE directors
(
  id INT
  AUTO_INCREMENT PRIMARY KEY, -- Chiave primaria con auto-incremento
    name VARCHAR
  (255) NOT NULL,        -- Nome del regista, non può essere nullo
    birth_year INT                      -- Anno di nascita (opzionale)
);

  -- Crea la tabella 'movies' per i film.
  CREATE TABLE movies
  (
    id INT
    AUTO_INCREMENT PRIMARY KEY,
    titolo VARCHAR
    (255) NOT NULL,
    anno INT,
    genere VARCHAR
    (100),
    director_id INT, -- Chiave esterna che si collega alla tabella 'directors'
    FOREIGN KEY
    (director_id) REFERENCES directors
    (id) -- Vincolo di integrità referenziale
);

    -- Crea la tabella 'platforms' per le piattaforme di streaming.
    CREATE TABLE platforms
    (
      id INT
      AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR
      (255) NOT NULL UNIQUE -- Il nome della piattaforma deve essere unico
);

      -- Crea una tabella 'ponte' (o 'di giunzione') per gestire la relazione molti-a-molti
      -- tra film e piattaforme (un film può essere su più piattaforme, e una piattaforma ha più film).
      CREATE TABLE movie_platforms
      (
        movie_id INT,
        platform_id INT,
        PRIMARY KEY (movie_id, platform_id),
        -- La chiave primaria è la coppia (film, piattaforma)
        FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
        -- Se un film viene cancellato, anche le sue associazioni vengono cancellate
        FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE
      );

      -- INSERIMENTO DATI DI ESEMPIO --

      -- Inserisce alcuni registi
      INSERT INTO directors
        (name, birth_year)
      VALUES
        ('Christopher Nolan', 1970),
        ('Quentin Tarantino', 1963),
        ('Martin Scorsese', 1942);

      -- Inserisce alcuni film, collegandoli ai registi tramite director_id
      INSERT INTO movies
        (titolo, anno, genere, director_id)
      VALUES
        ('Inception', 2010, 'Sci-Fi', 1),
        ('The Dark Knight', 2008, 'Action', 1),
        ('Pulp Fiction', 1994, 'Crime', 2),
        ('The Irishman', 2019, 'Crime', 3);

      -- Inserisce alcune piattaforme
      INSERT INTO platforms
        (name)
      VALUES
        ('Netflix'),
        ('Amazon Prime Video'),
        ('Disney+');

      -- Associa i film alle piattaforme
      INSERT INTO movie_platforms
        (movie_id, platform_id)
      VALUES
        (1, 1),
        -- Inception su Netflix
        (1, 2),
        -- Inception anche su Amazon Prime Video
        (2, 1),
        -- The Dark Knight su Netflix
        (3, 2),
        -- Pulp Fiction su Amazon Prime Video
        (4, 1); -- The Irishman su Netflix