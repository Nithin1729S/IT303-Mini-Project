from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from mtechMinorEval.forms import ProjectEditForm, StudentEditForm, FacultyEditForm
from users.models import User,Student,Profile,Faculty
from .tasks import log_activity
from django.core.cache import cache

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewProject(request):
    "Add new project"
    if request.method == 'POST':
        form = ProjectEditForm(request.POST,request.FILES)
        if form.is_valid():
            project=form.save()
            log_activity.delay(f"Admin created {project.title} belonging to {project.student.name}")
            cache.clear()
            return redirect('project-allotment')
    else:
        form = ProjectEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/editProject.html', context)
    


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewStudent(request):
    "Add new Student"
    if request.method == 'POST':
        form = StudentEditForm(request.POST,request.FILES)
        if form.is_valid():
            with transaction.atomic():
                name = form.cleaned_data.get('name')  # Use the name from the form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                cgpa=form.cleaned_data.get('cgpa')
                gender=form.cleaned_data.get('gender')
                phone_number=form.cleaned_data.get('phone_number')
                nationality=form.cleaned_data.get('nationality')
                country=form.cleaned_data.get('country')
                fathersName=form.cleaned_data.get('fathersName')
                degree=form.cleaned_data.get('degree')
                mother_tongue=form.cleaned_data.get('mother_tongue')
                aadhaar_number=form.cleaned_data.get('aadhaar_number')
                branch=form.cleaned_data.get('branch')
                date_of_birth=form.cleaned_data.get('date_of_birth')
                date_of_admission=form.cleaned_data.get('date_of_admission')
                address=form.cleaned_data.get('address')
                rollno=form.cleaned_data.get('rollno')
                pincode=form.cleaned_data.get('pincode')
                profile_image=form.cleaned_data.get('profile_image')
                # Create the User object
                user = User.objects.create_user(username=name, email=email, password=password)

                # Create the Profile object
                profile = Profile.objects.create(user=user, email=email, role='student')

                # Create the Student object
                student = Student.objects.create(
                    profile=profile,
                    name=name,  # Use the same name for the Student model
                    email=email,
                    rollno=form.cleaned_data.get('rollno'),
                    cgpa=cgpa,
                    gender=gender,
                    phone_number=phone_number,
                    nationality=nationality,
                    country=country,
                    fathersName=fathersName,
                    degree=degree,
                    mother_tongue=mother_tongue,
                    aadhaar_number=aadhaar_number,
                    branch=branch,
                    date_of_birth=date_of_birth,
                    date_of_admission=date_of_admission,
                    address=address,
                    pincode=pincode,
                    profile_image=profile_image
                )
                log_activity.delay(f"Admin created {student.name}'s entry")
                cache.clear()
                return redirect('student-database')
    else:
        form = StudentEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/addNewStudent.html', context)




@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewFaculty(request):
    "Add new faculty"
    if request.method == 'POST':
        form = FacultyEditForm(request.POST,request.FILES,)
        if form.is_valid():
            with transaction.atomic():
                # Extract fields from the form
                name = form.cleaned_data.get('name')  # Ensure username is included in the form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')  # Assuming password is included in the form
                phone_number = form.cleaned_data.get('phone_number')
                gender = form.cleaned_data.get('gender')
                nationality = form.cleaned_data.get('nationality')
                country = form.cleaned_data.get('country')
                address = form.cleaned_data.get('address')
                date_of_birth = form.cleaned_data.get('date_of_birth')
                profile_image = form.cleaned_data.get('profile_image')
                pincode = form.cleaned_data.get('pincode')
                facultyID = form.cleaned_data.get('facultyID')
                # Ensure username is provided
                if not name:
                    raise ValueError("Username must be provided")

                # Create the User object
                user = User.objects.create_user(username=name, email=email, password=password)
                
                # Create the Profile object
                profile = Profile.objects.create(user=user, email=email, role='faculty')

                # Create the Faculty object
                faculty = Faculty.objects.create(
                    profile=profile,
                    name=form.cleaned_data.get('name'),
                    email=email,
                    facultyID=form.cleaned_data.get('facultyID'),
                    phone_number=phone_number,
                    gender=gender,
                    nationality=nationality,
                    country=country,
                    address=address,
                    date_of_birth=date_of_birth,
                    profile_image=profile_image,
                    pincode=pincode,
                )
                log_activity.delay(f"Admin created {faculty.name}'s entry")
                cache.clear()
                return redirect('faculty-database')
    else:
        form = FacultyEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/addNewFaculty.html', context)

