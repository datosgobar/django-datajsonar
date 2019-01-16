import os
from setuptools import setup, find_packages

with open(os.path.join("requirements", "base.txt")) as f:
    requirements = [req.strip() for req in f.readlines()]

with open(os.path.join("requirements", "testing.txt")) as f:
    test_requirements = [req.strip() for req in f.readlines()]


setup(
    name='django_datajsonar',
    version='0.1.13',
    description="Paquete de django con herramientas para administrar modelos de catalogos.",
    author="Datos Argentina",
    author_email='datos@modernizacion.gob.ar',
    url='https://github.com/datosgobar/django-datajsonar',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='django_datajsonar',
    tests_require=test_requirements
)
