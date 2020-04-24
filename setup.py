from setuptools import setup

installs = ['bluepy']


setup(
    name='AithreToHud',
    version='2.0.0',
    python_requires='>=3.5',
    description='Adapter service to collects data from Aithre health monitoring devices.',
    url='https://github.com/JohnMarzulli/AithreToHud',
    author='John Marzulli',
    author_email='john.marzulli@hotmail.com',
    license='GPL V3',
    install_requires=installs)
