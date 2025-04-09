from django.shortcuts import render, redirect
from django.db.models import Sum
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
import random
from .models import AddProduct, Carts, Contact, Signup, Wishlists, Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from validate_email import validate_email
from django.contrib.auth.password_validation import validate_password


def index(request):
    return render(request, "index.html")


def contact(request):
    if request.method == "POST":
        try:
            name = request.POST["name"]
            phone = request.POST["phonenumber"]
            email = request.POST["email"]
            message = request.POST["message"]
            
            if not name:
                raise ValueError("Name field is required")
            elif not validate_email(email):
                raise ValueError("Email is not valid")
            elif not message:
                raise ValueError("Message field is required")

            Contact.objects.create(
                name=name,
                phonenumber=phone,
                email=email,
                message=message,
            )

            message = "Contact saved successfully."
            return render(request, "contact.html", {"message": message})

        except ValueError as e:
            message = str(e)
            return render(request, "contact.html", {"message": message})

    else:
        return render(request, "contact.html")


def signIn(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email:
            message = 'Email is required'
            return render(request, 'signIn.html', {'message': message})
        if not password:
            message = 'Password is required'
            return render(request, 'signIn.html', {'message': message})

        try:
            user = Signup.objects.get(email=email)

            if user.password != password:
                message = 'Incorrect password'
                return render(request, 'signIn.html', {'message': message})

            request.session['usertype'] = user.usertype
            request.session['email'] = user.email
            request.session['name'] = user.name

            if user.usertype == 'customer':
                wishlists = Wishlists.objects.filter(user=user)
                request.session['wishlists_count'] = len(wishlists)
                carts = Carts.objects.filter(user=user, status=False)
                request.session['carts_count'] = len(carts)

            return render(request, 'index.html')

        except Signup.DoesNotExist:
            message = 'User does not exist'
            return render(request, 'signIn.html', {'message': message})
    else:
        return render(request, 'signIn.html')


def changepassword(request):
    if request.method == "POST":
        try:
            user = Signup.objects.get(email=request.session['email'])
            old_password = request.POST.get('oldpassword', '').strip()
            new_password = request.POST.get('newpassword', '').strip()
            confirm_new_password = request.POST.get('cnewpassword', '').strip()

            if not old_password:
                raise ValueError("Old password is required")

            if user.password != old_password:
                raise ValueError("Incorrect Old Password.")

            if not new_password:
                raise ValueError("New password is required")

            if len(new_password) < 8:
                raise ValueError(
                    "New Password must be at least 8 characters long")

            if validate_password(new_password):
                raise ValueError(
                    "New Password must contain at least one uppercase letter, one digit, and one symbol.")

            if new_password != confirm_new_password:
                raise ValueError(
                    "New Password and Confirm New Password Does Not Match.")

            # Update user password
            user.password = new_password
            user.save()
            return redirect('logout')
        except (Signup.DoesNotExist, ValueError) as e:
            message = str(e)
            return render(request, 'changepassword.html', {'message': message})
    else:
        return render(request, "changepassword.html")


def logout(request):
    try:
        del request.session["email"]
        del request.session["name"]
        del request.session["usertype"]
        return render(request, "signIn.html")
    except:
        return render(request, "index.html")


def signUp(request):
    if request.method == "POST":
        try:
            Signup.objects.get(email=request.POST["email"])
            message = "Email has already been registered."
            return render(request, "signUp.html", {"message": message})
        except Signup.DoesNotExist:
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()
            cpassword = request.POST.get("cpassword", "").strip()
            phone = request.POST.get("phonenumber", "").strip()
            usertype = request.POST.get("usertype", "").strip()

            try:
                if len(name) < 3:
                    raise ValueError("Name must be at least 3 characters long")
                elif phone and (not phone.isdigit() or len(phone) != 10):
                    raise ValueError("Invalid phone number")
                elif not validate_email(email):
                    raise ValueError("Email is either empty or not valid")
                elif len(password) < 8:
                    raise ValueError(
                        "New Password must be at least 8 characters long")
                elif validate_password(password):
                    raise ValueError(
                        "Passwords must be contain at least one uppercase letter, one digit, and one symbol.")
                elif password != cpassword:
                    raise ValueError("Passwords do not match")
                else:
                    Signup.objects.create(
                        name=name,
                        phonenumber=phone,
                        email=email,
                        password=password,
                        usertype=usertype,
                    )
                    message = "User signed up successfully."
                    return render(request, "signIn.html", {"message": message})
            except ValueError as e:
                return render(request, "signUp.html", {"message": str(e)})
    else:
        return render(request, "signUp.html")


def forgotPassword(request):
    if(request.method == "POST"):
        try:
            message = ""
            email = request.POST['email']
            if Signup.objects.filter(email=email).exists():
                subject = 'OTP for Forgot Password.'
                otp = random.randint(1000, 9999)
                message = 'OTP for Forgot Password is ' + str(otp)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail(subject, message, email_from, recipient_list)
                return render(request, 'otp.html', {'otp': otp, 'email': email})
            else:
                message = "Email Does Not Exist. Please Register Yourself."
                return render(request, "forgotPassword.html", {'message': message})
        except:
            message = "Something went wrong!"
            return render(request, "forgotPassword.html", {'message': message})
    else:
        return render(request, "forgotPassword.html")


def verifyotp(request):
    try:
        otp = request.POST['otp']
        uotp = request.POST['uotp']
        email = request.POST['email']
        user = Signup.objects.get(email=email)
    except KeyError:
        message = "Invalid form data. Please try again."
        return render(request, 'otp.html', {'message': message})
    except Signup.DoesNotExist:
        message = "Email address not found. Please register first."
        return render(request, 'forgotPassword.html', {'message': message})

    if otp == uotp:
        return render(request, 'newpassword.html', {"email": email})
    else:
        message = "Invalid OTP. Please try again."
        return render(request, 'otp.html', {'otp': otp, 'email': email, 'message': message})


def newpassword(request):
    email = request.POST.get('email')
    newpassword = request.POST.get('newpassword')
    cnewpassword = request.POST.get('cnewpassword')

    if not email:
        message = "Email is required."
        return render(request, 'newpassword.html', {'message': message})

    if not newpassword or not cnewpassword:
        message = "New Password and Confirm New Password are required."
        return render(request, 'newpassword.html', {'email': email, 'message': message})

    if len(newpassword) < 8:
        message = "Password must be at least 8 characters long."
        return render(request, 'newpassword.html', {'email': email, 'message': message})

    if not any(char.isdigit() for char in newpassword):
        message = "Password must contain at least one digit."
        return render(request, 'newpassword.html', {'email': email, 'message': message})

    if not any(char.isupper() for char in newpassword):
        message = "Password must contain at least one uppercase letter."
        return render(request, 'newpassword.html', {'email': email, 'message': message})

    if not any(char in '!@#$%^&*()-_+=[]{}\\|;:\'",.<>/?`~' for char in newpassword):
        message = "Password must contain at least one special character."
        return render(request, 'newpassword.html', {'email': email, 'message': message})

    if newpassword != cnewpassword:
        message = "New Password and Confirm New Password do not match."
        return render(request, 'newpassword.html', {'email': email, 'message': message})

    try:
        user = Signup.objects.get(email=email)
        if newpassword == user.password:
            message = "New password should not same as previous."
            return render(request, 'newpassword.html', {'email': email, 'message': message})
        user.password = newpassword
        user.save()
        message = "Password Changed Successfully."
        return render(request, 'signIn.html', {'message': message})
    except Signup.DoesNotExist:
        message = "User does not exist."
        return render(request, 'newpassword.html', {'email': email, 'message': message})
    except Exception as e:
        message = "Error occurred while changing the password: {}".format(
            str(e))
        return render(request, 'newpassword.html', {'email': email, 'message': message})


def addproduct(request):
    if request.method == "POST":
        seller = Signup.objects.filter(
            email=request.session.get('email')).first()
        if not seller:
            message = "Invalid seller."
            return render(request, "addproduct.html", {"message": message})

        producttype = request.POST.get("producttype")
        productname = request.POST.get("productname")
        price = request.POST.get("price")
        description = request.POST.get("description")
        file = request.FILES.get("file")

        if not producttype or not productname or not price or not description or not file:
            message = "All fields are required."
            return render(request, "addproduct.html", {"message": message})

        try:
            price = int(price)
        except ValueError:
            message = "Price should be a valid number."
            return render(request, "addproduct.html", {"message": message})

        product = AddProduct(
            seller=seller,
            producttype=producttype,
            productname=productname,
            price=price,
            description=description,
            file=file
        )

        try:
            product.save()
            message = "Product added successfully."
            return render(request, "addproduct.html", {"message": message})
        except Exception as e:
            message = f"Error adding product: {e}"
            return render(request, "addproduct.html", {"message": message})
    else:
        return render(request, 'addproduct.html')


def viewproducts(request):
    seller = Signup.objects.get(email=request.session['email'])
    products = AddProduct.objects.filter(seller=seller)
    return render(request, 'viewproducts.html', {'products': products})


def editproduct(request, pk):
    product = AddProduct.objects.get(pk=pk)
    if(request.method == "POST"):
        original_details = {
            'producttype': product.producttype,
            'productname': product.productname,
            'price': product.price,
            'description': product.description,
            'file': product.file
        }
        product.producttype = request.POST['producttype']
        product.productname = request.POST['productname']
        product.price = request.POST['price']
        product.description = request.POST['description']
        try:
            product_file = request.FILES['file']
            if product_file:
                product.file = product_file
        except:
            pass

        updated_details = {
            'producttype': product.producttype,
            'productname': product.productname,
            'price': product.price,
            'description': product.description,
            'file': product.file
        }
        if original_details == updated_details:
            message = "You have not changed anything in details."
            return render(request, "editproduct.html", {'product': product, 'message': message})

        product.save()
        message = "Product Updated Successfully."
        return render(request, "editproduct.html", {'product': product, 'message': message})
    else:
        return render(request, "editproduct.html", {'product': product})


def deleteproduct(request, pk):
    product = AddProduct.objects.get(pk=pk)
    product.delete()
    return redirect("viewproducts")


def products(request):
    products = AddProduct.objects.all()
    return render(request, 'products.html', {"products": products})


def details(request, pk):
    try:
        product = AddProduct.objects.get(pk=pk)
    except AddProduct.DoesNotExist:
        return render(request, "details.html", {'message': "Product Not Found"})
    return render(request, "details.html", {'product': product})


def addToWishlists(request, pk):
    product = AddProduct.objects.get(pk=pk)
    user = Signup.objects.get(email=request.session['email'])
    if Wishlists.objects.filter(user=user, product=product).exists():
        wishlists = Wishlists.objects.filter(user=user)
        return render(request, 'wishlists.html', {'wishlists': wishlists, "message": "Product already added to wishlist"})
    else:
        Wishlists.objects.create(
            user=user,
            product=product
        )
        return redirect('wishlists')


def wishlists(request):
    try:
        user = Signup.objects.get(email=request.session['email'])
    except Signup.DoesNotExist:
        message = 'Please sign in to view your wishlists.'
        return render(request, 'signin.html', {'message': message})

    wishlists = Wishlists.objects.filter(user=user)
    request.session['wishlists_count'] = len(wishlists)
    return render(request, 'wishlists.html', {'wishlists': wishlists})


def remove(request, pk):
    try:
        product = AddProduct.objects.get(pk=pk)
        user = Signup.objects.get(email=request.session['email'])
        wishlist = Wishlists.objects.get(user=user, product=product)
        wishlist.delete()
        return redirect('wishlists')
    except (AddProduct.DoesNotExist, Signup.DoesNotExist, Wishlists.DoesNotExist):
        return render(request, 'wishlists.html', {'wishlists': wishlists, 'message': "Invalid request or product does not exist"})
    except Exception as e:
        return render(request, 'wishlists.html', {'wishlists': wishlists, 'message': str(e)})


def removeFromCart(request, pk):
    try:
        product = AddProduct.objects.get(pk=pk)
        user = Signup.objects.get(email=request.session['email'])
        cart = Carts.objects.filter(user=user, product=product, status=False)
        cart.delete()
        return redirect('carts')
    except AddProduct.DoesNotExist:
        return render(request, 'carts.html', {'carts': carts, 'message': 'Product not found'})
    except Signup.DoesNotExist:
        return render(request, 'carts.html', {'carts': carts, 'message': 'User not found'})
    except Exception as e:
        return render(request, 'carts.html', {'carts': carts, 'message': str(e)})


def addToCarts(request, pk):
    product = AddProduct.objects.get(pk=pk)
    user = Signup.objects.get(email=request.session['email'])
    try:
        cart = Carts.objects.get(
            user=user,
            product=product,
            status=False,
            price=product.price,
            totalprice=product.price
        )
        if(cart):
            carts = Carts.objects.filter(user=user, status=False)
            netPrice = 0
            for i in carts:
                netPrice = netPrice+i.totalprice
            return render(request, 'carts.html', {'carts': carts, 'message': 'Product is already available in cart.', 'netPrice': netPrice})
    except Carts.DoesNotExist:
        Carts.objects.create(
            user=user,
            product=product,
            price=product.price,
            totalprice=product.price
        )
    else:
        return redirect('carts')
    return redirect('carts')


def carts(request):
    netPrice = 0
    user = Signup.objects.get(email=request.session['email'])
    carts = Carts.objects.filter(user=user, status=False)
    for i in carts:
        netPrice = netPrice+i.totalprice
    request.session['carts_count'] = len(carts)
    return render(request, 'carts.html', {'carts': carts, 'netPrice': netPrice})


def changeQty(request):
    try:
        cid = request.POST.get('cid')
        productQty = request.POST.get('productQty')
        cart = Carts.objects.get(pk=cid, status=False)
        cart.qty = int(productQty)
        cart.totalprice = int(productQty)*float(cart.price)
        cart.save()
    except (Carts.DoesNotExist, ValueError):
        pass
    return redirect('carts')


def initiate_payment(request):
    try:
        user = Signup.objects.get(email=request.session['email'])
        amount = int(request.POST['amount'])
    except (Signup.DoesNotExist, ValueError):
        return render(request, 'carts.html', context={'error': 'Wrong Account Details or Amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', request.build_absolute_uri(reverse('callback'))),
    )

    paytm_params = dict(params)
    # checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = "checksum"
    transaction.save()
    carts = Carts.objects.filter(user=user)
    for i in carts:
        i.status = True
        i.save()
    carts = Carts.objects.filter(user=user, status=False)
    request.session['carts_count'] = len(carts)
    paytm_params['CHECKSUMHASH'] = "checksum"
    return render(request, 'myorders.html', context=paytm_params)


@csrf_exempt
def callback(request):
    try:
        if request.method == 'POST':
            received_data = dict(request.POST)
            paytm_params = {}
            paytm_checksum = received_data['CHECKSUMHASH'][0]
            for key, value in received_data.items():
                if key == 'CHECKSUMHASH':
                    paytm_checksum = value[0]
                else:
                    paytm_params[key] = str(value[0])
            is_valid_checksum = verify_checksum(
                paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
            if is_valid_checksum:
                received_data['message'] = "Checksum Matched"
            else:
                received_data['message'] = "Checksum Mismatched"
                return render(request, 'callback.html', context=received_data)
            return render(request, 'callback.html', context=received_data)
    except Exception as e:
        print(e)
        return render(request, 'callback.html', context={'message': 'An error occurred'})


def myorders(request):
    try:
        user = Signup.objects.get(email=request.session['email'])
        carts = Carts.objects.select_related('product').filter(user=user, status=True)
    except Signup.DoesNotExist:
        carts = []
    except Carts.DoesNotExist:
        carts = []
    return render(request, 'myorders.html', {'carts': carts})
