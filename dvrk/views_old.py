import urllib.request
import json
import math
import numpy as np
from scipy.spatial.transform import Rotation
from zmqRemoteApi import RemoteAPIClient
from django.shortcuts import render
from django.http import HttpResponse
import json

client = RemoteAPIClient()
sim = client.getObject('sim')
targetID = sim.getObject('/RCM_PSM2/Target')
gripper1 = sim.getObjectHandle("J3_dx_TOOL2")
gripper2 = sim.getObjectHandle("J3_sx_TOOL2")
toolPitch = sim.getObjectHandle("/RCM_PSM2/J2_TOOL2")
toolRoll = sim.getObjectHandle("J1_TOOL2")
pos = sim.getObjectPosition(targetID, -1)
print("TargetID & Position = ", targetID, pos)

sim.setJointPosition(gripper1, 0)
sim.setJointPosition(gripper2, 0)

posg1, posg2 = sim.getJointPosition(gripper1),sim.getJointPosition(gripper2)
tool_roll, tool_pitch = sim.getJointPosition(toolRoll),sim.getJointPosition(toolPitch)

init_joy = 100.0

action, f, b, s, sensitivity = 'joystick0', 0, 0, 0, 50
posx, posy, posz = init_joy, init_joy, init_joy
oldflag = 1
pos_flag = 1
scale = 0.0005
scale_gripper = 0.02
movex, movey, movez = 0,0,0
correction_factor = 0.5
yaw_sensitivity = 1
roll_sensitivity = 0.1
delx_old = posx
dely_old = posy
delz_old = posz
sensor_on = 0

def index(request):

    return render(request, 'home.html')

def apijoy(request):

    global posx, posy, posz,action, f, b, s, sensitivity,pos,posg1, posg2, pos_flag,delx_old,dely_old,delz_old, sensor_on
    if request.method == "POST" and request.is_ajax:

        f, b = 0,0

        action = request.POST['action']

        if action == 'joystick1':
            posx = float(request.POST['posx'])
            posy = float(request.POST['posy'])
        elif action == 'joystick2':
            posz = float(request.POST['posy'])
        elif action == 'open':
            f, b = 1,0
        elif action == 'close':
            b, f = 1,0
        elif action == 'On':
            s = 1
        elif action == 'Of':
            s = 0
        elif action == 'sensitivity':
            sensitivity = float(request.POST['sen'])
      
        if not sensor_on:

            dely, delx, delz,open_grip, close_grip,sensor_on, scale = posx, posy, posz,f,b,s,sensitivity
            
            movex = -(delx - delx_old)
            movey = (dely - dely_old)
            movez = -(delz - delz_old)

            delx_old = delx
            dely_old = dely
            delz_old = delz

            scale /= 16667
            if (movez or movex or movey):

                if delx != init_joy:
                    pos[0] -= movex*scale

                if dely != init_joy:
                    pos[1] += movey*scale

                if delz != init_joy:
                    pos[2] += movez*scale

                pos_flag = 0
                pos_flag = sim.setObjectPosition(targetID,-1,pos)
                
            # Gripper
            if open_grip or close_grip:
                posg1 += (open_grip-close_grip)*scale_gripper
                posg2 += (open_grip-close_grip)*scale_gripper
                g1_flag = sim.setJointPosition(gripper1, posg1) #gripper1
                g2_flag = sim.setJointPosition(gripper2, posg2)#gripper2


            # Orientation
        if sensor_on:

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

            # print(("tool-roll:  {:.3f} pitch-back:  {:.3f} base-yaw: {:.3f}").format(pos_roll,pos_pitch,pos_yaw))
            # print(("tool-roll:  {:.3f} pitch-back:  {:.3f} base-yaw: {:.3f}").format(na,nb,nc))

            tool_pitch += pos_yaw*yaw_sensitivity
            tool_roll += pos_roll*roll_sensitivity
            print(tool_pitch,  tool_roll)
            sim.setJointPosition(toolPitch, tool_pitch) #base-yaw (-pi, pi)   
            sim.setJointPosition(toolRoll, tool_roll)  #tool-roll (-pi, pi)

            # T_7_0 = compute_FK([b.get_joint_pos(0), b.get_joint_pos(6),b.get_joint_pos(2),b.get_joint_pos(1),b.get_joint_pos(5),b.get_joint_pos(3),b.get_joint_pos(4)])

            oa,ob,oc = na,nb,nc
            oldflag = 0

    return HttpResponse(json.dumps(s))
