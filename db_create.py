import sqlite3
from _config import DATABASE_PATH

with sqlite3.connect(DATABASE_PATH) as connection:
    c = connection.cursor()
    
    c.execute("""CREATE TABLE users(user_id STRING PRIMARY KEY,
        name TEXT NOT NULL)""")
    
    c.execute(
       'INSERT INTO users (user_id, name) VALUES("admin", "admin")' 
    )
    
    c.execute("""create table exercises(
                    id integer primary key autoincrement,
                    user_id text not null,
                    duration float not null,
                    date integer not null,
                    description text not null,
                    foreign key(user_id) references users(user_id)
                 )
              """
    )
    c.execute(
       'insert into exercises(user_id, duration, date, description) values("admin", 1, 0, "wrote some sql")'
    )