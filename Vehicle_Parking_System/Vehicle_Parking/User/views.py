from django.shortcuts import render,get_object_or_404,redirect
from Admin.models import User,Location,Mall,Customer,ParkingSlot
from User.models import Recharge,Booking
from django.views.decorators.csrf import csrf_exempt  
# Create your views here.
from django.http import JsonResponse
import json  # Add this line at the top of your file
from datetime import datetime
import stripe
from django.views.decorators.csrf import csrf_exempt 
from django.utils.timezone import make_aware,get_current_timezone
from django.utils import timezone
from django.http.response import HttpResponse
from django.utils.timezone import make_aware,get_current_timezone
from datetime import datetime

# Stripe API Key
stripe.api_key = "sk_test_51RCODB2NfdR6yj6nSzvDp3HBPqjbE6R0aULCt2YcyEb9wW00Kzj1lUyaD4aAgE1XKt9p5ytmx0aC9dqWSLUbjQZE00hoFNG9co"


def userhome(request):
    user = request.session['user_id']
    print(user)
        # print(request.session.items())  # Print all session items for debugging

    rr = User.objects.get(id=user)
    existing_recharge = Recharge.objects.filter(user=rr).first()

    if existing_recharge:
        # If the user exists, add the amount to the existing record
        balance=existing_recharge.amount 
    else:
        balance=0    
        
    request.session["balance"]    =balance
        # Get today's date
    today = timezone.now().date()

    # Get the logged-in user
    logged_in_user = request.user

    # Filter bookings and fetch the required fields
    bookings = Booking.objects.filter(
        user=logged_in_user,
        start_time__date__gt=today
    ).order_by('start_time').values(
        'parking_slot__slot_number',
        'user__username',
        'parking_slot__vehicle_type',
        'parking_slot__mall__username',
        'created_at',
        'start_time',
        'end_time',
        'status',
        'id'
    )

    # Count bookings where status is 'reserved'
    reserved_count = Booking.objects.filter(
        user=logged_in_user,
        status="reserved",
        start_time__date__gte=today
    ).count()    

    return render(request,'user/userhome.html',{"uname":request.session["uname"],'balance':balance,'count':reserved_count})



def available_slots(request):
    
    if request.session["balance"]<=500:
        return HttpResponse("<script>window.alert('Your account balance is below the limit. Please recharge!!');window.location.href='/user/paynow/'</script>")
        
    
    
    # Get location from query parameters (e.g., user input from a form or dropdown)
    selected_location = request.GET.get('location', None)

    if selected_location:
        # Query malls based on location and get free slots
        malls_with_free_slots = Mall.objects.filter(
            loc_id__location=selected_location
        ).prefetch_related(
            'mall'
        ).annotate(
            free_slots=ParkingSlot.objects.filter(
                mall=F('mall'), is_reserved=False, is_occupied=False
            )
        )
    else:
        malls_with_free_slots = None  # If no location selected, show none

    # Render the template with the context
    loc = Location.objects.all()
    return render(request, 'user/view_slots.html', {'loc': loc , "uname":request.session["uname"]})


def get_malls(request):
    location_id = request.GET.get('location_id')
    
    if location_id:
        malls = Mall.objects.filter(loc_id=location_id)
        malls_data = [{'id': mall.mall_id, 'name': mall.mall.username} for mall in malls]
    else:
        malls_data = []
    
    return JsonResponse({'malls': malls_data})

def get_slots(request):
    mall_id = request.GET.get('mall_id')
    start_date = request.GET.get('start_date')    
    end_date = request.GET.get('end_date')
    
    
    print("..............details .......",mall_id,start_date,end_date)
    
    if mall_id:
        slots = ParkingSlot.objects.filter(mall_id=mall_id).order_by('location')  #,  is_occupied=False
        print("//////",slots)
        
        slots_data = []
        for slot in slots:
            # Check if the parking slot is booked within the given date range
            is_occupied_indate = Booking.objects.filter(
                parking_slot_id=slot.id,
                start_time__lte=end_date,  # Check if booking overlaps the range
                end_time__gte=start_date,
                # now chanred
                status='reserved'
                
            ).exists()

    # Append slot data with additional is_occupied_indate field
            slots_data.append({
                'id': slot.id,
                'slot_number': slot.slot_number,
                'vehicle_type': slot.vehicle_type,
                'is_occupied': slot.is_occupied,
                'is_reserved': slot.is_reserved,
                'location': slot.location,
                'is_occupied_indate': 1 if is_occupied_indate else 0 # 0 for green and 1 for red
            })

        
        
        
        
        
        
        
        
        
        
        
        # slots_data = [{'id':slot.id,'slot_number': slot.slot_number, 'vehicle_type': slot.vehicle_type,'is_occupied':slot.is_occupied,'is_reserved':slot.is_reserved,'location':slot.location} for slot in slots]
        print("-----------------------------------",slots_data)
    else:
        slots_data = []
    
    return JsonResponse({'slots': slots_data})


