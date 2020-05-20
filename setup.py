import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytint",  # Replace with your own username
    version="0.0.3",
    author="Jinyu Liu",
    author_email="electronrush@gmail.com",
    description="A Python interpreter and visualization tool for finite automatons.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/semicolonTransistor/PyTint",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyyaml',
        'graphviz'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "pytint = pytint.command_line:main",
        ],
    },
    python_requires='>=3.6',
)