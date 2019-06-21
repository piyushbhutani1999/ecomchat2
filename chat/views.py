from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.shortcuts import render, HttpResponse, Http404, redirect
import json
from product.models import Product

from .models import Dialog, Message
from django.contrib.auth.decorators import login_required
from accounts.models import User
from django.db.models import Q
from django.contrib import messages

def index(request):
    dialog =  Dialog.objects.filter(Q(user1=request.user) | Q(user2 = request.user)).order_by('-date_of_dialog')
    if dialog.count() !=0:
        dialog = dialog.first()
        slug = dialog.slug_of_product
        room_id = dialog.id
        return redirect('chat:room',slug =  slug,room_id = room_id )
    else:
        messages.error(request,  '   No messages to show... Drop messages to chat with seller')
        return render(request,'nochat.html' ,{})

@login_required
def room(request,slug, room_id):
    dialog_obj = Dialog.objects.filter(id = room_id)[0]
    user_obj = request.user
    if request.user.email == dialog_obj.user1.email:
        opponent = dialog_obj.user2
    else:
        opponent = dialog_obj.user1
    dialog_win = Dialog.objects.filter(Q(user1=user_obj) | Q(user2 = user_obj)).order_by('-date_of_dialog')
    message_list = []
    for dialog in dialog_win:
        opp = dialog.get_opp_name(user_obj)
        message = Message.objects.filter(dialogbox = dialog)
        message = message.order_by('-date')
        if message.count():
            message  = message.first()
        else:
            message = "NO CHAT "
        d = dialog.date_of_dialog
        product_title = dialog.slug_of_product.title 
        date_new = d.strftime('%d %b')
        context= {
            'opp':opp,
            'message' :message,
            'date':date_new,
            'slug':dialog.slug_of_product,
            'product_title':product_title,
            'email':str(opp.email),
            'id' : dialog.id
        }
        print("THE EMAILS ARE")
        print(type(opponent.email))
        print(type(opp.email))
        if opponent.email==opp.email:
            print("WE FOUND THAT")
        message_list.append(context)
    if request.user.email == dialog_obj.user1.email:
        opponent = dialog_obj.user2
    else:
        opponent = dialog_obj.user1
    context = {
        'room_id' :room_id,
        'author' : mark_safe(json.dumps(request.user.email)),
        'author_name' :request.user.first_name,
        'opponent':mark_safe(json.dumps(opponent.email)),
        'opponent_name':opponent.first_name,
        'message_list':message_list,
        'slug': slug,
        'opp_email':str(opponent.email),
    }
    print(message_list)
    for message in message_list:
        print("THE ESSAGE IS")
        print(message)
        print(message['opp'])
        print(type((message['opp'].email)))
    return render(request, 'room6.html', context)

@login_required
def create_dialogbox(request, slug):
    query_set = Product.objects.filter(slug = slug)

    if query_set.count()==1:
        query_set = query_set.first()
    else :
        raise HttpResponse("not a valid url")
    user1 = query_set.seller_id
    user2 = request.user
    if user1==user2:
        return redirect('product:home' )
    qs = Dialog.objects.filter((Q(user1 = user1)&Q(user2 = user2)) | (Q(user1 = user2)&Q(user2 = user1)) )
    print(qs)
    if qs.count()==1:
        qs = qs.first()
        room_id = qs.id

    else:
        dialog = Dialog.objects.create(
            user1= user1,
            user2= user2,
            slug_of_product = query_set
        )
        print(dialog)
        room_id = dialog.id
        print("THE DIALOG IS")
        print(dialog)
    return redirect('chat:room',slug = slug,room_id = room_id )

