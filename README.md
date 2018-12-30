snake-pygame
=================

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Neves4/snake-rl/graphs/commit-activity) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/) [![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://GitHub.com/Neves4/ama)

<p align="center">
    <img src = "resources/images/snake_logo.png"/>
</p>

Snake game that can be controlled by human input and AI agents (DQN). Who's best? :8ball:

Table of Contents
=================

* [1. Getting Started (for human players)](#getting_started-human)
    * [1.1. Prerequisites](#pre-req-human)
    * [1.2. Installing](#installing-human)
    * [1.3. Playing](#playing-human)
* [2. Getting Started (using AI agents)](#getting_started-ai)
    * [2.1. Prerequisites](#pre-req-ai)
    * [2.2. Installing](#installing-ai)
    * [2.3. Training](#training-ai)
    * [2.4. Testing](#testing-ai)
* [3. Contributing](#contributing)
* [4. License](#license)
* [5. Acknowledgments](#acknowledgments)

## 1. Getting Started (for human players) <a name="getting-started-human"></a>

Let's get the game up and running on your computer, with the instructions below.
You can play the game and compare to the repos benchmark, which includes AI and
humans (you can include yourself by a pull request - WIP).

### 1.1. Prerequisites <a name="pre-req-human"></a>

To play the game you need Python 3.4+. If you installed [Anaconda](https://www.anaconda.com/) the only package
you need to download is pygame. Before installing it, make sure your Anaconda
installation is up-to-date using the command (conda update conda anaconda)and
updating all packages (conda update --all). To install pygame, use:

```
$ conda install -c cogsci pygame

```
It's highly recommended to use Anaconda to manage your Python packages and environments.
If you chose not to, make sure you run requirements_human.txt, using:

```
$ pip3 install -r requirements_human.txt
```

### 1.2. Installing <a name="installing-human"></a>

You can download the executable (WIP), download the source code or clone the
repository to your computer.

To download the executable, you can just [click here](stillnolink.com).

To clone the repository, open bash or command prompt, cd to the chosen directory
and run the following code:

```
$ git clone https://github.com/Neves4/SnakeAI.git
```

To download the repo, just follow along the gif (click 'Clone or Download' and
then 'Download ZIP').

![Download repo](/resources/gifs/download_repo.gif)

### 1.3. Playing <a name="playing-human"></a>

If using the executable, just double-click it. The GUI allows you to choose between
single games and the benchmark mode. It's also possible to choose between difficulties
levels.

If using the repository files, change directory to the root, then to the game folder
and use:

```
$ python snake.py [-h]
```

If using benchmark mode, you will play through 10 games and your mean score/steps
are going to be printed on the screen and console. Pull request changing the benchmark
file (WIP) or open an issue with your score.

## 2. Getting Started (using AI agents) <a name="getting-started-ai"></a>

You can play with or train AI agents, which will choose the best action according
to given policies. The currently implemented algorithms are:

* DQN:
    * Deep Q-Network (DQN) (with ExperienceReplay) [1]
        Paper: https://arxiv.org/abs/1312.5602
    * Double DQN [2]
        Paper: https://arxiv.org/abs/1509.06461
    * Dueling DQN [3]
        Paper: https://arxiv.org/abs/1511.06581
    * Prioritized Experience Replay (PER) [4]
        Paper: https://arxiv.org/abs/1511.05952
    * Multi-step returns [5]
        Paper: https://arxiv.org/pdf/1703.01327

* ACER:
    * WIP [6]
        Paper: https://arxiv.org/abs/1611.01224

### 2.1. Prerequisites <a name="pre-req-ai"></a>

### 2.2. Installing <a name="installing-ai"></a>

### 2.3. Training <a name="training-ai"></a>

### 2.4. Testing <a name="testing-ai"></a>

## 3. Contributing <a name="contributing"></a>

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## 4. License <a name="license"></a>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 5. Acknowledgments <a name="acknowledgments"></a>

* @farizrahman4u - For his [qlearning4k](https://github.com/farizrahman4u/qlearning4k) code;
* @chuyangliu - For being supportive with my questions;
* @Kaixhin - For his implementations of state-of-the-art RL models;
* @qfettes for his awesome repo [DeepRL-Tutorials](https://github.com/qfettes/DeepRL-Tutorials).
* @simoninithomas - awesome articles and implementations on his [repo](https://github.com/simoninithomas/Deep_reinforcement_learning_Course)
* A lot of other people that helped me entering in this journey :)
