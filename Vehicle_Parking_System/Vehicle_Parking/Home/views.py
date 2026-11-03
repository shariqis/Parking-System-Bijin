from django.shortcuts import render,redirect
from Home.forms import CustomUserCreationForm  
from Admin.models import User,Location,Mall,Customer
from django.contrib import messages
# Create your views here.
from django.contrib.auth import authenticate,login,logout
from django.http.response import HttpResponse



def about(request):
   
    return render(request,'home/about.html')

def service(request):
   
    return render(request,'home/service.html')



def register(request):
    if request.method == 'POST':
        user = request.POST.get('username')       
        passw = request.POST.get('password1')
        email = request.POST.get('email')
        print(user,passw)
        if User.objects.filter(username=user).exists():
            return HttpResponse("<script>window.alert('Username already exists. Choose a different one!');window.location.href='/register/'</script>")
        else:
            new_user=User.objects.create_user( username=user,password=passw, is_customer=1,is_active=False,email=email)        
            new_user.save()
            
            cust= Customer.objects.create(user=new_user)
            cust.save()
            
            messages.success(request, f'Your account has been created! PLz wait for the Approvel')
            # return redirect('SignIn')
            return HttpResponse("<script>window.alert('Your account has been created! PLZ wait for the Approval!');window.location.href='/'</script>")
    else:
        form = CustomUserCreationForm  ()
    return render(request, 'home/register.html', {'form': form})




