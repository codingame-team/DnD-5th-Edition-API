#!/usr/bin/python3
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class used by my classes (my entities)
from tests.dao_classes_sql_alchemy import Monster, Base

# The main part
if __name__ == '__main__':

    url: str = '/Users/display/Library/DBeaverData/workspace6/.metadata/sample-database-sqlite-1/Chinook.db'
    # hostname: str = 'pmourey.mysql.pythonanywhere-services.com'
    # url: str = f'mysql://pmourey:fifa2022@{hostname}/sample'

    engine = create_engine(f'sqlite:///{url}', echo=False)
    # engine = create_engine(f'sqlite:///demo.db', echo=False)
    # engine = create_engine(url, echo=False)
    # engine = create_engine('mysql+mysqldb://<user>:<pwd>@localhost/<yourDB>', echo=False)

    print("--- Construct all tables for the database (here just one table) ---")
    Base.metadata.create_all(engine)  # Only for the first time

    print("--- Create three new contacts and push its into the database ---")
    Session = sessionmaker(bind=engine)
    session = Session()

    doe = Monster(name="Goblin", armor_class=7, hit_points=4, hit_dice='1d4', xp=20, challenge_rating=1)
    session.add(doe)
    session.add(doe)
    session.add(doe)

    # session.add_all( [ doe, james, jason ] )
    session.commit()

    print("--- First select by primary key ---")
    contact = session.query(Monster).get(1)
    print(contact)

    print("--- Second select by name ---")
    searchedContacts = session.query(Monster).filter(Monster.name.startswith("Go"))
    for c in searchedContacts: print(c)

    print("--- Third select all contacts ---")
    monsters: List[Monster] = session.query(Monster)  # .filter_by( name='James' )
    for m in monsters: print(m)

    print("--- Try to update a specific contact ---")
    monster = session.query(Monster).get(2)
    monster.hit_points += 2
    monster.armor_class -= 2
    session.commit()  # Mandatory

    print("--- Try to delete a specific contact ---")
    # session.delete(monster)
    # session.commit()
