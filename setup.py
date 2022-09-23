from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    readme_text = f.read()

setup(
    name='agave',
    version='0.2.0.dev2',
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
    packages=find_packages(),
    install_requires=[
        #'pandas',
        'neo4j',
        'sqlalchemy',
        'pymysql',
        'networkx',
        'pyarrow'
    ]
    #scripts=[]
)