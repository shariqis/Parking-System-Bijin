from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import ParkingSlotForm, RateForm, LocationForm
from .models import ParkingSlot, Rate , User , Location,Mall,Staff
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from Home.forms import CustomUserCreationForm 
# Create your views here.


def manage_parking_slots(request):
    # parking_slots = ParkingSlot.objects.all()
    
    if request.method == 'POST':
        form = ParkingSlotForm(request.POST)
        print(form)
        if form.is_valid():
            print("........................")
            parking_slot=form.save(commit=False)
            parking_slot.mall = User.objects.get(id=request.session['mall_id'])  # or whatever session data you're using
            parking_slot.save()
            # return redirect('manage_parking_slots')
            return HttpResponse("<script>window.alert('Successfully  Saved!!');window.location.href='/adminApp/manage_parking_slots/'</script>")
        
    else:
        form = ParkingSlotForm()
    return  render(request, 'admin/manage_parking_slots.html', {'form': form ,"uname":request.session["uname"]})  #, 'parking_slots': parking_slots


def view_parking_slots(request):
    mall_id = request.session.get('mall_id')
    parking_slots = ParkingSlot.objects.filter(mall_id=mall_id)
    return render(request, 'admin/view_parking_slots.html', {'parking_slots': parking_slots,"uname":request.session["uname"]})

def set_parking_rates(request):
    # rates = Rate.objects.all()
    if request.method == 'POST':
        form = RateForm(request.POST)
        if form.is_valid():
            
            vehicle_type = form.cleaned_data.get('vehicle_type')  # Assuming 'rate_type' is either 'car' or 'bike'
            mall_id=request.session['mall_id']
            # Check if the rate for this mall already exists (for car or bike)
            existing_rate = Rate.objects.filter(mall=mall_id, vehicle_type=vehicle_type).first()
            if existing_rate:
                print("///////////")
                
                return HttpResponse("<script>window.alert('Rate is already exists!');window.location.href='/adminApp/set-parking-rates/'</script>")
            
            print("............")
            parking_rate=form.save(commit=False)
            parking_rate.mall = User.objects.get(id=request.session['mall_id'])
            parking_rate.save()
            # return redirect('set_parking_rates')
            return HttpResponse("<script>window.alert('Successfully  Saved!!');window.location.href='/adminApp/view-parking-rates/'</script>")
            
    else:
        form = RateForm()
    return render(request, 'admin/set_parking_rates.html', {'form': form,"uname":request.session["uname"]})  #, 'rates': rates


def view_parking_rates(request):
    mall_id = request.session.get('mall_id')
    rates = Rate.objects.filter(mall_id=mall_id)
    return render(request, 'admin/view_parking_rates.html', { 'rates': rates, "uname":request.session["uname"]})
    
