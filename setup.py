import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="Pythagoras"
    ,version="0.2.19"
    ,author="Vlad(imir) Pavlov"
    ,author_email="vlpavlov@ieee.org"
    ,description="Advanced Python tools for Data Scientists"
    ,long_description=long_description
    ,long_description_content_type="text/markdown"
    ,url="https://github.com/vladlpavlov/Pythagoras"
    ,packages=["Pythagoras"]
    ,classifiers=[
        "Development Status :: 3 - Alpha"
        , "Intended Audience :: Developers"
        , "Intended Audience :: Science/Research"
        , "Programming Language :: Python"
        , "Programming Language :: Python :: 3"
        , "License :: OSI Approved :: MIT License"
        , "Operating System :: OS Independent"
        , "Topic :: Scientific/Engineering"
        , "Topic :: Scientific/Engineering :: Information Analysis"
        , "Topic :: Software Development :: Libraries"
        , "Topic :: Software Development :: Libraries :: Python Modules"
    ]
    ,keywords='caching logging regression'
    ,python_requires='>=3.6'
    ,install_requires=['numpy', 'scipy','pandas', 'xxhash','scikit-learn', 'psutil']
)