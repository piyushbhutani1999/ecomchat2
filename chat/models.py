from django.db import models

# Create your models here.
from datetime import datetime
from accounts.models import User
from product.models import Product

class Dialog(models.Model):
    user1 = models.ForeignKey(User, verbose_name=("Dialog owner"), related_name="selfDialogs",
                              on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, verbose_name=("Dialog opponent"), on_delete=models.CASCADE)
    date_of_dialog = models.DateTimeField(default=datetime.now, blank=True, null = True)
    slug_of_product = models.ForeignKey(Product,on_delete=models.CASCADE, default= 'bat',null=True, blank=True )

    def get_opp_name(self , user_obj):
        if user_obj ==self.user1:
            return self.user2
        else:
            return self.user1


class Message(models.Model):
    dialogbox = models.ForeignKey(Dialog, verbose_name=("Dialog"), related_name="messages", on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now, blank=True, null = True)
    content = models.TextField(max_length = 300)
    author = models.ForeignKey(User,on_delete = models.CASCADE)

    def __str__(self):
        return self.content
