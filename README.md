# AI_Rescue_Drone

Computer Vision based disaster relief drone (Tello) . CS698 Computer Science senior year project in progress.

### Prerequisites

To deploy the program on a local machine the following hardware/softwares are requires :

#### DjiTello

#### Python 3.7

#### Flask

#### SQLite3

To download required libraries, navigate to the project directory in terminal and type in the command below.

```
pip install -r requirements.txt
```

## Running the tests

1. To run a basic test of the drone's connection to the local machine, navigate to Drone directory and run test.py
2. To run tests on manual flying and video feed run fly.py
3. To test face detection and autonomous flight run activate.py

The following commands can be used to control the drone:

```
t = Takeoff
Up Key = Forward
Down Key = Backwards
Left Key = Left
Right Key = Right
a = Yaw Left
d  = Yaw Right
s = Descend
a = Ascend

```

When running activate.py use the following commands to switch between manual and autonomous flight after takeoff.

```
p = Automous Flight
m = Manual Flight
```

## Screenshots

- Flask Site
  ![alt text](/static/screenshots/site_screenshot.png?v=4&s=200)

## Built With

- [DJITELLOPU](https://github.com/damiafuentes/DJITelloPy) - DJI Tello Python3 Interface
- [OpenCV-Contrib](https://github.com/opencv/opencv_contrib) - Computer Vision Library
- [Pygame](https://github.com/pygame/pygame) - Graphical Interface Library

## Authors

- **Hamza Ehsan** - _Autonomous Flight_ - (www.hamzaehsan.com)
- **Damià Fuentes Escoté** - _DJI Tello Python3 Interface_ (https://github.com/damiafuentes)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

- Damià Fuentes Escoté
- Jabrils - Project Inspiration (https://github.com/Jabrils)
