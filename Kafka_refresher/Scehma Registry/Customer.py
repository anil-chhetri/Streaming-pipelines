from  faker import Faker
import uuid
import random

class Customer:
    def __init__(self, name, email):
        self.id = uuid.uuid1()
        self.name = name
        self.email = email

    def __repr__(self):
        return f'Name: {self.name} -> Id: {self.id}'

    def __str__(self):
        return self.__repr__()
    
    def as_dict(self):
        return {
            "id": str(self.id.int),
            "name": self.name,
            "email": self.email
        }

    @classmethod
    def get_customer(cls):
        fake = Faker()
        name = fake.name()
        email = '.'.join(name.lower().split(' ')[::-1][:2]) + str(random.randint(0,1000)) + '@example.com'
        return cls(name, email)


        