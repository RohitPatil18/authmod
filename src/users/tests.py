from faker import Faker

from users.models import User

faker = Faker()


def create_test_user(**kwargs):
    data = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email_address": faker.free_email(),
        "password": faker.password(),
        **kwargs,
    }
    return User.objects.create(**data)
