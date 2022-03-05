from django.shortcuts import render
from django.http import HttpResponse
import json      
from matplotlib.pyplot import imshow, show   

posx, posy, posz, action, f, b, s, sensitivity = 100,100, 100,'joystick0', 0, 0, 0, 50
img = 0

def index(request):

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

		# print(action, posx, posy, posz,f,b,s, sensitivity)
		print(f,b)
		return HttpResponse(json.dumps(1))

	elif request.method == "GET":

		actions = {'action': action, 'x': posx, 'y': posy, 'z': posz, 'o':f, 'c': b, 's':s, 'sensitivity': sensitivity}
		f,b = 0,0
		return HttpResponse(json.dumps(actions))



def apimg(request):
	global img
	if request.method == "POST" and request.is_ajax:
		img = request.read()
		print(len(img))
		# print(request.read())

		return  HttpResponse(1)


	elif request.method == "GET":
		# print(img)

		li = []
		for idx,i in enumerate(img):
			if (idx+1)%3 == 0:
				li.append(256)
			li.append(i)

		return  HttpResponse(img,headers={'Content-Type': 'application/octet-stream'})