#---------------------generate QR

import qrcode
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from django.db.models import Max


def admin_gen_QR(request,id)  :
    
    print('///////////////////',id)
    # Generate the QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(id)
    qr.make(fit=True)

    # Create an image from the QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    image_stream = BytesIO()
    qr_image.save(image_stream, format='PNG')
    
    book= Booking.objects.get(id=id)
    image_stream.seek(0)
    book.qr_code.save('image.png', ContentFile(image_stream.read()))

    book.save()
   
   
    # return HttpResponse("<script>window.alert('Successfully Qr Code Generated!!');window.location.href='/adminapp/admin_manage_QR'</script>")
    # return HttpResponse("QR code generated and saved successfully.")


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from django.conf import settings


def send_mail_qrcode(request,id):
    
    booking=Booking.objects.get(id=id)
    
    
    qr_code_url = booking.qr_code  # This gives the URL of the QR code image
    user_email = booking.user.email    # This gives the user's email address
    
    mall_name = booking.parking_slot.mall.first_name
    slot_number = booking.parking_slot.slot_number 

    
    print(f"slot_number: {slot_number}")
    
    filename = os.path.join(settings.MEDIA_ROOT, str( qr_code_url))
    
    # fromaddr = 'sharonvarghese046@gmail.com'
    fromaddr = 'questremi@gmail.com'
    # toaddr = 'sharonvarghese935@gmail.com'
    toaddr = user_email

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = user_email

    msg['Subject'] = " subject of the mail : Parking Slot Booking QR Code "   #subject of the mail

    body = f"""
    Hello {booking.user.first_name},

    Thank you for booking with us. Here are your booking details:
    - Mall Name: {mall_name}
    - Slot Number: {slot_number}
    - Start Time: {booking.start_time}
    - End Time: {booking.end_time}

    Please find the attached QR code for your booking.

    Regards,
    {mall_name} Team
    """     #description of mail

    msg.attach(MIMEText(body,'plain'))

    filename = filename

    attachment = open(filename,"rb")

    p = MIMEBase('application','octet-stream')

    p.set_payload((attachment).read())

    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename=%s" % filename)

    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com',587)

    s.starttls()

    # s.login("sharonvarghese046@gmail.com", "skuw juhz amwb uleg")
    s.login("questremi@gmail.com", "bpqs wnhu zzjm oydq")

    text = msg.as_string()

    s.sendmail(fromaddr,toaddr,text)

    s.quit()


@csrf_exempt  # Only for development; ensure CSRF protection in production
def book_slot(request):
    if request.method == 'POST':
        # try:
            print("///////////////////////////------")
            
            data = json.loads(request.body)
            print("datat",data)
            slot_id = data.get('slot_id')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            
            print("//////")
            print("slot_id",slot_id,"start_time",start_time,"end_time",end_time)



            # Retrieve the ParkingSlot and the user from the request
            parking_slot = ParkingSlot.objects.get(id=slot_id)
            user = request.user  # Make sure the user is authenticated

            # Check if the slot is already occupied or reserved
            # if  parking_slot.is_occupied:
            #     return JsonResponse({'success': False, 'message': 'Slot is already taken.'})


            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            
            # Parse the datetime and make it timezone-aware
            # start_time = make_aware(datetime.strptime(start_time, '%Y-%m-%dT%H:%M'))
            # start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            # start_time = make_aware(start_time, timezone=get_current_timezone())
            
            # end_time = make_aware(datetime.strptime(end_time, '%Y-%m-%dT%H:%M'))
            # end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            # end_time = make_aware(end_time, timezone=get_current_timezone())

       
            # Create a new booking
            booking = Booking.objects.create(
                user=user,
                parking_slot=parking_slot,
                start_time=start_time,
                end_time=end_time,
                status='reserved'
            )

            # Update the parking slot status (optional, depending on your use case)
            parking_slot.is_occupied = True
            parking_slot.save()
            
            max_id = Booking.objects.aggregate(Max('id'))['id__max']
            print("booking -> ",max_id)
            print("............../////////////////////////////")
            # admin_gen_QR(request,booking)
            qr_response = admin_gen_QR(request, id=max_id)
