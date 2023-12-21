from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from shop.models import Product
from cart.models import Cart,Account,Order
# Create your views here.
def cartview(request):
    sum=0
    u=request.user
    try:
        cart=Cart.objects.filter(user=u)
    except:
        pass

    for i in cart:
        sum+=i.quantity*i.product.price

    return render(request,'addtocart.html',{'c':cart,'sum':sum})




@login_required
def addtocart(request,p):
    product=Product.objects.get(name=p)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=product)
        if(cart.quantity<cart.product.stock):
            cart.quantity+=1
        cart.save()
    except:
        cart=Cart.objects.create(product=product,user=u,quantity=1)
        cart.save()
    return redirect('cart:cartview')


def minuss(request,p):
    product=Product.objects.get(name=p)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=product)
        if(cart.quantity>1):
            cart.quantity-=1
            cart.save()
        else:
            cart.delete()

    except:
        pass
    return redirect('cart:cartview')

def delete(request,p):
    product=Product.objects.get(name=p)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=product)
        cart.delete()
    except:
        pass
    return redirect('cart:cartview')


def orderform(request):
    if (request.method == "POST"):
        a = request.POST['a']
        p = request.POST['p']
        n = request.POST['n']
        u=request.user
        cart=Cart.objects.filter(user=u)

        #total amount calculation
        total=0
        for i in cart:
            total+=i.quantity*i.product.price

        #check accont balance to bye the item in the cart
        ac=Account.objects.get(acctnum=n)
        if(ac.amount>=total):
            ac.amount=ac.amount-total
            ac.save()

            for i in cart:         #for get each cart object
                o=Order.objects.create(user=u,product=i.product,address=a,phone=p,noofitem=i.quantity,order_status="paid")
                o.save()
                i.product.stock=i.product.stock-i.quantity
                i.product.save()
            cart.delete()      #clear the cart
            msg="Order placed Sucessully"
            return render(request,'orderdetail.html',{'m':msg})
        else:
            msg="Insufficient Amount in User Account.You CAnnot place this order"
            return render(request, 'orderdetail.html', {'m': msg})

    return render(request,'orderform.html')


def orderview(request):
    u=request.user
    n=Order.objects.filter(user=u)
    return render(request,'orderview.html',{'n':n,'u':u})