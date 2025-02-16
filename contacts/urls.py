from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),  # Home page
    path('add/', views.add_contact, name='add_contact'),
    path('search/', views.search_by_id, name='search_by_id'),
    path('update/<int:id>/', views.update_contact, name='update_contact'),  # Use 'id' instead of 'pk'
    path('delete/<int:id>/', views.delete_contact, name='delete_contact'),  # Use 'id' instead of 'pk'
    path('display/', views.display_contacts, name='display_contacts'),
]