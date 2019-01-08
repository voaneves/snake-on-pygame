snake-on-pygame
=================

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Neves4/snake-rl/graphs/commit-activity) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/) [![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://GitHub.com/Neves4/ama)

<p align="center">
    <img src = "resources/images/snake_logo.png"/>
</p>

Snake game that can be controlled by human input and AI agents (DQN). Who's best? :snake: :8ball:

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

You can download download the source code or clone the repository to your computer.

To clone the repository, open bash or command prompt, cd to the chosen directory
and run the following code:

```
$ git clone https://github.com/Neves4/SnakeAI.git
```

To download the repo, just follow along the gif (click 'Clone or Download' and
then 'Download ZIP').

![Download repo](/resources/gifs/download_repo.gif)

### 1.3. Playing <a name="playing-human"></a>

The GUI allows you to choose between single games and the benchmark mode. It's
also possible to choose between difficulty levels.

If using the repository files, change directory to the root, then to the game folder
and use:

```
$ python snake.py [-h]
```

In the benchmark mode, you will play through 10 games and your mean score/steps
are going to be recorded and you can add to the leaderboards. Pull request
changing the benchmark file ([located in here](resources/scores.json)) or open an issue with your score.


## 2. Getting Started (using AI agents) <a name="getting-started-ai"></a>

This game uses similar usage structure and methods to [OpenAI's gym](https://github.com/openai/gym) and you
can easily integrate it with any agent, written in Pytorch, Tensorflow, Theano or Keras.

It's recommended that you use [colab-rl](https://github.com/Neves4/colab-rl), a repository that integrates
state-of-the-art algorithms with games, because it already implements the agents
and the game, making the process of quick prototyping much easier.

### 2.1. Available methods to integrate with any agent <a name="available-methods"></a>

#### 2.1.1. Methods <a name="training-on-colab-rl"></a>

#### 2.1.2. Example <a name="training-on-colab-rl"></a>

### 2.2. Using colab-rl <a name="using-colab-rl"></a>

#### 2.2.1. Example <a name="training-on-colab-rl"></a>

## 3. Contributing <a name="contributing"></a>

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on this repo's code of conduct, and the process for submitting pull requests.

## 4. License <a name="license"></a>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 5. Acknowledgments <a name="acknowledgments"></a>

* @farizrahman4u - For his [qlearning4k](https://github.com/farizrahman4u/qlearning4k) snake code, I used it as the base of this repo's code.

* @chuyangliu - Also for his snake code, which implemented the relative actions.
