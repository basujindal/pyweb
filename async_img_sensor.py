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
MAX_INT = sys.maxsize


async def move_bot(sim):

    df = pd.DataFrame(columns = ['Timestamp', 'Input_L', 'PSM_L', 'Gripper_L', 'Puzzle_position'])
    df.to_csv("Experiment1.csv")
    row = {'Timestamp': 0, 'Input_L': 0, 'PSM_L': (0,0,0), 'Gripper_L':(0,0), 'Puzzle_position':0}

    # Getting object handles 
    targetID = await sim.getObject('/RCM_PSM2/TargetPSMR')
    gripper1 = await sim.getObjectHandle("J3_dx_TOOL2")
    gripper2 = await sim.getObjectHandle("J3_sx_TOOL2")
    toolPitch = await sim.getObjectHandle("/RCM_PSM2/J2_TOOL2")
    toolRoll = await sim.getObjectHandle("J1_TOOL2")

    # Reading initial position
    pos = await sim.getObjectPosition(targetID, -1)
    posg1, posg2 = await sim.getJointPosition(gripper1), await sim.getJointPosition(gripper2)
    tool_roll, tool_pitch = await sim.getJointPosition(toolRoll),await sim.getJointPosition(toolPitch)
    print("TargetID & Position = ", targetID, pos, gripper1, gripper2)


    # Logging initial position
    row['PSM_L'] = (pos, tool_roll, tool_pitch)
    row['Gripper_L'] = (posg1, posg2)
    row['Timestamp'] = time.time()
    df = df.append(row, ignore_index=True)
    df.to_csv("Experiment1.csv")

    init_joy = 100.0
    url =  '10.42.0.1'
    js_ik = json.loads( urllib.request.urlopen('http://' +  url + ':8000/dvrk/apijoy/').read().decode('utf-8'))
    dely, delx, delz = float(js_ik['x']), float(js_ik['y']), float(js_ik['z'])

    oldflag = 1
    scale = 0.0005
    scale_gripper = 0.05
    movex, movey, movez = 0,0,0
    correction_factor = 0.5
    yaw_sensitivity = 1
    roll_sensitivity = 0.5
    

    for i in range(MAX_INT):
        flag = 0

        delx_old = delx
        dely_old = dely
        delz_old = delz

        js_ik = json.loads( urllib.request.urlopen('http://' + url + ':8000/dvrk/apijoy/').read().decode('utf-8'))
        dely, delx,delz, open_grip, close_grip,sensor_on, scale = float(js_ik['x']), float(js_ik['y']), float(js_ik['z']),js_ik['o'],js_ik['c'],js_ik['s'],float(js_ik['sensitivity'])  
        row['Input_L'] = js_ik

        if not sensor_on:
        # if 1:

            movex = -(delx - delx_old)
            movey = (dely - dely_old)
            movez = -(delz - delz_old)
            

            scale /= 16667
            if (movez or movex or movey):
                flag = 1

                if delx != init_joy:
                    pos[0] -= movex*scale

                if dely != init_joy:
                    pos[1] += movey*scale

                if delz != init_joy:
                    pos[2] += movez*scale

                print(movez or movex or movey)

                await sim.setObjectPosition(targetID,-1,pos)

            if open_grip or close_grip:
                flag = 1
                posg1 += (open_grip-close_grip)*scale_gripper
                posg2 += (open_grip-close_grip)*scale_gripper

                await sim.setJointPosition(gripper1, posg1) #gripper1
                await sim.setJointPosition(gripper2, posg2) #gripper2


            if(flag):
                row['PSM_L'] = (pos, tool_roll, tool_pitch)
                row['Gripper_L'] = (posg1, posg2)
                row['Timestamp'] = time.time()
                df = df.append(row, ignore_index=True)
                df.to_csv("Experiment1.csv")
                flag = 0


        if sensor_on:
        # if 0:

            a = urllib.request.urlopen('http://10.42.0.10:8080/sensors.json')
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
            pos_pitch = (nb-ob)
            

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

            row['PSM_L'] = (pos, tool_roll, tool_pitch)
            row['Timestamp'] = time.time()
            df = df.append(row, ignore_index=True)
            df.to_csv("Experiment1.csv")
        
            oa,ob,oc = na,nb,nc
            oldflag = 0

        await asyncio.sleep(0.001)



async def get_img(sim):

    vis_left = await sim.getObjectHandle("./Vision_sensor_left") 
    url =  '10.42.0.1'   
    t = time.time()
    for i in range(MAX_INT):
        img,resx, resy = await sim.getVisionSensorCharImage(vis_left)
        
        requests.post('http://' + url + ':8000/dvrk/apimg/', data = img, headers={'Content-Type': 'application/octet-stream'})
        
        if(i%100 == 0):
            print(time.time() - t)
            t = time.time()

        await asyncio.sleep(0.001)


async def main():

    async with RemoteAPIClient() as client:
        sim = await client.getObject('sim')

        task1  = asyncio.create_task(move_bot(sim))
        task2  = asyncio.create_task(get_img(sim))

        await task1
        await task2
        

asyncio.run(main())

