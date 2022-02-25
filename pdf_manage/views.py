import os
from django.shortcuts import render,redirect
from .forms import UploadFileForm
from django.contrib import messages
from .forms import UploadFileForm
from django.conf import settings
from django.http import HttpResponse, Http404
from PyPDF2 import PdfFileReader, PdfFileWriter



tools =  [ {'title': 'pdf_combine', 
            'about': 'combines pdfs',
            'url' : 'upload'},
            {'title': 'brightness',
            'about': 'controls brightness',
             'url' : 'upload'} ]

def home(request):
    context = {'tools':tools}
    return render(request, 'pdf_manage/home.html', context)


def about(request):
    # return HttpResponse('<h1>PyTools About</h1>')
    return render(request, 'pdf_manage/about.html')


def merge_pdfs(paths, output):
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)



def handle_uploaded_file(f):
    PATH = 'media/pdfs/' + f.name
    with open(PATH, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def download(path):
    file_path = settings.MEDIA_ROOT + path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404



def upload_multiple_files(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        paths = []
        if form.is_valid():
            for f in files:
                handle_uploaded_file(f)
                paths.append('media/pdfs/' + f.name)
            merge_pdfs(paths, output='media/pdfs/merged.pdf')
            # messages.success(request, f'')
            # return render(request, "pdf_manage/download.html", {})
            return download('/pdfs/merged.pdf')

    else:
        form = UploadFileForm()
        # messages.error(request, f'Please upload PDF')
        return render(request, 'pdf_manage/upload.html', {'form': form})


# def addition(request):

#     num1 = request.POST['num1']
#     num2 = request.POST['num2']

#     if num1.isdigit() and num2.isdigit():
#         a = int(num1)
#         b = int(num2)
#         res = a + b

#         return render(request, "pdf_manage/result.html", {"result": res})
#     else:
#         res = "Only digits are allowed"
#         return render(request, "pdf_manage/result.html", {"result": res})
