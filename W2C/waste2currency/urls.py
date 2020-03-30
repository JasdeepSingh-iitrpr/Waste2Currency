from django.urls import path

from . import views

urlpatterns = [path("", views.home, name="home"),path("login",views.login,name = "login"),path("signup",views.signup,name="signup"),path("register",views.register,name="register"),path("logout",views.logout,name="logout"),path("balance",views.balance,name="balance"),path("WasteForm",views.WasteForm,name="WasteForm"),path("CreateWaste",views.CreateWaste,name="CreateWaste"),path("RequestForm",views.RequestForm,name="RequestForm"),path("SendRequest",views.SendRequest,name="SendRequest"),path("AcceptForm",views.AcceptForm,name="AcceptForm"),path("AcceptRequest",views.AcceptRequest,name="AcceptRequest"),path("transactions",views.transactions,name="transactions"),path("TrackForm",views.TrackForm,name="TrackForm"),path("track",views.track,name="track")]


