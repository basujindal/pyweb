# Instructions for conducting the experiments are in SOP.md

## Requirements

- Install Anaconda for python package version management
- Install the required python packages using `pip install -r requirements.txt`
- CoppeliaSim Simulator [Download](https://www.coppeliarobotics.com/downloads)

## Steps to run the Simulation

- Launch CoppeliaSim and open the scene `V-REP_models/dVRK_peg_transfer_smartphone.ttt`. This is our simulation Enviornment.

- Launch Python server made using Django for controlling dVRK simulation using `python manage.py runserver 0.0.0.0:8000`. The dvrk controller can be accessed on the link 127.0.0.1:8000

- If accessing the controller through smartphone, replace 127.0.0.1 by the host ip address.
  eg. 10.42.0.1:8000

- Run the script to communicate with CoppeliaSim simulation using `python async_img_sensor.py -n log_file_name.csv`

## Notes

- VREP_scenes were taken from a repository by [
  unina-icaros](https://github.com/unina-icaros/dvrk-vrep)
- zmqRemoteApi was taken from CoppeliaSim package.

## ToDo

- Number pins
- Scale geomagic board
- Log images
- Permanent viewing angle
- Prevent phone from selecting text
- better way to log
- Test Second Puzzle
- 2nd Phone
- Websockets
