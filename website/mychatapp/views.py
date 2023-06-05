from django.shortcuts import render, redirect
from .models import Message, Profile, Friend , Image
from .forms import MessageForm , ImageForm
from django.http import JsonResponse
import json
import tensorflow as tf
import numpy as np
import pandas as pd

from tensorflow.keras.layers import TextVectorization

# Loading tensorflow model and preprocessing data
model = tf.keras.models.load_model('../model_comment_toxicity_2.h5', compile=False)

df = pd.read_csv('../comment_toxicity_train.csv')
X = df['comment_text']
y = df[df.columns[2:]].values
MAX_FEATURES = 200000
vectorizer = TextVectorization(max_tokens=MAX_FEATURES, output_sequence_length=1800, output_mode='int')
vectorizer.adapt(X.values)



# Create your views here.


#home
def index(request):
    user = request.user.profile
    friends = user.friends.all()
    form = MessageForm()
    context = {"user": user, "friends": friends , "form":form}
    return render(request, "mychatapp/index.html", context)



#chatting

def detail(request,pk):
    friend = Friend.objects.get(friend_profile_id=pk)
    user = request.user.profile
    profile = Profile.objects.get(id=friend.friend_profile.id)
    chats = Message.objects.all()
    rec_chats = Message.objects.filter(msg_sender = profile , msg_reciver = user)
    rec_chats.update(seen=True)
    form = MessageForm()

    if request.method == "POST":
        img=ImageForm(data=request.POST,files=request.FILES)
        if img.is_valid():
            image = img.save(commit=False)
            image.img_sender = user
            image.img_reciver = profile
            image.save()
            
            obj=img.instance
            context = {"friend": friend, "form": form, "user":user, 
                "profile":profile, "chats": chats , "num":rec_chats.count() , "form_img":img , "obj":obj }
            return render(request, "mychatapp/detail.html", context)
    else:
        img=ImageForm()
        image = '0'
    img_all=Image.objects.all()
    context = {"friend": friend, "form": form, "user":user, 
                "profile":profile, "chats": chats , "num":rec_chats.count() , "form_img":img , "img_all":img_all}
    return render(request, "mychatapp/detail.html", context)



#adding_friends

def friends(request):
    user = request.user.profile
    #all_friends = user.friends.all()
    users = Profile.objects.all()
    arr = []
    #for friend in all_friends:
     #   if friend not in users:
      #      arr.append(friend)
    form = MessageForm()
    context = {"user": user, "form":form , "friends":users }
    return render(request, "mychatapp/friends.html" , context)



#saving,sending and recieving msg

def sentMessages(request ,pk):
    is_toxicity = False
    friend = Friend.objects.get(friend_profile_id=pk)
    user = request.user.profile
    profile = Profile.objects.get(id=friend.friend_profile.id)
    data = json.loads(request.body)
    new_chat = data["msg"]
    

    # Model prediction   
    input_str = vectorizer(new_chat)
    res = model.predict(np.expand_dims(input_str, 0))
    is_toxicity_arr = [type_toxicity for type_toxicity in res[0] if type_toxicity > TOXICITY_FLAG]
    is_toxicity = True if len(is_toxicity_arr) > 0 else False
    print(is_toxicity)
    # If is_toxicity, then don't send this message
    if is_toxicity == False:
        new_chat_message = Message.objects.create(body = new_chat , msg_sender = user , msg_reciver = profile , seen=False) 
        return JsonResponse(new_chat_message.body , safe=False)
    else : return JsonResponse()


def recivedMessages( request , pk ):
    arr = []
    friend = Friend.objects.get(friend_profile_id=pk)
    user = request.user.profile
    profile = Profile.objects.get(id=friend.friend_profile.id)
    chats = Message.objects.filter(msg_sender = profile , msg_reciver = user)
    for chat in chats:
        arr.append(chat.body) 
    return JsonResponse(arr , safe=False)


def chatNotification(request):
    user = request.user.profile
    friends = user.friends.all()
    arr = []
    for friend in friends:
        chats = Message.objects.filter(msg_sender__id=friend.friend_profile.id, msg_reciver=user, seen=False)
        arr.append(chats.count())
    return JsonResponse(arr, safe=False)