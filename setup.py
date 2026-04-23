from setuptools import find_packages, setup


setup(
    name="lotr-adventure",
    version="0.1.0",
    description="A text adventure in Middle-earth powered by the OpenAI API.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    package_data={"lotr_adventure": ["content/*.yaml"]},
    install_requires=[
        "openai>=1.0.0",
        "pydantic>=2.8.0",
        "PyYAML>=6.0.1",
        "rich>=13.9.0",
        "prompt_toolkit>=3.0.47",
        "python-dotenv>=1.0.1",
    ],
    extras_require={"dev": ["pytest>=8.3.0"]},
    entry_points={"console_scripts": ["lotr-adventure=lotr_adventure.main:main"]},
)
