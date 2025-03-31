from  faker import Faker
import uuid
import random

class Customer:
    def __init__(self, name, email, phone, status):
        self.id = uuid.uuid1()
        self.name = name
        self.email = email
        self.phone = phone
        self.status = status

    def __repr__(self):
        return f'Name: {self.name} -> Id: {self.id}'

    def __str__(self):
        return self.__repr__()
    
    def as_dict(self):
        return {
            "id": str(self.id.int),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status
        }

    @classmethod
    def get_customer(cls):
        customer_status = ["ACTIVE", "INACTIVE", "SUSPENDED"]
        fake = Faker()
        name = fake.name()
        email = '.'.join(name.lower().split(' ')[::-1][:2]) + str(random.randint(0,1000)) + '@example.com'
        phone = fake.phone_number()
        status = random.choice(customer_status)
        return cls(name, email, phone, status)


        