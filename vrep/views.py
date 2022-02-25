from django.shortcuts import render
from django.http import HttpResponse
import json


posx, posy, posz, action, f, b, s, sensitivity = 100,100, 100,'joystick0', 0, 0, 1, 50
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

		print(action, posx, posy, posz,f,b,s, sensitivity)
		return HttpResponse(json.dumps(s))

	elif request.method == "GET":

		actions = {'action': action, 'x': posx, 'y': posy, 'z': posz, 'o':f, 'c': b, 's':s, 'sensitivity': sensitivity}
		f,b = 0,0

		return HttpResponse(json.dumps(actions))