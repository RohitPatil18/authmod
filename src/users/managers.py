from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, **kwargs):
        """
        Creates and saves a User with the given email and password.
        """

        email_address = kwargs.pop("email_address", None)
        if not email_address:
            raise ValueError("Users must have an email address")

        password = kwargs.pop("password", None)
        if not email_address:
            raise ValueError("Users must have a password")

        user = self.model(email_address=self.normalize_email(email_address), **kwargs)

        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email_address, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """

        user = self.create_user(
            email_address=email_address,
            password=password,
            is_superuser=True,
        )
        return user

    def create(self, **kwargs):
        return self.create_user(**kwargs)

    def get_by_email_address(self, email_address):
        return self.get(email_address=self.normalize_email(email_address))
