<div align="center">
  <img src="http://vlpavlov.org/Pythagoras-Logo3.svg"><br>
</div>

# Pythagoras

## (1) What Is It?

An experimental framework that aims to democratize access to distributed serverless compute. 
We make it simple and inexpensive to create, deploy and run cloud-hosted massively parallel algorithms 
from within local Python scripts and notebooks. Pythagoras makes data scientists' lives easier, 
while allowing them to solve more complex problems in a shorter time with smaller budgets.

## (2) What Is Inside?
Pythagoras offers:
1. a powerful abstraction model for a global-scale serverless compute engine;
2. a simple API for Python programmers to use the engine;
3. a collection of backends that implement the API for various deployment scenarios 
(*work in progress, currently only P2P backend is available*)
4. a collection of massively parallel algorithms that take advantage of 
Pythagoras serverless compute engine (*planned*)

### ((2.1)) Pythagoras Abstraction Model For Global Compute Engine

Pythagoras offers a very powerful, yet simple abstraction model for a serverless compute engine. 
It contains three fundamental components:
* Massively parallel serverless code executor for pure functions; 
* Global persistent store for immutable values with hash-based addressing scheme; 
* Global persistent cache for function execution outputs.

This [overview](https://docs.google.com/document/d/1lgNOaRcZNGvW4wF894s7KmIWjhLX2cDVM_15a4lE02Y) 
provides detailed information about the abstraction model.

### ((2.2)) Pythagoras API

Pythagoras makes it very easy to scale computationally expensive code to the cloud, 
without a need to explicitly parallelize the code, to provision any infrastructure, 
or to orchestrate code deployment or execution.  

Data scientists can continue using their local workstations. 
They can keep working with their local Python scripts and Jupyter notebooks. 
They will need to add just a few extra lines to their existing code. 
After this change, computationally expensive parts of the local code will be 
automatically executed in the cloud on dozens (or even hundreds or thousands) servers, 
and the execution results will seamlessly get back to local workstations.

This [introduction tutorial](https://github.com/vladlpavlov/pythagoras/blob/master/pythagoras_introduction.ipynb) 
explains how to use the API. 

### ((2.3)) Pythagoras Backends
Backends are seamlessly interchangeable.
They differ by their under-the-hood implementations of deployment models and provisioning / orchestration algorithms. 
A collection of backends will offer engineers a wide variety of trade-offs that fit different use-cases.

As of now, Pythagoras team has implemented a 
[P2P version](https://github.com/vladlpavlov/pythagoras/blob/master/pythagoras_P2P_tutorial.ipynb) 
of the backend. It allows to parallelize program execution by simply launching the program simultaneously 
on a swarm of local computers (e.g. desktops and laptops in your office or dormitory).

The Pythagoras team is currently working on a reference implementation for AWS-based backend. 
Over time, we anticipate to have dozens of alternative backends. 
Please, reach to [Volodymyr (Vlad) Pavlov](https://www.linkedin.com/in/vlpavlov/) 
if you want to help to create one.

## (3) Roadmap

Pythagoras has just started and is actively evolving. Here is our roadmap for 2022:

1. Develop an abstraction model and API for the Global Compute Engine - **DONE**;
2. Develop several alternative backend implementations:
   1. P2P reference backend implementation - **DONE**;
   2. Basic AWS reference backend implementation - **IN PROGRESS**;
   3. Basic GCP backend implementation;
   4. Basic Azure backend implementation;
   5. Various advanced backend implementations for specific use-cases;
3. Implement massively parallel algorithms for Data Science and Machine Learning:
   1. Reference implementation for massively parallel grid search for hyperparameter optimisation - **IN PROGRESS**;
   2. Massively parallel implementations of popular DS/ML algorithms 
   that can benefit from highly scalable serverless compute;
   3. Brand-new DS/ML algorithms that were impossible to ideate in pre-serverless era.
   
## (4) How To Get It?

The source code is hosted on GitHub at:
[https://github.com/vladlpavlov/pythagoras](https://github.com/vladlpavlov/pythagoras) 

Binary installers for the latest released version are available at the Python package index at:
[https://pypi.org/project/pythagoras](https://pypi.org/project/pythagoras)

        pip install pythagoras

## (5) Dependencies

* [pandas](https://pandas.pydata.org)
* [scikit-learn](https://scikit-learn.org) 
* [numpy](https://numpy.org)
* [scipy](https://www.scipy.org)
* [psutil](https://pypi.org/project/psutil)
* [boto3](https://boto3.readthedocs.io)
* [moto](http://getmoto.org)
* [jsonpickle](https://jsonpickle.github.io)
* [pytest](https://pytest.org)
* [hypothesis](https://hypothesis.works) 


## (6) Key Contacts

* [Volodymyr (Vlad) Pavlov](https://www.linkedin.com/in/vlpavlov/) 
* [Illia Shestakov](https://www.linkedin.com/in/illia-shestakov-88716a21b/) 
* [Kai Zhao](https://www.linkedin.com/in/kaimzhao/)

## (7) What Do The Name And Logo Mean?

Pythagoras was a famous ancient Greek thinker and scientist 
who was the first man to call himself a philosopher ("lover of wisdom"). 
He is most recognised for his many mathematical findings, 
including the Pythagorean theorem. 

But not everyone knows that in antiquity, Pythagoras was also credited with major astronomical discoveries,
such as sphericity of the Earth and the identity of the morning and evening stars as the planet Venus. 
Our logo depicts these, lesser known but not less important achievements of Pythagoras.