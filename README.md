<div align="center">
  <img src="http://vlpavlov.org/Pythagoras-Logo3.svg"><br>
</div>

# Pythagoras
## Advanced Meta-Algorithms for Data Scientists

### What Is It?

An experimental SKLearn extension for researching meta-algorithms 

### How To Get It?

The source code is hosted on GitHub at:
[https://github.com/vladlpavlov/Pythagoras](https://github.com/vladlpavlov/Pythagoras) 

Binary installers for the latest released version are available at the Python package index at:
[https://pypi.org/project/Pythagoras](https://pypi.org/project/Pythagoras)

        pip install Pythagoras

### Core Design Principles 

1. Rapid experimentation
2. Feedback-supported training: ***.val_fit()*** instead of .fit() 
3. Ubiquitous ensembling
4. Predictors are transformers: ***.map()*** instead of .predict() and .transform() 
5. Compatibility with SKLearn when practical
6. Pandas as the main data vessel
7. Storytelling via logging
8. Acceleration via persistent caching

### Major Components

* **Learner**: An abstract base class, capable to be taught. Implements .val_fit() method.

* **CrossValMapper**: A meta-learner, capable to predict/transform. Implements .map() method.

* **PickleCache**: Pandas-compatible persistent caching, extendable to work with new classes.

* **LoggableObject**: Simple base class that provides easy-to-use story-telling tools.

* **FeatureShower**: Automatic data cleaner and feature generator (*coming soon*).

* **SimpleGarden**: Efficient regression meta-algorithm: boosted feature selection factory creates an assembly of parsimonious estimators (*coming soon*).

* **MagicGarden**: Automated regression baseline creator. It builds well-performing regression models that 
require no manual work from data scientists: no EDA, no data cleaning and no feature engineering (*coming soon*). 

### Tutorials

1. [Basic Caching](https://github.com/vladlpavlov/Pythagoras/blob/master/Pythagoras_caching_introductory_tutorial.ipynb): 
How to speed up your scripts and notebooks if your Python code works with Pandas and build-in datatypes
2. [Advanced Caching](https://github.com/vladlpavlov/Pythagoras/blob/master/Pythagoras_caching_advanced_tutorial.ipynb): 
How to make Pythagoras PickleCache work with custom classes 


### Dependencies

* [pandas](https://pandas.pydata.org/)
* [scikit-learn](https://scikit-learn.org/) 
* [numpy](https://numpy.org/)
* [scipy](https://www.scipy.org/)
* [xxhash](https://pypi.org/project/xxhash/)


### Key Contacts

* [Vlad(imir) Pavlov](https://www.linkedin.com/in/vlpavlov/): algorithm design and core development 
* [Kai Zhao](https://www.linkedin.com/in/kaimzhao/): quality assurance

### What Do The Name And Logo Mean?

Pythagoras was a famous ancient Greek thinker and scientist 
who was the first man to call himself a philosopher ("lover of wisdom"). 
He is most recognised for his many mathematical findings, 
including the Pythagorean theorem. 

But not everyone knows that in antiquity, Pythagoras was also credited with major astronomical discoveries,
such as sphericity of the Earth and the identity of the morning and evening stars as the planet Venus. 
Our logo depicts these, lesser known but not less important achievements of Pythagoras.