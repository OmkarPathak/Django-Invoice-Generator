# Django-Inventory-Management
A minimal Inventory Management System using Django

## Features

- Easy to use
- A simple GUI
- Faster load speeds (thanks to Django 2.x!)
- Reports for keeping track of payments
- Download invoice PDF
- What is see is waht you get

## Working

![Working](results/django_invoice_generator.gif)

## How to use

- Download the zip
- Extract the contents
- Install all dependencies by executing the following command:

    ```
    $pip install -r inventory_management/requirements.txt
    ```

- For running the application simply execute the following commands:

    ```
    $python3 manage.py migrate
    $python3 manage.py runserver
    ```

- For creating a user execute:

    ```
    $python3 manage.py createsuperuser
    # Follow the instructions
    ```

- You can now login to the system!

- For first time use, visit [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and under `Works` section select `Challan Number`. Then click on add challan number and add 1 in the textbox and click save. Now you can use the app by visiting [http://127.0.0.1:8000/](http://127.0.0.1:8000/)


### Built with ♥ and :coffee: by [`Omkar Pathak`](http://www.omkarpathak.in/)

# Donation

If you have found my softwares to be of any use to you, do consider helping me pay my internet bills. This would encourage me to create many such softwares :)

| PayPal | <a href="https://paypal.me/omkarpathak27" target="_blank"><img src="https://www.paypalobjects.com/webstatic/mktg/logo/AM_mc_vs_dc_ae.jpg" alt="Donate via PayPal!" title="Donate via PayPal!" /></a> |
|:-------------------------------------------:|:-------------------------------------------------------------:|
| ₹ (INR)  | <a href="https://www.instamojo.com/@omkarpathak/" target="_blank"><img src="https://www.soldermall.com/images/pic-online-payment.jpg" alt="Donate via Instamojo" title="Donate via instamojo" /></a> |

