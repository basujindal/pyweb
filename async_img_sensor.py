import urllib
import json
import asyncio
import time
import requests   
import math
import pandas as pd
from scipy.spatial.transform import Rotation
from zmqRemoteApi.asyncio import RemoteAPIClient
import sys
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-n", "--name", required=True, help="Experiment logs file name")
args = vars(ap.parse_args())
log_file = args["name"]


MAX_INT = sys.maxsize
server_url =  '10.42.0.1' # IP address of the Django server
smartphone_ip = '10.42.0.134' # IP address of the smartphone connected
                              # to the server

async def move_bot(sim):

    # CSV file to log simultion data
    df = pd.DataFrame(columns = ['Timestamp', 'PSM_xyz', 'PSM_roll_pitch','Gripper_angle_radians', 'Puzzle_position_xyz', 'smartphone_input'])
    row = {'Timestamp': 0, 'PSM_xyz': [0,0,0], 'PSM_roll_pitch': (0,0), 'Gripper_angle_radians':(0,0), 'Puzzle_position_xyz':0}

    # Getting object handles 
    targetID = await sim.getObjectHandle('TargetPSMR')
    gripper1 = await sim.getObjectHandle("J3_dx_TOOL2")
    gripper2 = await sim.getObjectHandle("J3_sx_TOOL2")
    toolPitch = await sim.getObjectHandle("/RCM_PSM2/J2_TOOL2")
    toolRoll = await sim.getObjectHandle("J1_TOOL2")
    peg = await sim.getObjectHandle("Peg")

    # Reading initial position
    pos = await sim.getObjectPosition(targetID, -1)
    posg1, posg2 = await sim.getJointPosition(gripper1), await sim.getJointPosition(gripper2)
    tool_roll, tool_pitch = await sim.getJointPosition(toolRoll),await sim.getJointPosition(toolPitch)
    peg_pos = await sim.getObjectPosition(peg, -1)
    print("TargetID & Position = ", targetID, pos, gripper1, gripper2)

    init_joy = 100.0
    js_ik = json.loads( urllib.request.urlopen('http://' +  server_url + ':8000/dvrk/apijoy/').read().decode('utf-8'))
    posy, posx, posz = float(js_ik['x']), float(js_ik['y']), float(js_ik['z'])

    # Logging initial position
    row['Timestamp'] = time.time()
    row['PSM_xyz'] = (pos[0], pos[1], pos[2])
    row['PSM_roll_pitch'] = (tool_roll, tool_pitch)
    row['Gripper_angle_radians'] = (posg1, posg2)
    row['Puzzle_position_xyz'] = peg_pos
    row['smartphone_input'] = js_ik
    df = df.append(row, ignore_index=True)
    df.to_csv(log_file)

    oldflag = 1
    movex, movey, movez = 0,0,0
    correction_factor = 0.5
    yaw_sensitivity = 1
    roll_sensitivity = 0.5
    

    for i in range(MAX_INT):

        flag = 0
        posx_old = posx
        posy_old = posy
        posz_old = posz

        js_ik = json.loads( urllib.request.urlopen('http://' + server_url + ':8000/dvrk/apijoy/').read().decode('utf-8'))
        posy, posx,posz, open_grip, close_grip, sensor_on, scale = float(js_ik['x']), float(js_ik['y']), float(js_ik['z']),js_ik['o'],js_ik['c'],js_ik['s'],float(js_ik['sensitivity']) 

        if not sensor_on:

            movex = -(posx - posx_old)
            movey = -(posy - posy_old)
            movez = -(posz - posz_old)

            scale /= 16667
            if (movez or movex or movey):
                flag = 1

                if posx != init_joy:
                    pos[0] -= movex*scale

                if posy != init_joy:
                    pos[1] += movey*scale

                if posz != init_joy:
                    pos[2] += movez*scale

                print(movez or movex or movey)

                await sim.setObjectPosition(targetID,-1,pos)

                
                # Limiting gripper angle between 0 and 1.5 radians
            if open_grip:
                posg1 = 0.8
                posg2  = 0.8
            elif close_grip:
                posg1 = 0
                posg2  = 0

            if open_grip or close_grip:
                flag = 1

                await sim.setJointPosition(gripper1, posg1) #set gripper position
                await sim.setJointPosition(gripper2, posg2)


        if sensor_on:
            flag = 1
        
            a = urllib.request.urlopen('http://' + smartphone_ip + ':8080/sensors.json')
            a = json.loads(a.read().decode('utf-8'))["rot_vector"]['data']

            i = len(a) -1
            quat = [a[i][1][3]] + a[i][1][:3]
            rot = Rotation.from_quat(quat)
            euler = rot.as_euler('xyz', degrees=True) #(mobile-yaw, mobile-pitch,mobile-roll )
            na,nb,nc = math.radians(euler[0]),math.radians(euler[1]),math.radians(euler[2])

            if oldflag:
                oa,ob,oc = na,nb,nc

            pos_roll = (na-oa)
            pos_yaw = (nc-oc)
            # pos_pitch = (nb-ob)
            

        # sensor values jump from -pi to pi, so this ensures that there is no sudden change  

            if abs(pos_roll) > correction_factor:
                pos_roll = 0 
            if abs(pos_yaw) > correction_factor:
                pos_yaw = 0 
            
            tool_pitch += pos_yaw*yaw_sensitivity
            tool_roll += pos_roll*roll_sensitivity
            print(tool_pitch,  tool_roll)
            await sim.setJointPosition(toolPitch, tool_pitch) #base-yaw (-pi, pi)   
            await sim.setJointPosition(toolRoll, tool_roll)  #tool-roll (-pi, pi)

            row['Timestamp'] = time.time()
            row['PSM_xyz'] = pos
            row['PSM_roll_pitch'] = (tool_roll, tool_pitch)
            row['Gripper_angle_radians'] = (posg1, posg2)
            row['Puzzle_position_xyz'] = sim.getObjectPosition(peg, -1)
            df = df.append(row, ignore_index=True)
            df.to_csv(log_file)
        
            oa,ob,oc = na,nb,nc
            oldflag = 0

        
        if(flag):
            peg_pos = await sim.getObjectPosition(peg, -1)
            row['Timestamp'] = time.time()
            row['PSM_xyz'] = pos
            row['PSM_roll_pitch'] = (tool_roll, tool_pitch)
            row['Gripper_angle_radians'] = (posg1, posg2)
            row['Puzzle_position_xyz'] = peg_pos
            row['smartphone_input'] = js_ik
            df = df.append(row, ignore_index=True)
            df.to_csv(log_file)
            flag = 0

        await asyncio.sleep(0.001)



async def get_img(sim):

    vis_left = await sim.getObjectHandle("./Vision_sensor_left")   
    t = time.time()
    for _ in range(MAX_INT):
        img,_,_ = await sim.getVisionSensorCharImage(vis_left)
        
        requests.post('http://' + server_url + ':8000/dvrk/apimg/', data = img, headers={'Content-Type': 'application/octet-stream'})

        await asyncio.sleep(0.001)


async def main():

    async with RemoteAPIClient() as client:
        sim = await client.getObject('sim')

        task1  = asyncio.create_task(move_bot(sim))
        task2  = asyncio.create_task(get_img(sim))

        await task1
        await task2
        

asyncio.run(main())

