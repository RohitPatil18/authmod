# Django Custom Role Based Access Control

Django by default provide group based authorization. There might be some cases where business wants you to implement role based system. To fit you usecase into default implementation may be a little bit tricky.

In this small project, I have demonstrated how you build custom role based by modifying permission mixins and adding customised backend,

## Getting Started

- **Prerequisite**: Make sure to Install python (greater than 3.8)
- Git clone this repository to your local machine.
- Go to cloned directory and create **.env** at root, copy all content from **.env.example** and fill in values for all environment variables
- Create a virtual env with name **".venv"** Refer, [Virtualenv Guide](https://www.geeksforgeeks.org/python-virtual-environment/)
- Change your working directory to **backend** with following command:

  `cd src`

- Install required packages from "requirements.txt" with following command:

  `pip install -r requirements/base.txt`

- Once done, Perform migrations with command:
  `python manage.py migrate`
- Then you can run your project with following command:
  `python manage.py runserver`
