from setuptools import setup

with open("README.md", 'r') as f:
    readme_text = f.read()

setup(
    name='agave',
    version='0.1.0.dev1',
    description='a graphical abstract verification engine',
    license="bsd-3-clause",
    long_description=readme_text,
    author="Francesco Invernici",
    url="github.com/FrInve/agave",
    classifiers=[
        'Development Status :: 1 - Planning',

        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering',

        'License :: OSI Approved :: BSD License',

        'Natural Language :: English',

        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    packages=['agave'],
    install_requires=[
        'pandas',
        'neo4j',
        'sqlalchemy',
        'pymysql',
        'networkx',
        'pyarrow'
    ]
    #scripts=[]
)