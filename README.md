<div align="center">
  <img src="http://vlpavlov.org/Pythagoras-Logo3.svg"><br>
</div>

# Pythagoras

## What Is It?

An experimental framework that aims to democratize access to distributed serverless compute. 
We make it simple and inexpensive to create, deploy and run cloud-hosted massively parallel algorithms 
from within local Python scripts and notebooks. Pythagoras makes data scientists' lives easier, 
while allowing them to solve more complex problems in a shorter time with smaller budgets.

## What Is In It?
Pythagoras offers:
1. a powerful abstraction model for a global-scale serverless compute engine;
2. a simple API for Python programmers to use the engine;
3. a collection of backends that implement the API for various deployment scenarios.

### 1. Pythagoras Abstraction Model For Global Compute Engine

Pythagoras offers a very powerful, yet extremely simple abstraction model for a serverless compute engine. 
It contains three fundamental components:
* Massively parallel serverless code executor; 
* Global store for immutable values with hash-based addressing; 
* Global cache for function execution outputs.

**Massively parallel serverless code executor** takes care of launching on demand 
virtually unlimited number of concurrently running instances of code. Pythagoras requires the parallelized code 
to be packaged into [pure](https://en.wikipedia.org/wiki/Pure_function) functions. 
A function is considered pure when it is fully deterministic 
(it's output value depends solidly on input arguments, 
the function return values are identical for identical arguments), 
and function execution has no side effects (no mutation of local static variables, non-local variables, 
mutable reference arguments or input/output streams). 
In return to adhering to these constraints, Pythagoras offers unlimited scalability 
and elasticity of its serverless code execution environment.

**Global value store**, as the name implies, stores all the values ever created within any running instance of your code. 
It's a key-value store, where the key (the object's address) is composed using the object's hash.
Under the hood, these hash-based addresses are used by Pythagoras the same way as RAM-based addresses are used
(via pointers and references) in C and C++ libraries. For example, 
while passing input arguments to a remotely executed function, 
only the hash-based addresses of the arguments are passed, 
not their actual values. Such approach makes it possible to significantly decrease data marshalling overhead, 
while immutability of values allows to employ a variety of optimization techniques to speed up 
access to the objects in a distributed system.

**Global function output store** caches all results of all function executions that ever happened in the system. 
It allows to employ "calculate once, reuse forever" approach, which makes repeated execution of the same code 
blazingly fast and ridiculously cheap. It also improves software recoverability and availability: 
an interrupted program, once restarted, will reuse already calculated and cached values, 
and almost immediately will continue its execution from the point where it was terminated.

### 2. Pythagoras API

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

### 3. Pythagoras backends
Backends are seamlessly interchangeable.
They differ by their under-the-hood implementations of deployment models and provisioning / orchestration algorithms. 
A collection of backends will offer engineers a wide variety of trade-offs that fit different use-cases.

As of now, Pythagoras team has implemented a P2P version of the backend. 
It allows to parallelize program execution by simply launching the program simultaneously 
on a swarm of local computers (e.g. desktops and laptops in your office or dorm).

The Pythagoras team is currently working on a reference implementation for AWS-based backend. 
Over time, we anticipate to have dozens of alternative backends. 
Please, reach to [Volodymyr (Vlad) Pavlov](https://www.linkedin.com/in/vlpavlov/) 
if you want to help to create one.

## How To Get It?

The source code is hosted on GitHub at:
[https://github.com/vladlpavlov/pythagoras](https://github.com/vladlpavlov/pythagoras) 

Binary installers for the latest released version are available at the Python package index at:
[https://pypi.org/project/pythagoras](https://pypi.org/project/pythagoras)

        pip install pythagoras

## Dependencies

* [pandas](https://pandas.pydata.org/)
* [scikit-learn](https://scikit-learn.org/) 
* [numpy](https://numpy.org/)
* [scipy](https://www.scipy.org/)
* [psutil](https://pypi.org/project/psutil/)

## Key Contacts

* [Volodymyr (Vlad) Pavlov](https://www.linkedin.com/in/vlpavlov/): algorithm design and core development 
* [Kai Zhao](https://www.linkedin.com/in/kaimzhao/): quality assurance

## What Do The Name And Logo Mean?

Pythagoras was a famous ancient Greek thinker and scientist 
who was the first man to call himself a philosopher ("lover of wisdom"). 
He is most recognised for his many mathematical findings, 
including the Pythagorean theorem. 

But not everyone knows that in antiquity, Pythagoras was also credited with major astronomical discoveries,
such as sphericity of the Earth and the identity of the morning and evening stars as the planet Venus. 
Our logo depicts these, lesser known but not less important achievements of Pythagoras.