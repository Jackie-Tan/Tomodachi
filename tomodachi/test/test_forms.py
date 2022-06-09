import os
from .. forms import *
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

class TestChangeProfilePictureForm(TestCase):

    def test_no_file_upload(self):
        file_dict = {'profile_image': None}
        form = ChangeProfilePictureForm(files=file_dict)
        self.assertFalse(form.is_valid())

    def test_correct_file_upload(self):
        upload_file = open(os.path.join(settings.MEDIA_ROOT, 'default/profile-pic.png'), 'rb')
        file_dict = {'profile_image': SimpleUploadedFile(upload_file.name, content=upload_file.read(), content_type='image/jpeg')}
        form = ChangeProfilePictureForm(files=file_dict)
        self.assertTrue(form.is_valid())

    def test_incorrect_file_upload(self):
        upload_file = open(os.path.join(settings.MEDIA_ROOT, 'default/default-profile-pic.svg'), 'rb')
        file_dict = {'profile_image': SimpleUploadedFile(upload_file.name, content=upload_file.read(), content_type='image/jpeg')}
        form = ChangeProfilePictureForm(files=file_dict)
        self.assertFalse(form.is_valid())

class TestPostForm(TestCase):

    def test_form_with_correct_data(self):
        data = {'text' : 'random text'}
        form = PostForm(data=data)
        self.assertTrue(form.is_valid())
        
        upload_file = open(os.path.join(settings.MEDIA_ROOT, 'default/profile-pic.png'), 'rb')
        file_dict = {'image': SimpleUploadedFile(upload_file.name, content=upload_file.read(), content_type='image/jpeg')}
        form = PostForm(data=data, files=file_dict)
        self.assertTrue(form.is_valid())

    def test_form_without_text(self):
        data = {'text' : ''}
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'text' : None}
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_with_invalid_fieldname(self):
        data = {'bad_field' : 'text'}
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())