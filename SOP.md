## User guidelines

- The goal of the experiment is to pick and place the Peg from one Pin to another using dVRK PSM controlled by a smartphone and the Geomagic Haptic device.

- The pin will be randomly chosen before the experiment.

- Each participants will be given 2 trial attemts in the beginning.

- Participant will have to solve the puzzle 10 times using both Smartphone application and Haptic device.

- Approximate time per participant is around 30 minutes

# Instructions for performing the experiment using a Geomagic Touch

- The Geomagic stylus should be inserted inside the ink well before each experiment.

- The stylus will move the PSM tip position in the 3D space.

- The upper button and the lower button will open and close the gripper repectively.

## Steps

1. Launch the ROS node

```
sudo chmod 777 /dev/ttyACM0 && source devel/setup.bash && roslaunch omni_common omni_state.launch
```

2. Launch CoppeliaSim and open the scene `GeoMagicTouch-3ds-USB/V-REP_scenes/dVRK_peg_transfer_geomagic.ttt`. This is our simulation Enviornment.

3. Start the simulation in CoppeliaSim

4. Run `python rosnode_listener.py`

5. After the experiment is done stop rosnode_listener.py

6. Insert stylus back into the Ink Well and stop the simulation.

7. Repeat steps 3 to 6 for each user and each experiment.

# Instructions for performing the experiment using a SmartPhone

- Make sure that the smartphone is connected to the Django server

- Open and close button opens and closes the PSM gripper repectively

- The upper joystick controls the xy position of the PSM tooltip

- The lower joystick vertical movement controls the z position of the PSM tooltip.

- The scrollbar controls the scaling factor of the joystic movement to PSM movement

## Steps to perform the experiment

1. Launch the Django server using `python manage.py runserver 0.0.0.0:8000`

2. Launch CoppeliaSim and open the scene `pyweb/V-REP_scenes/dVRK_peg_transfer_smartphone.ttt`. This is our simulation Enviornment.

3. Start the simulation in CoppeliaSim

4. Run `python async_img_sensor.py`

5. After the experiment is done stop async_img_sensor.py

6. Stop the simulation.

7. Repeat steps 3 to 6 for each user and each experiment.
