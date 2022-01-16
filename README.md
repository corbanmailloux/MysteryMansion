# MysteryMansion
A Python 3 rebuild of the Electronic Talking Mystery Mansion board game.


### Wait, why?
My family *loves* this game. As kids, we used to play it all the time. At a recent family event, we wanted to play it and discovered that the "computer" part wasn't reliably working. I joked that I could recreate the game... and a couple hours of tinkering later, we were playing again.

### Installation
#### Windows
Because Python provides the [winsound](https://docs.python.org/3.1/library/winsound.html) library, no additional packages are required.

Just clone the repository and run `python3 game.py`.

#### Linux and MacOS
For Linux and MacOS, audio support depends on [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/).

Follow the installation steps on the page linked above, clone the repository, and run `python3 game.py`.

If you would prefer not to use PyAudio (or it fails to install), you can run the game without audio support by changing the following code near the top of `game.py`:

```python
ENABLE_AUDIO = True
```

becomes:

```python
ENABLE_AUDIO = False
```
