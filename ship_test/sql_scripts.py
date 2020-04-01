CREATE_SHIP_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS ships (
        ship text PRIMARY KEY,
        weapon text NOT NULL,
        hull text NOT NULL,
        engine text NOT NULL,
        FOREIGN KEY (weapon) REFERENCES weapons (weapon),
        FOREIGN KEY (hull) REFERENCES hulls (hull),
        FOREIGN KEY (engine) REFERENCES engines (engine)
    );
    """

CREATE_WEAPON_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS weapons (
        weapon text PRIMARY KEY,
        reload_speed integer NOT NULL,
        rotational_speed integer NOT NULL,
        diameter integer NOT NULL,
        power_volley integer NOT NULL,
        count integer NOT NULL
    );
    """

CREATE_HULL_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS hulls (
        hull text PRIMARY KEY,
        armor integer NOT NULL,
        type integer NOT NULL,
        capacity integer NOT NULL
    );
    """

CREATE_ENGINE_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS engines (
        engine text PRIMARY KEY,
        power integer NOT NULL,
        type integer NOT NULL
    );
    """

INSERT_INTO_TABLE = "INSERT INTO {table} ({columns}) VALUES ({values});"

SELECT_FROM = "SELECT * from {table};"

UPDATE_ENTITY = "UPDATE {table} SET {values} WHERE {where};"
