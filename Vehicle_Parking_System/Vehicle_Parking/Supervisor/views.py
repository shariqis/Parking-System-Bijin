from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from User.models import Booking,Recharge
from django.http.response import HttpResponse
from Admin.models import User,Location,Mall,Customer,ParkingSlot,Staff,Rate
from django.db.models import Subquery
from decimal import Decimal
import cv2
import webbrowser
# Create your views here.
from datetime import datetime
from dateutil import parser
from django.utils import timezone
from datetime import timedelta


def Supervisorhome(request):
   
    return render(request,'supervisor/staffhome.html',{"uname":request.session["uname"]})



@login_required
def view_todays_booked_slots(request):
   
    
    # if not request.user.is_active or request.user.is_customer:
    #     return HttpResponse("You are not authorized to access this page.")

    # Get the mall associated with the logged-in supervisor
    '''   try:
        print('request.user',request.user.id)
        
        mall = Mall.objects.get(mall=request.user)
    except Mall.DoesNotExist:
        return HttpResponse("Mall not found for the logged-in supervisor.")'''

    # Filter bookings for today only
    today = datetime.now().date()
    
    print(today)
    # bookings = Booking.objects.filter(
    #     mall=mall,
    #     booked_at__date=today
    # ).select_related('parking_slot', 'user')
    
    
    # Subquery to get mall_id for staff with ID 14
    mall_id_subquery = Staff.objects.filter(
        staff_id=request.user.id  # staff_id in SQL
    ).values('mall_id')[:1]  # Assuming `mall_id` is a field in Admin_staff
    
    print('mall_id_subquery',mall_id_subquery)

    # Query to get bookings where the parking slot is in the corresponding mall
    bookings = Booking.objects.filter(
        parking_slot__mall_id=Subquery(mall_id_subquery),
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
    
    return render(request, 'supervisor/todays_booked_slots.html', {'bookings': bookings, 'today': today,'current_time':current_time})





@login_required
def bookingHistory(request):
    
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
    mall_id_subquery = Staff.objects.filter(
        staff_id=request.user.id  # staff_id in SQL
    ).values('mall_id')[:1]  # Assuming `mall_id` is a field in Admin_staff
    
    print('mall_id_subquery',mall_id_subquery)

    # Query to get bookings where the parking slot is in the corresponding mall
    bookings = Booking.objects.filter(
        parking_slot__mall_id=Subquery(mall_id_subquery),
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
    
    return render(request, 'supervisor/booking_history.html', {'bookings': bookings, 'today': today,'current_time':current_time})








import cv2
import webbrowser


def admin_view_QRcode_details(request): 
    
    cap=cv2.VideoCapture(0)
    detector=cv2.QRCodeDetector()
    while True:
        _,img=cap.read()
        data,one, _=detector.detectAndDecode(img)
        if data:
            a=data
            break
        cv2.imshow('qrcodescanner app',img)
        if cv2.waitKey(1)==ord('q'):
            break
    print(a)    
    # b=webbrowser.open(str(a))
    # cap.release(a)
    # cv2.destroyAllWindows()    
    # view = Student.objects.select_related('student_id','department_id','course_id').filter(student_id=a)
    
    booking=Booking.objects.get(id=a)
    mall_name = booking.parking_slot.mall.first_name
    slot_number = booking.parking_slot.slot_number 
    
    mall_id = booking.parking_slot.mall.id
    print(mall_id)
    
    staff_mall_id= Staff.objects.get(staff_id=request.session["staff_id"]).mall 
    
    print('staff_mall_id',staff_mall_id.id)
    
    if mall_id== staff_mall_id.id:
    
        body = f"""
        

        Here are your booking details of {booking.user.first_name}: 
        - Mall Name: {mall_name} 
        - Slot Number: {slot_number} 
        - Start Time: {booking.start_time} 
        - End Time: {booking.end_time} 
        

        Regards,
        {mall_name} Team
        """ 
        
        return render(request,'supervisor/view_QRcode_details.html',{'data':body,'id':a})
    else:
        return HttpResponse("<script>window.alert('Invalid QR CODE!!');window.location.href='/Supervisor/Supervisorhome/'</script>")





def Occupied(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # if request.method == 'POST':
    booking.status = 'Occupied'
    booking.save()
    # return redirect('manage_parking_slots')  
    return HttpResponse("<script>window.alert('Successfully  Occupied!!');window.location.href='/Supervisor/view_todays_booked_slots/'</script>")

def NotOccupied(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # if request.method == 'POST':
    booking.status = 'NotOccupied'
    booking.save()
    # return redirect('manage_parking_slots')  
    return HttpResponse("<script>window.alert('Successfully  Updated!!');window.location.href='/Supervisor/view_todays_booked_slots/'</script>")



def Payment(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    
    # Get the ParkingSlot related to this booking
    parking_slot = booking.parking_slot

    # Get the Mall related to the ParkingSlot
    mall = parking_slot.mall

    # Get the rate from the Mall's associated Rate model (assuming the rate applies to the vehicle type)
    # You may need to add filtering if the rate depends on vehicle type (example: 'Car', 'Truck')
    rate = Rate.objects.filter(mall=mall,vehicle_type=parking_slot.vehicle_type).first() 
    print('rate -> ',rate)
    # Assuming the booking has a related Recharge model and vehicle_type has a rate
    if booking.start_time and booking.end_time:
        # Calculate the time difference in hours
        time_difference = booking.end_time - booking.start_time
        hours = time_difference.total_seconds() / 3600  # Convert seconds to hours

        new_amount = Decimal(hours) * rate.rate_per_hour
        print('new_amount -> ',new_amount)
        recharge = Recharge.objects.filter(user=booking.user).first()
        
        recharge.amount -= new_amount
        recharge.save()

        # if request.method == 'POST':
        booking.status = 'Paid'
        booking.paid_amount=new_amount
        booking.save()



        parksslotid=booking.parking_slot.id
        parkingslot = ParkingSlot.objects.get(id=parksslotid)
        parkingslot.is_occupied = False
        parkingslot.save()        
        
        
        
        admin_mallid= Mall.objects.get(mall_id=mall)    
        
        
        
        admin_mallid.balance += new_amount
        admin_mallid.save()
        
        
        # return redirect('manage_parking_slots')  
        return HttpResponse("<script>window.alert('Successfully  Paid!!');window.location.href='/Supervisor/view_todays_booked_slots/'</script>")
