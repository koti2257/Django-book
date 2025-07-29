from django.urls import path
from . import views
from .views import cancel_booking

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/theaters', views.theater_list, name='theater_list'),
    path('theater/<int:theater_id>/seats/book/', views.book_seats, name='book_seats'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('cancel-booking/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('profile/', views.profile_view, name='profile'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),  # ✅ Added route for "My Bookings"
]
