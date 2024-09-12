from setuptools import setup, find_packages

setup(
    name="mirrormirror",
    version="0.2.3",
    author="John Major",  # Replace with your name
    author_email="iamh2o+mirrormirror@gmail.com",  # Replace with your email
    packages=find_packages(),
    install_requires=[
        'pyobjc-framework-CoreLocation',
        'pyobjc',
        'pystray',
        'pillow',
        # Add any other dependencies you might need
    ],
    entry_points={
        "console_scripts": [
            'mirrormirror=mirrormirror.main:main',
        ],
    },
    extras_require={
        'dev': [
            'pytest',
        ],
    }
)

