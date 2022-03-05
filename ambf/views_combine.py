import urllib.request
import json
# from zmqRemoteApi import RemoteAPIClient
import asyncio
import cv2
from matplotlib.pyplot import imshow, show    
import numpy as np
from zmqRemoteApi.asyncio import RemoteAPIClient
from django.shortcuts import render
from django.http import HttpResponse
import json


posx, posy, posz, action, f, b, s, sensitivity = 100,100, 100,'joystick0', 0, 0, 0, 50
async def index(request):

	return render(request, 'home.html')

def apijoy(request):

	global posx, posy, posz,action, f, b, s, sensitivity
	if request.method == "POST" and request.is_ajax:
		f, b = 0,0
		action = request.POST['action']

		if action == 'joystick1':
			posx = request.POST['posx']
			posy = request.POST['posy']
		elif action == 'joystick2':
			posz = request.POST['posy']
		elif action == 'open':
			f, b = 1,0
		elif action == 'close':
			b, f = 1,0
		elif action == 'On':
			s = 1
		elif action == 'Of':
			s = 0
		elif action == 'sensitivity':
			sensitivity = request.POST['sen']

		print(action, posx, posy, posz,f,b,s, sensitivity)
		return HttpResponse(json.dumps(s))

	elif request.method == "GET":

		actions = {'action': action, 'x': posx, 'y': posy, 'z': posz, 'o':f, 'c': b, 's':s, 'sensitivity': sensitivity}
		f,b = 0,0

		return HttpResponse(json.dumps(actions))


def apimg(request):
	return  HttpResponse(json.dumps(1))


async def move_bot(sim):
    global posx, posy, posz

    targetID = await sim.getObject('/RCM_PSM2/Target')
    pos = await sim.getObjectPosition(targetID, -1)
    print("TargetID & Position = ", targetID, pos)

    init_joy = 100.0
    dely, delx, delz = float(posx), float(posy), float(posz)
    
    for i in range(100000000):

        delx_old = delx
        dely_old = dely
        delz_old = delz
        dely, delx,delz = float(posy) , float(posx), float(posz)

        # if not sensor_on:
        if 1:

            movex = -(delx - delx_old)
            movey = (dely - dely_old)
            movez = -(delz - delz_old)
            

            scale /= 16667
            if (movez or movex or movey):

                if delx != init_joy:
                    pos[0] -= movex*scale

                if dely != init_joy:
                    pos[1] += movey*scale

                if delz != init_joy:
                    pos[2] += movez*scale

                await sim.setObjectPosition(targetID,-1,pos)
                # print(pos)

        await asyncio.sleep(0.03)



async def get_img(sim):

    vis_left = await sim.getObjectHandle("./Vision_sensor_left")

    for i in range(100000):
        a,resx, resy = await sim.getVisionSensorCharImage(vis_left)
        # print(i)
        li = []
        for i in a:
            li.append(i)
        img = np.array(li,dtype=np.uint8).reshape(resx,resy,3)
        # print(img[0])
    #     cv2.imshow('image',img)
    #     cv2.waitKey()
        await asyncio.sleep(0.03)

    # cv2.destroyAllWindows()

async def main():

    async with RemoteAPIClient() as client:
        sim = await client.getObject('sim')

        task1  = asyncio.create_task(move_bot(sim))
        task2  = asyncio.create_task(get_img(sim))

        img = await task2
        bol = await task1


asyncio.run(main())

