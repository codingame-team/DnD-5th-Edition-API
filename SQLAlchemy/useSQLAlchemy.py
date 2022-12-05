#!/usr/bin/python3

from sqlalchemy import Column, Integer, Text, Identity
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class used by my classes (my entities)
Base = declarative_base()  # Required


# Definition of the Contact class
class Contact(Base):
    __tablename__ = 'T_Contacts'

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    firstName = Column(Text)
    lastName = Column(Text)

    def __init__(self, fn="John", ln="Doe"):
        self.firstName = fn
        self.lastName = ln

    def __str__(self):
        return self.firstName + " " + self.lastName


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

    doe = Contact()
    session.add(doe)

    james = Contact("James", "Bond")
    session.add(james)

    jason = Contact("Jason", "Bourne")
    session.add(jason)

    # session.add_all( [ doe, james, jason ] )
    session.commit()

    print("--- First select by primary key ---")
    contact = session.query(Contact).get(3)
    print(contact)

    print("--- Second select by firstName ---")
    searchedContacts = session.query(Contact).filter(Contact.firstName.startswith("Ja"))
    for c in searchedContacts: print(c)

    print("--- Third select all contacts ---")
    agenda = session.query(Contact)  # .filter_by( firstName='James' )
    for c in agenda: print(c)

    print("--- Try to update a specific contact ---")
    contact = session.query(Contact).get(1)
    contact.lastName += "!"
    session.commit()  # Mandatory

    print("--- Try to delete a specific contact ---")
    session.delete(contact)
    session.commit()
