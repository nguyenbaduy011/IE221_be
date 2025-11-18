import os
import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db import transaction
from faker import Faker

from authen.models import CustomUser
from subjects.models.category import Category
from subjects.models.subject import Subject
from subjects.models.task import Task
from subjects.models.subject_category import SubjectCategory
from courses.models.course_model import Course
from courses.models.course_subject import CourseSubject
from courses.models.course_supervisor_model import CourseSupervisor
from courses.models.course_category import CourseCategory
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from users.models.user_task import UserTask
from users.models.comment import Comment
from daily_reports.models import DailyReport

fake = Faker()

class CourseSeederService:
    def __init__(self, course, all_trainees, today):
        self.course = course
        self.all_trainees = all_trainees
        self.today = today

    def seed(self):
        print(f"    -> Seeding data for Course: '{self.course.name}'")
        self.seed_course_subjects_and_tasks()
        self.seed_trainees_and_related_data()

    def seed_course_subjects_and_tasks(self):
        all_subjects = list(Subject.objects.all())
        if not all_subjects:
            return
            
        num_subjects = random.randint(6, 12)
        subjects_for_course = random.sample(all_subjects, min(len(all_subjects), num_subjects))

        for index, subject in enumerate(subjects_for_course):
            estimated_days = getattr(subject, 'estimated_time_days', 10)
            if not estimated_days: 
                estimated_days = random.randint(5, 10)
            
            cs_start = self.course.start_date + timedelta(days=index * estimated_days)
            cs_finish = cs_start + timedelta(days=estimated_days - 1)
            
            if self.course.finish_date:
                cs_finish = min(self.course.finish_date, cs_finish)
            if cs_start > cs_finish:
                cs_start = cs_finish

            course_subject = CourseSubject.objects.create(
                course=self.course,
                subject=subject,
                position=index + 1,
                start_date=cs_start,
                finish_date=cs_finish
            )

            original_tasks = Task.objects.filter(
                taskable_type=Task.TaskType.SUBJECT,
                taskable_id=subject.id
            )
            
            for org_task in original_tasks:
                Task.objects.create(
                    name=org_task.name,
                    taskable_type=Task.TaskType.COURSE_SUBJECT,
                    taskable_id=course_subject.id
                )

            for i in range(random.randint(3, 8)):
                Task.objects.create(
                    name=f"{fake.catch_phrase()} {random.randint(1000, 9999)} {i+1}",
                    taskable_type=Task.TaskType.COURSE_SUBJECT,
                    taskable_id=course_subject.id
                )

    def seed_trainees_and_related_data(self):
        num_trainees = random.randint(20, 30)
        trainees_for_course = random.sample(self.all_trainees, min(len(self.all_trainees), num_trainees))

        for trainee in trainees_for_course:
            if UserCourse.objects.filter(user=trainee, course=self.course).exists():
                continue

            uc_status = UserCourse.Status.NOT_STARTED
            if self.course.status == Course.Status.IN_PROGRESS:
                uc_status = UserCourse.Status.IN_PROGRESS
            elif self.course.status == Course.Status.FINISHED:
                uc_status = UserCourse.Status.FINISH

            user_course = UserCourse.objects.create(
                user=trainee,
                course=self.course,
                status=uc_status,
                joined_at=timezone.make_aware(timezone.datetime.combine(self.course.start_date, timezone.datetime.min.time()))
            )
            
            if uc_status == UserCourse.Status.FINISH:
                user_course.finished_at = timezone.make_aware(timezone.datetime.combine(self.course.finish_date, timezone.datetime.min.time()))
                user_course.save()

            self.create_and_update_user_subjects(user_course)
            self.seed_daily_reports(user_course)

    def create_and_update_user_subjects(self, user_course):
        course_subjects = CourseSubject.objects.filter(course=self.course).order_by('position')

        for cs in course_subjects:
            user_subject, created = UserSubject.objects.get_or_create(
                user=user_course.user,
                subject=cs.subject,
                defaults={'status': UserSubject.Status.NOT_STARTED}
            )

            cs_tasks = Task.objects.filter(
                taskable_type=Task.TaskType.COURSE_SUBJECT,
                taskable_id=cs.id
            )
            
            for task in cs_tasks:
                UserTask.objects.get_or_create(
                    user=user_course.user,
                    task=task,
                    user_subject=user_subject,
                    defaults={'status': UserTask.Status.NOT_DONE}
                )

            self.update_realistic_progress(user_subject, cs, cs_tasks)

    def update_realistic_progress(self, user_subject, cs, cs_tasks):
        status, started_at, completed_at = self.determine_status_and_dates(cs)
        
        score = None
        if status == UserSubject.Status.FINISH:
            score = round(random.uniform(5.0, 10.0), 1)

        user_subject.status = status
        user_subject.score = score
        if started_at:
             user_subject.started_at = timezone.make_aware(timezone.datetime.combine(started_at, timezone.datetime.min.time()))
        if completed_at:
             user_subject.completed_at = timezone.make_aware(timezone.datetime.combine(completed_at, timezone.datetime.min.time()))
        user_subject.save()

        if status == UserSubject.Status.NOT_STARTED:
            return

        if status == UserSubject.Status.FINISH:
             UserTask.objects.filter(user_subject=user_subject).update(status=UserTask.Status.DONE)
        else:
            for ut in UserTask.objects.filter(user_subject=user_subject):
                if random.choice([True, False]):
                    ut.status = UserTask.Status.DONE
                    ut.save()

    def determine_status_and_dates(self, cs):
        if self.course.status == Course.Status.NOT_STARTED or not cs.start_date or self.today < cs.start_date:
            return UserSubject.Status.NOT_STARTED, None, None
        
        started_at = cs.start_date + timedelta(days=random.randint(-1, 1))
        
        rand_val = random.random()
        if rand_val < 0.6:
            target_complete = cs.finish_date - timedelta(days=random.randint(1, 3))
        elif rand_val < 0.9:
            target_complete = cs.finish_date
        else:
            target_complete = cs.finish_date + timedelta(days=random.randint(1, 5))
            
        if self.course.status == Course.Status.FINISHED:
            if random.random() > 0.05:
                return UserSubject.Status.FINISH, started_at, target_complete
            return UserSubject.Status.IN_PROGRESS, started_at, None

        if cs.start_date <= self.today <= cs.finish_date:
            if random.random() < 0.2 and target_complete <= self.today:
                return UserSubject.Status.FINISH, started_at, target_complete
            return UserSubject.Status.IN_PROGRESS, started_at, None
            
        if self.today > cs.finish_date:
             if random.random() < 0.9:
                 return UserSubject.Status.FINISH, started_at, target_complete
             return UserSubject.Status.IN_PROGRESS, started_at, None

        return UserSubject.Status.IN_PROGRESS, started_at, None

    def seed_daily_reports(self, user_course):
        start_day = self.course.start_date
        end_day = min(self.today, self.course.finish_date)
        
        if start_day > end_day:
            return

        delta = end_day - start_day
        for i in range(delta.days + 1):
            day = start_day + timedelta(days=i)
            if day.weekday() >= 5:
                continue
            if random.random() > 0.85:
                continue
            
            status = 1 if random.random() > 0.2 else 0
            
            report_time = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
            
            if not DailyReport.objects.filter(user=user_course.user, course=self.course, created_at__date=day).exists():
                 DailyReport.objects.create(
                    user=user_course.user,
                    course=self.course,
                    content=fake.paragraph(nb_sentences=random.randint(3, 6)),
                    status=status,
                )
                 last = DailyReport.objects.filter(user=user_course.user, course=self.course).latest('created_at')
                 DailyReport.objects.filter(pk=last.pk).update(created_at=report_time, updated_at=report_time)


