from distutils.core import setup

setup(
    name="life-stream-cli",
    version="0.0.1",
    author="Sergey Royz",
    author_email="zjor.se@gmail.com",
    packages=["app"],
    include_package_data=True,
    url="git@github.com:zjor/life-log.git",
    license="LICENSE.txt",
    description="Useful towel-related stuff.",
    long_description=open("README.txt").read(),
    install_requires=[
        "requests==2.25.0",
        "click==7.1.2",
        "colorama==0.4.4",
        "termcolor==1.1.0",
        "prompt_toolkit==3.0.5"
    ],
)
