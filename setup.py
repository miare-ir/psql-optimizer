import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers = [
    # Pick your license as you wish (should match "license" above)
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Framework :: Django",
    "Framework :: Django :: 2.2",
    "Framework :: Django :: 3.0",
    "Framework :: Django :: 3.1",
    "Framework :: Django :: 3.2",
    "Framework :: Django :: 4.0",
]

setuptools.setup(
    name='psql-stat-optimizer',
    version='0.0.45',
    author="Amir Alaghmandan",
    author_email="amir.amotlagh@gmail.com",
    description="Postgresql Set Statistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miare-ir/psql-optimizer",
    packages=setuptools.find_packages(exclude=["tests*"]),
    install_requires=["django-tqdm==1.3.1", "Django>=2.2"],
    classifiers=classifiers,
)
