# imports
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Identity
from sqlalchemy.orm import mapper, sessionmaker

from Person import Person

# mysql database (or sqllite)
url: str = '/Users/display/Library/DBeaverData/workspace6/.metadata/sample-database-sqlite-1/Chinook.db'
engine = create_engine(f'sqlite:///{url}', echo=False)
# engine = create_engine("mysql+mysqlconnector://root@localhost/dbpersonnes")

# metadata
metadata = MetaData()

# table
persons_table = Table("persons", metadata,
                        Column('id', Integer, Identity(start=1, cycle=True), primary_key=True),
                        # Column('id', Integer, primary_key=True),
                        Column('firstName', String(30), nullable=False),
                        Column("lastName", String(30), nullable=False),
                        Column("age", Integer, nullable=False),
                        sqlite_autoincrement=True
                        )

# mapping
mapper(Person, persons_table, properties={
    'id': persons_table.c.id,
    'firstname': persons_table.c.firstName,
    'name': persons_table.c.lastName,
    'age': persons_table.c.age,
})

# session factory
Session = sessionmaker()
Session.configure(bind=engine)

# session
session = Session()

# insert
session.add(Person("x", "y", 10))
session.commit()

# query
personnes = session.query(Person).all()

# logs
for personne in personnes:
    print(personne)