def SignIn_User(request):
    
    if request.method == 'GET':
        context = {}
        context['form'] = ''
        return render(request,'home/login_user.html',context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = authenticate(username=username, password=password)
        # print(user,'///////////',user.is_customer)
        if user is not None:
            login(request,user)
            request.session["uname"] =user.first_name +" " +user.last_name
            print(user.first_name +" " +user.last_name)
            
            if user.is_superuser:
                return redirect("adminhome")
            else:
                if user.is_customer == 1: # user
                    if user.is_active==1:
                        request.session["user_id"]=user.id      
                        request.session["uname"] =user.first_name +" " +user.last_name                 
                        return redirect("userhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 2: # mall
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["mall_id"]=user.id                        
                        return redirect("Mallhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 3: # staff
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["staff_id"]=user.id                        
                        return redirect("Supervisorhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                # elif user.usertype == "teacher": # Teacher
                #         login(request,user)
                #         request.session['teach_id']=user.id                         
                #         return redirect("teacherhome")
                # elif user.usertype == "Exam_Controller": # Exam_Controller
                #         login(request,user)
                #         request.session['Exam_Controller_id']=user.id                         
                #         return redirect("examControllerhome")
                # elif user.usertype == "Office_Staff": # Office_Staff
                #         login(request,user)
                #         request.session['Office_Staff_id']=user.id                         
                #         return redirect("staffhome")
                else:
                    print('................')
                    return HttpResponse("<script>window.alert('Invalid!');window.location.href='/'</script>")
               
        else:
            return HttpResponse("<script>window.alert('Invalid Credentials Or Approval!');window.location.href='/'</script>")
        
   
    return render(request,'home/login_user.html')




# Mall

def SignIn_Mall(request):
    
    if request.method == 'GET':
        context = {}
        context['form'] = ''
        return render(request,'home/login_Mall.html',context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = authenticate(username=username, password=password)
        # print(user,'///////////',user.is_customer)
        if user is not None:
            login(request,user)
            request.session["uname"] =user.first_name +" " +user.last_name
            print(user.first_name +" " +user.last_name)
            
            if user.is_superuser:
                return redirect("adminhome")
            else:
                if user.is_customer == 1: # user
                    if user.is_active==1:
                        request.session["user_id"]=user.id      
                        request.session["uname"] =user.first_name +" " +user.last_name                 
                        return redirect("userhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 2: # mall
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["mall_id"]=user.id                        
                        return redirect("Mallhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 3: # staff
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["staff_id"]=user.id                        
                        return redirect("Supervisorhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                # elif user.usertype == "teacher": # Teacher
                #         login(request,user)
                #         request.session['teach_id']=user.id                         
                #         return redirect("teacherhome")
                # elif user.usertype == "Exam_Controller": # Exam_Controller
                #         login(request,user)
                #         request.session['Exam_Controller_id']=user.id                         
                #         return redirect("examControllerhome")
                # elif user.usertype == "Office_Staff": # Office_Staff
                #         login(request,user)
                #         request.session['Office_Staff_id']=user.id                         
                #         return redirect("staffhome")
                else:
                    print('................')
                    return HttpResponse("<script>window.alert('Invalid!');window.location.href='/'</script>")
               
        else:
            return HttpResponse("<script>window.alert('Invalid Credentials Or Approval!');window.location.href='/'</script>")
        
   
    return render(request,'Home/login_Mall.html')



# Supervisor

def SignIn_Supervisor(request):
    
    if request.method == 'GET':
        context = {}
        context['form'] = ''
        return render(request,'home/login_Supervisor.html',context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = authenticate(username=username, password=password)
        # print(user,'///////////',user.is_customer)
        if user is not None:
            login(request,user)
            request.session["uname"] =user.first_name +" " +user.last_name
            print(user.first_name +" " +user.last_name)
            
            if user.is_superuser:
                return redirect("adminhome")
            else:
                if user.is_customer == 1: # user
                    if user.is_active==1:
                        request.session["user_id"]=user.id      
                        request.session["uname"] =user.first_name +" " +user.last_name                 
                        return redirect("userhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 2: # mall
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["mall_id"]=user.id                        
                        return redirect("Mallhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 3: # staff
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["staff_id"]=user.id                        
                        return redirect("Supervisorhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                # elif user.usertype == "teacher": # Teacher
                #         login(request,user)
                #         request.session['teach_id']=user.id                         
                #         return redirect("teacherhome")
                # elif user.usertype == "Exam_Controller": # Exam_Controller
                #         login(request,user)
                #         request.session['Exam_Controller_id']=user.id                         
                #         return redirect("examControllerhome")
                # elif user.usertype == "Office_Staff": # Office_Staff
                #         login(request,user)
                #         request.session['Office_Staff_id']=user.id                         
                #         return redirect("staffhome")
                else:
                    print('................')
                    return HttpResponse("<script>window.alert('Invalid!');window.location.href='/'</script>")
               
        else:
            return HttpResponse("<script>window.alert('Invalid Credentials Or Approval!');window.location.href='/'</script>")
        
   
    return render(request,'home/login_Supervisor.html')


#Admin

def SignIn_Admin(request):
    
    if request.method == 'GET':
        context = {}
        context['form'] = ''
        return render(request,'home/login_admin.html',context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = authenticate(username=username, password=password)
        # print(user,'///////////',user.is_customer)
        if user is not None:
            login(request,user)
            request.session["uname"] =user.first_name +" " +user.last_name
            print(user.first_name +" " +user.last_name)
            
            if user.is_superuser:
                return redirect("adminhome")
            else:
                if user.is_customer == 1: # user
                    if user.is_active==1:
                        request.session["user_id"]=user.id      
                        request.session["uname"] =user.first_name +" " +user.last_name                 
                        return redirect("userhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 2: # mall
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["mall_id"]=user.id                        
                        return redirect("Mallhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                elif user.is_customer == 3: # staff
                    print("/////////////////////////////")
                    if user.is_active==1:
                        request.session["staff_id"]=user.id                        
                        return redirect("Supervisorhome")
                    else:
                        return HttpResponse("<script>window.alert('User is no Yet Varified!');window.location.href='/'</script>")
                # elif user.usertype == "teacher": # Teacher
                #         login(request,user)
                #         request.session['teach_id']=user.id                         
                #         return redirect("teacherhome")
                # elif user.usertype == "Exam_Controller": # Exam_Controller
                #         login(request,user)
                #         request.session['Exam_Controller_id']=user.id                         
                #         return redirect("examControllerhome")
                # elif user.usertype == "Office_Staff": # Office_Staff
                #         login(request,user)
                #         request.session['Office_Staff_id']=user.id                         
                #         return redirect("staffhome")
                else:
                    print('................')
                    return HttpResponse("<script>window.alert('Invalid!');window.location.href='/'</script>")
               
        else:
            return HttpResponse("<script>window.alert('Invalid Credentials Or Approval!');window.location.href='/'</script>")
        
   
    return render(request,'Home/login_admin.html')









def accounts_logout(request):
    logout(request)
    return redirect('about')  



def Mall_register(request):
    if request.method == 'POST':
        user = request.POST.get('username')       
        passw = request.POST.get('password1')
        email = request.POST.get('email')
        loc = request.POST.get('loc')
        locid= Location.objects.get(id=loc)
        fname = request.POST.get('fname')
        # lat = request.POST.get('latitude')
        # lon = request.POST.get('longitude')
        print(user,passw)
        new_user=User.objects.create_user( username=user,password=passw, is_customer=2,is_active=False,email=email, first_name=fname)        
        new_user.save()
        
        mall= Mall.objects.create(mall=new_user,loc_id=locid)  #,lat=lat,lon=lon
        mall.save()
        
        messages.success(request, f'Your account has been created! Please wait for the Approvel')
        # return redirect('SignIn')
        return HttpResponse("<script>window.alert('Your account has been created! Please wait for the Approval!');window.location.href='/'</script>")
    else:
        # form = CustomUserCreationForm  ()
        loc = Location.objects.all()
        
        return render(request, 'home/Mall_register.html',{"loc":loc})    