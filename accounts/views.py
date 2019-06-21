from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages

from .models import User
from .forms import LoginForm,UserRegisterForm,UserEditForm, UserPasswordEditForm
from django.views.generic import TemplateView
from product.models import Product
from django.contrib import messages
from product.forms import AddProductInfoForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage

class HomePageView(TemplateView):
    template_name = 'home.html'

class AboutUsPageView(TemplateView):
    template_name = 'aboutus.html'


class ContactUsPageView(TemplateView):
    template_name = 'contactus.html'


def login_user(request):
    if request.method == 'POST' :
        form = LoginForm(request.POST)
        print(form)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                print("LOGIN PAGE")
                print(user.active)
                if user.active:
                    login(request, user)
                    storage = messages.get_messages(request)
                    print(storage)
                    print(len(storage._loaded_messages))
                    for _ in storage: 
                        pass
                    print(len(storage._loaded_messages))
                    if len(storage._loaded_messages) == 1: 
                        del storage._loaded_messages[0]
                    print(storage)
                    return redirect('product:home')
                else:
                    messages.error(request, 'Please verify you email address')

            else:
                messages.error(request, 'Incorrect Username or Password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def register_user(request):
    if request.method=='POST':
        form = UserRegisterForm(request.POST)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            password_ = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            college_name = form.cleaned_data['college_name']
            user = User.objects.create_user(email=email, password=password_, first_name=first_name, last_name=last_name , phone=phone, college_name = college_name)
            current_site = get_current_site(request)
            user.save()
            mail_subject = 'Activate your Maroon account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            messages.info(request,'Please confirm your email address to complete the registration')
            return redirect('product:home')
    else:
        form = UserRegisterForm()
    return render(request,'signup.html',{'form':form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        print("TElls that user is active or not")
        print(user.is_active)
        user.active = True
        user.save()
        print(user.active)
        print("ye chala")
        user.is_active = True
        print("ye chala")
        login(request, user)

        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def profile_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return render(request, 'profile.html',{})
    else:
        return redirect('accounts:login')

def update_user_profile(request):
    if request.user.is_authenticated:
        phone = request.user.phone
        first_name = request.user.first_name
        last_name = request.user.last_name
        from2 = UserPasswordEditForm()
        if request.method == 'POST':
            if 'form1_submit' in request.POST:
                form = UserEditForm(request.POST)
                if form.is_valid():
                    user_info = request.user
                    user_info.first_name = form.cleaned_data['first_name']
                    user_info.last_name = form.cleaned_data['last_name']
                    new_phone = form.cleaned_data['phone']
                    if new_phone!=phone:
                        phone_list = User.objects.all()
                        print(phone_list)
                        for x in phone_list:
                            if new_phone == x.phone:
                                messages.error(request, 'Phone Number already exists.')
                                return render(request, 'update.html', {'form': form})
                    request.user.phone = new_phone
                    try:
                        request.user.save()
                    except:
                        return render(request, 'update.html', {'form': form, 'form2':form2})
                    return redirect('accounts:profile')
            else:
                form = UserEditForm(initial={'phone':phone, 'first_name':first_name , 'last_name':last_name})
                form2 = UserPasswordEditForm(request.POST)
                print(form2.is_valid())
                if form2.is_valid():

                    user_info = request.user
                    email = user_info.email
                    user_password = user_info.password
                    old_password = form2.cleaned_data['old_password']
                    success = user_info.check_password(request.POST['old_password'])
                    new_password = form2.cleaned_data['new_password']
                    confirm_password = form2.cleaned_data['confirm_password']
                    if not success:
                            messages.error(request, 'Current Password is not correct.')
                            return render(request, 'update.html', {'form2': form2, 'form':form })
                    if new_password!=confirm_password:
                            messages.error(request, 'Confirm Password doesnot match with New Password')
                            return render(request, 'update.html', {'form2': form2, 'form':form })
                    user_info.set_password(new_password)
                    try:
                        user_info.save()
                        user = authenticate(request, username=email, password=new_password)
                        if user is not None:
                            login(request, user)
                            messages.success(request, 'Password is updated successfully')
                            return redirect('product:home')
                    except:
                        return render(request, 'update.html', {'form': form, 'form2': form2})
                    return redirect('accounts:profile')
                    
        else:
            form = UserEditForm(initial={'phone':phone, 'first_name':first_name , 'last_name':last_name})
            form2 = UserPasswordEditForm()
        return render(request, 'update.html', {'form': form, 'form2': form2 })
    else:
        return redirect('accounts:login')


def my_ads_view(request):
    if request.user.is_authenticated:
        instance = Product.objects.filter(seller_id = request.user.pk)
        context = {
            'query_set' : instance
        }
        return render(request,"my_ads.html",context )
    else:
        return redirect('accounts:login')


def edit_product(request,slug):
    if request.user.is_authenticated:
        obj = Product.objects.filter(slug = slug , seller_id = request.user.pk)
        if obj.count()==1:
            obj = obj.first()
            title = obj.title
            description = obj.description
            price = obj.price
            image = obj.image
            category = obj.category
            if request.method =='POST':
                form = AddProductInfoForm(request.POST ,request.FILES)
                if form.is_valid():
                    product_info=form.save(commit=False)
                    new_price = form.cleaned_data['price']
                    new_title = form.cleaned_data['title']
                    new_description = form.cleaned_data['description']
                    new_image = form.cleaned_data['image']
                    new_category = form.cleaned_data['category']
                    obj.title = new_title
                    obj.price = new_price
                    obj.description = new_description
                    obj.image = new_image
                    obj.category = new_category
                    try: 
                        obj.save()
                    except:
                        return render(request, 'update_ad.html', {'form': form})
                    return redirect('product:home')
            
            else:
                form = AddProductInfoForm(initial={'title':title, 'description':description , 'category':category,'price':price, 'image':image})

            return render(request, 'update_ad.html', {'form': form})
        else:
            raise ValueError("The product is not associated to the authenticated user")

    else:
        return redirect('accounts:login')

def logout_view(request):
    logout(request)
    return redirect('product:home')

def delete_user(request):
    user_obj = User.objects.filter(email = request.user.email)[0]
    user_obj.delete()
    return redirect('product:home')