class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=> Starting seeding process...'))
        
        user_image_path = os.path.join(settings.BASE_DIR, "core", "assets", "default_user_image.png")
        course_image_path = os.path.join(settings.BASE_DIR, "core", "assets", "default_course_image.png")
        
        if not os.path.exists(user_image_path) or not os.path.exists(course_image_path):
             self.stdout.write(self.style.WARNING('!!! WARNING: Image files not found in core/assets/. Seeds will run without images.'))

        with transaction.atomic():
            self.stdout.write("-> Creating Users...")
            self.create_users()
            
            self.supervisors = list(CustomUser.objects.filter(role=CustomUser.Role.SUPERVISOR))
            self.trainees = list(CustomUser.objects.filter(role=CustomUser.Role.TRAINEE))
            
            self.stdout.write("-> Creating Categories and Subjects...")
            self.create_subjects_and_categories(user_image_path)
            
            self.stdout.write("-> Creating Courses and Related Data...")
            self.create_courses(course_image_path)
            
            self.stdout.write("-> Creating Comments...")
            self.create_comments()

        self.stdout.write(self.style.SUCCESS('=> Seeding completed successfully!'))

    def create_users(self):
        for i in range(5):
            email = f"admin-{i+1}@example.com"
            if not CustomUser.objects.filter(email=email).exists():
                CustomUser.objects.create_superuser(
                    email=email,
                    password="password",
                    full_name=f"Admin User {i+1}",
                    role=CustomUser.Role.ADMIN,
                    birthday=date(1990, 1, 1),
                    gender=1
                )
        
        for i in range(5):
            email = f"supervisor-{i+1}@example.com"
            if not CustomUser.objects.filter(email=email).exists():
                CustomUser.objects.create_user(
                    email=email,
                    password="password",
                    full_name=f"Supervisor {i+1}",
                    role=CustomUser.Role.SUPERVISOR,
                    birthday=fake.date_of_birth(minimum_age=28, maximum_age=50),
                    gender=random.choice([0, 1])
                )

        for i in range(20):
            email = f"trainee-{i+1}@example.com"
            if not CustomUser.objects.filter(email=email).exists():
                CustomUser.objects.create_user(
                    email=email,
                    password="password",
                    full_name=fake.name(),
                    role=CustomUser.Role.TRAINEE,
                    birthday=fake.date_of_birth(minimum_age=20, maximum_age=24),
                    gender=random.choice([0, 1])
                )

    def create_subjects_and_categories(self, image_path):
        category_names = [
            "Software Engineering", "Data Science", "Cyber Security", 
            "UI/UX Design", "Digital Marketing", "Business Analysis",
            "Project Management", "Cloud Computing", "Artificial Intelligence",
            "Network Administration", "DevOps", "Mobile Development",
            "Game Design", "Blockchain Basics", "Quality Assurance"
        ]

        categories = []
        for name in category_names:
            cat, _ = Category.objects.get_or_create(name=name)
            categories.append(cat)
            
        for i in range(50):
            name = f"Subject {i+1}: {fake.catch_phrase()}"
            
            defaults = {
                'max_score': 10,
                'estimated_time_days': random.randint(5, 15) 
            }
            
            subject, created = Subject.objects.get_or_create(
                name=name,
                defaults=defaults
            )
            
            if created and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    pass

            selected_cats = random.sample(categories, random.randint(1, 3))
            for idx, cat in enumerate(selected_cats):
                SubjectCategory.objects.get_or_create(
                    subject=subject, 
                    category=cat,
                    defaults={'position': idx}
                )
            
            if created:
                for t_idx in range(random.randint(4, 6)):
                    Task.objects.create(
                        name=f"Task Template: {fake.bs().capitalize()}",
                        taskable_type=Task.TaskType.SUBJECT,
                        taskable_id=subject.id
                    )

    def create_courses(self, image_path):
        today = date.today()
        all_categories = list(Category.objects.all())

        def run_service(course):
            course_sups = random.sample(self.supervisors, random.randint(1, 2))
            for sup in course_sups:
                CourseSupervisor.objects.get_or_create(course=course, supervisor=sup)
            
            service = CourseSeederService(course, self.trainees, today)
            service.seed()

        def create_course_with_image(name, start, finish, status):
            defaults = {
                'creator': random.choice(self.supervisors),
                'start_date': start,
                'finish_date': finish,
                'status': status,
                'link_to_course': f"https://{fake.domain_name()}"
            }
            
            if not Course.objects.filter(name=name).exists():
                course = Course.objects.create(name=name, **defaults)
                
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        course.image.save('course_cover.png', File(f), save=True)
                
                if all_categories:
                    selected_cats = random.sample(all_categories, random.randint(1, 3))
                    for cat in selected_cats:
                        CourseCategory.objects.get_or_create(course=course, category=cat)

                run_service(course)

        for i in range(5):
            c_name = f"Advanced {fake.job()} Bootcamp {2020+i}"
            finish_date = fake.date_between(start_date='-8M', end_date='-1w')
            start_date = finish_date - timedelta(days=random.randint(90, 120))
            create_course_with_image(c_name, start_date, finish_date, Course.Status.FINISHED)

        for i in range(5):
            c_name = f"{fake.catch_phrase().title()} Masterclass"
            start_date = fake.date_between(start_date='-3M', end_date='-2w')
            finish_date = fake.date_between(start_date='+1w', end_date='+4M')
            create_course_with_image(c_name, start_date, finish_date, Course.Status.IN_PROGRESS)

        for i in range(5):
            c_name = f"Intro to {fake.bs().title()} {random.randint(101, 301)}"
            start_date = fake.date_between(start_date='+1w', end_date='+2M')
            finish_date = start_date + timedelta(days=random.randint(90, 120))
            create_course_with_image(c_name, start_date, finish_date, Course.Status.NOT_STARTED)

    def create_comments(self):
        user_subjects = UserSubject.objects.filter(status=UserSubject.Status.FINISH)
        content_type = ContentType.objects.get_for_model(UserSubject)

        for us in user_subjects:
            if random.random() > 0.5: continue

            relevant_course = Course.objects.filter(
                user_courses__user=us.user,
                coursesubject__subject=us.subject
            ).first()

            if not relevant_course:
                continue

            course_sup_link = relevant_course.supervisors.first()
            if not course_sup_link: continue
            
            supervisor_user = course_sup_link.supervisor 

            Comment.objects.create(
                user=supervisor_user,
                content=fake.sentence(),
                content_type=content_type,
                object_id=us.id
            )