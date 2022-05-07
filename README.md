# Python Server

- Python server using Django for controlling dVRK simulation

## Requirements

- Django == 3.2.9
- CoppeliaSim Simulator [Download](https://www.coppeliarobotics.com/downloads)

## Steps to launch the server

- Launch the server using `python manage.py runserver 0.0.0.0:8000`. The dvrk controller can be accessed on the link 127.0.0.1:8000/dvrk

- If accessing the controller through smartphone, replace 127.0.0.1 by the host ip address.
  eg. 10.42.0.1:8000/dvrk
