from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from mtechMinorEval.models import Project
from users.models import Student,Faculty
from .tasks import log_activity
from django.core.cache import cache

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def deleteProject(request,pk):
    "Delete a particular project"
    project=Project.objects.get(id=pk)
    context={
        'project':project
    }
    if(request.method=='POST'):
        project.delete()
        log_activity.delay(f"Admin deleted {project.student.name}'s project {project.title}")
        cache.clear()
        return redirect('project-allotment')
    return render(request,'mtechMinorEval/delete.html',context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def deleteStudent(request,pk):
    "Delete a particular student"
    student=Student.objects.get(id=pk)
    profile=student.profile
    user=profile.user
    context={
        'student': student
    }
    with transaction.atomic():
        if(request.method=='POST'):
            student.delete()
            profile.delete()
            user.delete()
            log_activity.delay(f"Admin deleted {student.name}'s entry")
            cache.clear()
            return redirect('student-database')
    return render(request,'mtechMinorEval/delete.html',context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def deleteFaculty(request,pk):
    "Delete a particular faculty"
    faculty=Faculty.objects.get(id=pk)
    profile=faculty.profile
    user=profile.user
    context={
        'faculty': faculty
    }
    with transaction.atomic():
        if(request.method=='POST'):
            faculty.delete()
            profile.delete()
            user.delete()
            log_activity.delay(f"Admin deleted {faculty.name}'s entry")
            cache.clear()
            return redirect('faculty-database')
    return render(request,'mtechMinorEval/delete.html',context)
