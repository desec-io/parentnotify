import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parentnotify",
    version="0.1",
    author="Peter Thomassen",
    author_email="peter@desec.io",
    description="DNS Notifications to the Parent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/desec-io/parentnotify",
    packages=setuptools.find_packages(),
    install_requires=['dnspython@git+https://github.com/peterthomassen/dnspython@20240720_DSYNC'],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: Name Service (DNS)",
    ],
    entry_points = {
        'console_scripts': ['parent-notify=parentnotify.commands.notify:main'],
    }
)
