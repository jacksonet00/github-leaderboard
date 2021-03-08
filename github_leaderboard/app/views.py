from django.shortcuts import render

# Create your views here.
def home(request):
   return render(request, 'pages/home.html') # This is the same page as before but it's just a stand in