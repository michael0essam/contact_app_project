from django.shortcuts import render, redirect, get_object_or_404
import logging

import idlelib
from .models import Contact
from .forms import ContactForm
from .github_sync import queue_change, upload_offline_changes, download_changes
from django.contrib import messages
from django.db.models import Q

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            try:
                # Download changes from GitHub
                download_changes()
                logging.info("Changes downloaded successfully during login.")
            except Exception as e:
                logging.error(f"Error downloading changes during login: {e}")

            try:
                # Upload offline changes to GitHub
                upload_offline_changes()
                logging.info("Offline changes uploaded successfully during login.")
            except Exception as e:
                logging.error(f"Error uploading offline changes during login: {e}")

            return redirect('home')  # Redirect to the home page after login
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'contacts/login.html')

# Logout View
@login_required
def logout_view(request):
    try:
        # Upload any remaining offline changes before logging out
        upload_offline_changes()
        logging.info("Offline changes uploaded successfully during logout.")
    except Exception as e:
        logging.error(f"Error uploading offline changes during logout: {e}")
    logout(request)
    return redirect('login')  # Redirect to the login page after logout



@login_required
def home(request):
    # try:
    #     # Ensure the contacts table exists before downloading changes
    #     from django.db import connection
    #     with connection.cursor() as cursor:
    #         cursor.execute("CREATE TABLE IF NOT EXISTS contacts (id BIGINT PRIMARY KEY, name TEXT, company TEXT, card1 TEXT, card2 TEXT, phone TEXT)")
    # except Exception as e:
    #     logging.error(f"Error ensuring table exists: {e}")

    # try:
    #     # Download changes from GitHub
    #     download_changes()
    # except Exception as e:
    #     logging.error(f"Error downloading changes: {e}")
    #     messages.error(request, "Failed to download changes from GitHub.")

    # try:
    #     # Upload offline changes to GitHub
    #     upload_offline_changes()
    # except Exception as e:
    #     logging.error(f"Error uploading offline changes: {e}")
    #     messages.error(request, "Failed to upload offline changes to GitHub.")

    contacts = []  # Initialize an empty list for contacts
    search_performed = False  # Track whether a search was performed

    if request.method == 'POST':
        # Check if the ID search form was submitted
        if 'id' in request.POST:
            id_query = request.POST.get('id', '').strip()
            if id_query:  # Only search if the ID query is not empty
                search_performed = True
                contacts = Contact.objects.filter(id=id_query)
                if not contacts:
                    logging.info(f"No contacts found for ID: {id_query}")
        
        # Check if the Name search form was submitted
        elif 'search_query' in request.POST:
            name_query = request.POST.get('search_query', '').strip()
            if name_query:  # Only search if the name query is not empty
                search_performed = True
                contacts = Contact.objects.filter(
                    Q(name__icontains=name_query) |
                    Q(company__icontains=name_query) |
                    Q(phone__icontains=name_query) |
                    Q(card1__icontains=name_query) |
                    Q(card2__icontains=name_query)
                )
                if not contacts:
                    logging.info(f"No contacts found for query: {name_query}")

    return render(request, 'contacts/home.html', {
        'contacts': contacts,
        'search_performed': search_performed  # Pass the flag to the template
    })


@login_required
def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            queue_change(f"INSERT INTO contacts (id, name, company, card1, card2, phone) VALUES ('{contact.id}', '{contact.name}', '{contact.company}', '{contact.card1}', '{contact.card2}', '{contact.phone}')")
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'contacts/add_contact.html', {'form': form})

def search_by_id(request):
    if request.method == 'POST':
        id = request.POST.get('id', '').strip()
        try:
            contact = Contact.objects.get(id=id)
            return render(request, 'contacts/contact_detail.html', {'contact': contact})
        except Contact.DoesNotExist:
            return render(request, 'contacts/not_found.html', {'message': 'Contact not found'})
    return redirect('home')


@login_required
def update_contact(request, id):  # Change 'pk' to 'id'
    contact = get_object_or_404(Contact, id=id)  # Use 'id=id' since the model's primary key is 'id'
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            queue_change(f"UPDATE contacts SET name='{contact.name}', company='{contact.company}', card1='{contact.card1}', card2='{contact.card2}', phone='{contact.phone}' WHERE id={contact.id}")
            return redirect('home')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contacts/update_contact.html', {'form': form})



@login_required
def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    if request.method == 'POST':
        contact.delete()
        queue_change(f"DELETE FROM contacts WHERE id='{id}'")
        return redirect('home')
    return render(request, 'contacts/delete_contact.html', {'contact': contact})


@login_required
def display_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts/display_contacts.html', {'contacts': contacts})


