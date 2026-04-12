from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# def redirect_to_frontend(request):
#     return HttpResponseRedirect('http://127.0.0.1:5500/Frontend/templates/login.html')


urlpatterns = [
    #path('', redirect_to_frontend, name='home'),

    path('admin/', admin.site.urls),

    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/journal/', include('journal.urls')),
    path('api/nlp/', include('nlp.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/alerts/', include('alerts.urls')),
]