from django.shortcuts import render
from django.db.models import Sum
from User.models import Booking
# Create your views here.
from django.contrib.auth.decorators import login_required

from datetime import datetime
from dateutil import parser
from django.utils import timezone
from datetime import timedelta

def Mallhome(request):

    result = Booking.objects.filter(parking_slot__mall_id=request.session["mall_id"]).aggregate(total_paid_amount=Sum('paid_amount'))
    print(result)
    return render(request,'mall/mallhome.html',{"uname":request.session["uname"],"total":result["total_paid_amount"]})

def transaction_history(request):
    
    booking=Booking.objects.filter(
    parking_slot__mall_id=request.session["mall_id"], 
    status="Paid"
        ).select_related('parking_slot','user').order_by('updated_at').values(
    'parking_slot__slot_number',  # Slot Number
    'user__username',             # Booked By
    'parking_slot__vehicle_type', # Vehicle Type
    'created_at',                 # Booked At
    'start_time',                 # Start At
    'end_time',                   # End At
    'paid_amount'          ,            # paid_amount
    'updated_at'
)
    
    return render(request,'mall/transaction_history.html',{"bookings":booking,"uname":request.session["uname"]})
    



@login_required
def mall_booking_history(request):
    
    if request.method == 'POST':
        today=request.POST.get('start_time')
    else:
        today = datetime.now().date()
        
    # if not request.user.is_active or request.user.is_customer:
    #     return HttpResponse("You are not authorized to access this page.")

    # Get the mall associated with the logged-in supervisor
    '''   try:
        print('request.user',request.user.id)
        
        mall = Mall.objects.get(mall=request.user)
    except Mall.DoesNotExist:
        return HttpResponse("Mall not found for the logged-in supervisor.")'''

    # Filter bookings for today only
    
    print(today)
    # bookings = Booking.objects.filter(
    #     mall=mall,
    #     booked_at__date=today
    # ).select_related('parking_slot', 'user')
    
    
    # Subquery to get mall_id for staff with ID 14
    # mall_id_subquery = Staff.objects.filter(
    #     staff_id=request.user.id  # staff_id in SQL
    # ).values('mall_id')  # Assuming `mall_id` is a field in Admin_staff
    
    # print('mall_id_subquery',mall_id_subquery)

    # Query to get bookings where the parking slot is in the corresponding mall
    bookings = Booking.objects.filter(
        parking_slot__mall_id=request.session["mall_id"],
        start_time__date=today
    ).select_related('parking_slot','user'
    ).values(
       'parking_slot__slot_number',  # Slot number
       'user__username',       # Booked by (username of the user)
       'parking_slot__vehicle_type',# Vehicle type
       'created_at',                 # Booked at timestamp
       'start_time',                # Start time
       'end_time'  ,
       'status' ,
       'id'# End time
   )
    
    print("mmmmmmmmmmmmmmmmmmmm",bookings)
    
    current_time = timezone.now()
    
    # start_time_dt = parser.parse(bookings.start_time)
    adjusted_time = current_time + timedelta(hours=5, minutes=30)
    formatted_time  = adjusted_time.strftime("%b. %d, %Y, %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")
    normalized_time = formatted_time.replace(".", "")
    converted_time = datetime.strptime(normalized_time, "%b %d, %Y, %I:%M %p")
    # current_time = datetime.strptime(formatted_time, "%b. %d, %Y, %I:%M %p")
    current_time=converted_time

    
    # print(booking.start_time  < current_time_dt)

    # Pass data to the template
    '''
    
    for booking in bookings:
        # Convert start_time string to a datetime object if needed
        start_time_dt = parse_datetime(booking['start_time']) if isinstance(booking['start_time'], str) else booking['start_time']
         # Ensure start_time is timezone-aware
        if start_time_dt is not None and timezone.is_naive(start_time_dt):
            start_time_dt = timezone.make_aware(start_time_dt, timezone.get_current_timezone())
        # Format the current time
        adjusted_time = current_time + timedelta(hours=5, minutes=30)
        formatted_current_time = adjusted_time.strftime("%b. %d, %Y, %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")
        
        # Add formatted time or other calculations to the booking
        booking['current_time'] = formatted_current_time
        
        booking['is_start_time_over'] = start_time_dt < formatted_current_time
        
        '''
    for booking in bookings:
        start_time = booking['start_time']  # Replace with actual field

        # Parse and process start_time
        if isinstance(start_time, str):
            start_time = parse_datetime(start_time)
        if start_time and timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, timezone.get_current_timezone())

        # Check if the start time has passed
        booking['current_time'] =  current_time
        print('///////////////////////////////',type(current_time))
        
        # booking['is_start_time_over'] = start_time and start_time < current_time
        
        # print(start_time and start_time < current_time)
    
    return render(request, 'mall/mall_booking_history.html', {'bookings': bookings, 'today': today,'current_time':current_time})
    