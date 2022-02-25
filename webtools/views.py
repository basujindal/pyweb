from django.shortcuts import render

tools =  [ {'title': 'pdf_combine', 
			'about': 'combines pdfs'},
			{'title': 'brightness',
			'about': 'controls brightness'} ]

def home(request):
	context = {'tools':tools}
	return render(request, 'webtools/home.html', context)


def about(request):
    # return HttpResponse('<h1>PyTools About</h1>')
    return render(request, 'webtools/about.html')

# Create your views here.
