from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Theater, Seat, Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages

# Movie listing + search
def movie_list(request):
    search_query = request.GET.get('search')
    if search_query:
        movies = Movie.objects.filter(name__icontains=search_query)
    else:
        movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})

# Theater list with seat availability indicator
def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    theater_info = []
    for theater in theaters:
        total_seats = Seat.objects.filter(theater=theater).count()
        booked_seats = Seat.objects.filter(theater=theater, is_booked=True).count()
        is_available = booked_seats < total_seats

        theater_info.append({
            'id': theater.id,
            'name': theater.name,
            'time': theater.time,
            'is_available': is_available,
        })

    return render(request, 'movies/theater_list.html', {
        'movie': movie,
        'theaters': theater_info
    })

# Seat booking view
@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        error_seats = []

        if not selected_seats:
            return render(request, "movies/seat_selection.html", {
                'theater': theater,
                'seats': seats,
                'error': "No seat selected"
            })

        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theater.movie,
                    theater=theater
                )
                seat.is_booked = True
                seat.save()
            except IntegrityError:
                error_seats.append(seat.seat_number)

        if error_seats:
            error_message = f"The following seats are already booked: {', '.join(error_seats)}"
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                'seats': seats,
                'error': error_message
            })

        return redirect('profile')

    return render(request, 'movies/seat_selection.html', {
        'theater': theater,
        'seats': seats
    })

# Static Pages
def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

# Profile Page
@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

# Cancel booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    seat = booking.seat
    seat.is_booked = False
    seat.save()
    booking.delete()
    messages.success(request, 'Your booking has been canceled successfully.')
    return redirect('profile')

# My Bookings Page
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'movies/my_bookings.html', {'bookings': bookings})
