<div align="center">
  <img src="http://vlpavlov.org/Pythagoras-Logo3.svg"><br>
</div>

# Pythagoras
## Advanced Python tools for Data Scientists

### Main Use Cases

1. ***Speed up*** your Data Science code by adding persistent file-based caching 
2. Make your scripts and classes ***easy to debug and reuse*** by equipping them with story-telling capabilities
3. Create ***well-performing baseline regression models*** that require no manual EDA, data cleaning, or feature engineering (coming soon)
4. ***Improve accuracy*** of your predictions by employing new efficient meta-algorithms (coming soon)

### How To Get It?

The source code is hosted on GitHub at:
[https://github.com/vladlpavlov/Pythagoras](https://github.com/vladlpavlov/Pythagoras) 

Binary installers for the latest released version are available at the Python package index at:
[https://pypi.org/project/Pythagoras](https://pypi.org/project/Pythagoras)

        pip install Pythagoras

### Major Pythagoras Components

* **PickleCache**: Pandas-compatible persistent caching, effortlessly extendable to work with new custom classes.

* **LoggableObject**: Simple base class that provides your objects with easy-to-use story-telling tools.

* **MagicGarden**: Automated regression baseline creator. It builds well-performing regression models that 
require no manual work from data scientists: no EDA, no data cleaning and no feature engineering (coming soon). 

* **SimpleGarden**: Efficient regression meta-algorithm: boosted feature selection factory creates an assembly of parsimonious regressors (coming soon).

* **FeatureShower**: Automatic data cleaner and feature generator (coming soon).

### Tutorials

1. [Basic Caching](https://github.com/vladlpavlov/Pythagoras/blob/master/Pythagoras_caching_introductory_tutorial.ipynb): 
How to speed up your scripts and notebooks if your Python code works with Pandas and build-in datatypes
2. [Advanced Caching](https://github.com/vladlpavlov/Pythagoras/blob/master/Pythagoras_caching_advanced_tutorial.ipynb): 
How to make Pythagoras PickleCache work with custom classes 
 
### Core Design Principles 

1. Pandas as main data vessel
2. Storytelling via logging
3. Feedback-supported training
4. Leakproof ensembling: predictors are transformers
5. Experimental meta-estimators
6. Compatibility with SKLearn (when practical)

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