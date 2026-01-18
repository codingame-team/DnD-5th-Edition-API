class Utils:
    pass


class MyException:
    pass


class Person:
    def __init__(self, firstname: str = "x", name: str = "y", age: int = 0):
        self.firstname = firstname
        self.name = name
        self.age = age

    def __str__(self) -> str:
        return f"[{self.__firstname},{self.__name},{self.__age}]"

    @property
    def id(self):
       return self.__id

    @property
    def firstname(self) -> str:
        return self.__firstname

    @property
    def name(self) -> str:
        return self.__name

    @property
    def age(self) -> int:
        return self.__age

    # setters

    @id.setter
    def id(self, id: int):
        if not isinstance(id,int) or id<=0:
            raise MyException(f"...")

    @firstname.setter
    def firstname(self, firstname: str):
        if Utils.is_string_ok(firstname):
            self.__firstname = firstname.strip()
        else:
            raise MyException("...")

    @name.setter
    def name(self, name: str):
        if Utils.is_string_ok(name):
            self.__name = name.strip()
        else:
            raise MyException("...")

    @age.setter
    def age(self, age: int):
        error = False
        if isinstance(age, int):
            if age >= 0:
                self.__age = age
            else:
                error = True
        else:
            error = True
        if error:
            raise MyException("...")