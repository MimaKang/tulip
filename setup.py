from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
        name = "tulip",
        version="0.1.0",
        author="Mima Kang",
        author_email="mima@fiftypercent-magazine.org",
        description="Simple personal database application",
        long_description = long_description,
        long_description_content_type="text/markdown",
        url="",
        license="MIT",
        packages=['tulip'],
        python_requires='>=3',
        classifiers=[
            'Development Status :: 3 - Alpha',
            "Programming Language :: Python",
            "programming Language :: Python :: 3 :: Only",
            "programming Language :: Python :: 3.6",
            "programming Language :: Python :: 3.7",
        ],
        entry_points = {
                'console_scripts': [
                    'tulip=tulip.tulip:main',
                ],
            },

)