def edit_parking_rates(request, pk):
    rate = get_object_or_404(Rate, pk=pk)
    if request.method == 'POST':
        form = RateForm(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            # return redirect('manage_parking_slots')  
            return HttpResponse("<script>window.alert('Successfully  Updated!!');window.location.href='/adminApp/view-parking-rates/'</script>")
    else:
        form = RateForm(instance=rate)  
    return render(request, 'admin/edit_parking_rate.html', {'form': form ,"uname":request.session["uname"]})  #, 'rate': rate


def delete_parking_rates(request, pk):
    rate = get_object_or_404(Rate, pk=pk)
    # if request.method == 'POST':
    rate.delete()
    # return redirect('manage_parking_slots')  
    return HttpResponse("<script>window.alert('Successfully  Deleted!!');window.location.href='/adminApp/view-parking-rates/'</script>")


def edit_parking_slot(request, pk):
    slot = get_object_or_404(ParkingSlot, pk=pk)
    if request.method == 'POST':
        form = ParkingSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            # return redirect('manage_parking_slots')  
            return HttpResponse("<script>window.alert('Successfully  Updated!!');window.location.href='/adminApp/view_parking_slots/'</script>")
    else:
        form = ParkingSlotForm(instance=slot)  
    return render(request, 'admin/edit_parking_slot.html', {'form': form, 'slot': slot,"uname":request.session["uname"]})



def delete_parking_slot(request, pk):
    slot = get_object_or_404(ParkingSlot, pk=pk)
    # if request.method == 'POST':
    slot.delete()
    # return redirect('manage_parking_slots')  
    return HttpResponse("<script>window.alert('Successfully  Deleted!!');window.location.href='/adminApp/view_parking_slots/'</script>")


# Check if the user is an admin
def is_admin(user):
    return user.is_superuser  # Or any other condition for an admin user


# List of pending users awaiting approval
@user_passes_test(is_admin)
def pending_users(request):
    users = User.objects.filter(is_active=False,is_customer=1)  # Only show unapproved users
    return render(request, 'admin/pending_users.html', {'users': users,"uname":request.session["uname"]})    


@user_passes_test(is_admin)
def view_users(request):
    users = User.objects.filter(is_active=True,is_customer=1)  # Only show unapproved users
    return render(request, 'admin/view_users.html', {'users': users,"uname":request.session["uname"]})    


# Approve a user
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been approved.')
    # return redirect('pending_users')
    return HttpResponse("<script>window.alert('Successfully Approved!');window.location.href='/adminApp/pending-users/'</script>")

# Reject (delete) a user
@user_passes_test(is_admin)
def reject_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.success(request, f'User {user.username} has been rejected and deleted.')
    # return redirect('pending_users')
    return HttpResponse("<script>window.alert('Successfully Rejected!');window.location.href='/adminApp/pending-users/'</script>")
    

@user_passes_test(is_admin)
def pending_malls(request):
    users = Mall.objects.filter(mall__is_active=False, mall__is_customer=2)  # Only show unapproved users
    return render(request, 'admin/pending_malls.html', {'users': users,"uname":request.session["uname"]})  

@user_passes_test(is_admin)
def view_malls(request):
    users = Mall.objects.filter(mall__is_active=True, mall__is_customer=2)  # Only show unapproved users
    return render(request, 'admin/view_malls.html', {'users': users,"uname":request.session["uname"]})  
  


# Approve a user
@user_passes_test(is_admin)
def approve_mall(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.first_name} has been approved.')
    # return redirect('pending_users')
    return HttpResponse("<script>window.alert('Successfully Approved!');window.location.href='/adminApp/pending-malls/'</script>")

# Reject (delete) a user
@user_passes_test(is_admin)
def reject_mall(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.success(request, f'User {user.first_name} has been rejected and deleted.')
    # return redirect('pending_users')
    return HttpResponse("<script>window.alert('Successfully Rejected!');window.location.href='/adminApp/pending-malls/'</script>")
    


def adminhome(request):   
    
    mall_count = Mall.objects.filter(mall__is_active=True, mall__is_customer=2).count()

    # Count of active users
    user_count = User.objects.filter(is_active=True, is_customer=1).count()

    print(f"Active Malls: {mall_count}")
    print(f"Active Users: {user_count}")

    return render(request,'admin/home.html',{'mall_count':mall_count,'user_count':user_count})



def addSupervisor(request):
    mall_id=request.session['mall_id']
    print(mall_id)
    data = Staff.objects.filter(mall_id=mall_id).select_related('staff')   
    if request.method == 'POST':
        name = request.POST.get('name')       
        user = request.POST.get('username')       
        passw = request.POST.get('password1')
        email = request.POST.get('email')
        print(user,passw)
        new_user=User.objects.create_user(first_name=name, username=user,password=passw, is_customer=3,is_active=True,email=email, is_staff=True)        
        new_user.save()
        
        mall= User.objects.get(id=mall_id)
        
        s=Staff.objects.create(staff=new_user,mall=mall)
        s.save()
        
        
        
        # messages.success(request, f'Successfully Created')
        # return redirect('SignIn')
        return HttpResponse("<script>window.alert('Successfully Created !');window.location.href='/adminApp/addSupervisor/'</script>")
    else:
        form = CustomUserCreationForm  ()
    print(data)    
    return render(request, 'admin/addStaff.html', {'form': form,"data":data ,"uname":request.session["uname"]})




def add_locations(request):
    # rates = Rate.objects.all()
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('set_parking_rates')
            return HttpResponse("<script>window.alert('Successfully  Saved!!');window.location.href='/adminApp/view_locations/'</script>")
            
    else:
        form = LocationForm()
    return render(request, 'admin/add_locations.html', {'form': form,"uname":request.session["uname"]})  #, 'rates': rates


def view_locations(request):
    loc = Location.objects.all()
    print(loc)
    return render(request, 'admin/view_locations.html', { 'loc': loc,"uname":request.session["uname"]})

    
def edit_locations(request, pk):
    loc = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=loc)
        if form.is_valid():
            form.save()
            # return redirect('manage_parking_slots')  
            return HttpResponse("<script>window.alert('Successfully  Updated!!');window.location.href='/adminApp/view_locations/'</script>")
    else:
        form = LocationForm(instance=loc)  
    return render(request, 'admin/edit_locations.html', {'form': form,"uname":request.session["uname"]})  #, 'rate': rate


def delete_locations(request, pk):
    loc = get_object_or_404(Location, pk=pk)
    # if request.method == 'POST':
    loc.delete()
    # return redirect('manage_parking_slots')  
    return HttpResponse("<script>window.alert('Successfully  Deleted!!');window.location.href='/adminApp/view_locations/'</script>")