#generate qur code

            
            mail_send=send_mail_qrcode(request,id=max_id)

            
            
            return JsonResponse({'success': True, 'message': 'Slot booked successfully!'})

        # except ParkingSlot.DoesNotExist:
        #     return JsonResponse({'success': False, 'message': 'Parking slot does not exist.'})
        # except Exception as e:
        #     return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



# genereate QR Code







# Payment


# @login_required(login_url='/user_login/')
def paynow(request):
    user = request.session['user_id']
    rr = User.objects.get(id=user)

    if request.method == "POST":
        amount_str = request.POST.get('amount')
        amount = int(amount_str) * 100  # Stripe uses paisa

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': 'Wallet Recharge',
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/user/success/',
                cancel_url='http://127.0.0.1:8000/user/paynow/',
            )

            # Store amount in session for update after successful payment
            request.session['pending_recharge_amount'] = float(amount_str)
            request.session['stripe_session_id'] = session.id
            request.session.modified = True

            return redirect(session.url)
        except stripe.error.CardError as e:
            return render(request, 'user/payment_error.html', {'error': str(e)})
        except stripe.error.RateLimitError:
            return render(request, 'user/payment_error.html', {'error': 'Rate limit exceeded'})
        except stripe.error.InvalidRequestError as e:
            return render(request, 'user/payment_error.html', {'error': str(e)})
        except stripe.error.AuthenticationError:
            return render(request, 'user/payment_error.html', {'error': 'Authentication failed'})
        except stripe.error.APIConnectionError:
            return render(request, 'user/payment_error.html', {'error': 'Network error'})

    return render(request, 'user/stripe_checkout.html', {"name": rr.username, "email": rr.email, "price": 200, 'user': user})


@csrf_exempt
def success(request):
    """Handle successful Stripe payment"""
    user_id = request.session.get('user_id')
    pending_amount = request.session.get('pending_recharge_amount')
    
    if not user_id or not pending_amount:
        return redirect("userhome")
    
    try:
        rr = User.objects.get(id=user_id)
        existing_recharge = Recharge.objects.filter(user=rr).first()
        
        if existing_recharge:
            # If the user exists, add the amount to the existing record
            existing_recharge.amount += float(pending_amount)
            existing_recharge.save()
        else:
            # If the user doesn't exist, create a new Recharge record
            Recharge.objects.create(user=rr, amount=pending_amount)
        
        # Clear session data
        if 'pending_recharge_amount' in request.session:
            del request.session['pending_recharge_amount']
        if 'stripe_session_id' in request.session:
            del request.session['stripe_session_id']
        request.session.modified = True
        
        return redirect("userhome")
    except Exception as e:
        print(f"An error occurred in success: {e}")
        return redirect("userhome")
    
    
    
    
@csrf_exempt  # Only for development; ensure CSRF protection in production
def my_booking_history(request): 
    
    logged_in_user = request.user
    bookings = Booking.objects.filter(user=logged_in_user).order_by('-start_time').values('parking_slot__slot_number',
    'user__username',
    'parking_slot__vehicle_type',
    'parking_slot__mall__username',  #__mall_user
    'created_at',
    'start_time',
    'end_time',
    'status',)  
    
    return render(request,'user/my_booked_slots.html',{"bookings":bookings}) 


@csrf_exempt  # Only for development; ensure CSRF protection in production
def upcomming_booking(request): 
    today = timezone.now().date()
    print(today)
    logged_in_user = request.user
    bookings = Booking.objects.filter(
        user=logged_in_user,
        start_time__date__gte=today  # Filter where start_time is greater than today
        ).order_by('start_time').values('parking_slot__slot_number',
    'user__username',
    'parking_slot__vehicle_type',
    'parking_slot__mall__username',  #__mall_user
    'created_at',
    'start_time',
    'end_time',
    'status',
    'qr_code',
    'id')  
    return render(request,'user/upcomming_booking.html',{"bookings":bookings}) 



def Cancel_Booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # if request.method == 'POST':
    booking.status = 'Cancelled'
    booking.save()


    parksslotid=booking.parking_slot.id
    parkingslot = ParkingSlot.objects.get(id=parksslotid)
    parkingslot.is_occupied = False
    parkingslot.save()
    
    # return redirect('manage_parking_slots')  
    return HttpResponse("<script>window.alert('Successfully  Cancelled!!');window.location.href='/user/upcomming_booking/'</script>")



def map_booking(request):
    return render(request,'user/map-booking.html')