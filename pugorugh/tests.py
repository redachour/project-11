from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token

from . import models
from . import serializers


DOG1 = {"name": "Francesca",
        "image_filename": "1.jpg",
        "breed": "Labrador",
        "age": 72,
        "gender": "f",
        "size": "l"}

DOG2 = {"name": "Hank",
        "image_filename": "2.jpg",
        "breed": "French Bulldog",
        "age": 14,
        "gender": "m",
        "size": "s"}

USER = {'username': 'username',
        'password': 'password'}


class TestSetUp(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = get_user_model().objects.create(**USER)
        self.test_dog1 = models.Dog.objects.create(**DOG1)
        self.test_dog2 = models.Dog.objects.create(**DOG2)
        self.token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def tearDown(self):
        self.test_user.delete()
        self.test_dog1.delete()
        self.test_dog2.delete()


# Model Tests
class DogModelTestCase(TestCase):
    def test_create_dog(self):
        dog = models.Dog.objects.create(**DOG1)
        self.assertEqual(dog.name, 'Francesca')
        self.assertEqual(dog.size, 'l')


class DogUserModelTestCase(TestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create(**USER)
        self.test_dog = models.Dog.objects.create(**DOG2)

    def tearDown(self):
        self.test_user.delete()
        self.test_dog.delete()

    def test_user_dog(self):
        user_dog = models.UserDog.objects.create(
            user=self.test_user,
            dog=self.test_dog,
            status='l'
        )
        self.assertEqual('username', user_dog.user.username)
        self.assertEqual('l', user_dog.status)
        self.assertEqual('French Bulldog', user_dog.dog.breed)


class UserPrefModelTestCase(TestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create(**USER)

    def tearDown(self):
        self.test_user.delete()

    def test_user_pref(self):
        user_pref = models.UserPref.objects.get(user=self.test_user)
        self.assertEqual(user_pref.user.username, 'username')
        self.assertIn('m', user_pref.gender)
        self.assertIn('l', user_pref.size)
        self.assertIn('a', user_pref.age)


# view tests
class DogViewSetTestCase(TestSetUp):
    def test_dog_list(self):
        resp = self.client.get('/api/dog/1/')
        self.assertEqual(resp.status_code, 200)

    def test_liked_dog_put(self):
        resp = self.client.put('/api/dog/1/liked/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'l')

    def test_disliked_dog_put(self):
        resp = self.client.put('/api/dog/1/disliked/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'd')

    def test_undecided_dog_put(self):
        resp = self.client.put('/api/dog/1/undecided/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], '')

    def test_get_next_liked_dog(self):
        self.client.put('/api/dog/1/liked/')
        resp = self.client.get('/api/dog/1/liked/next/')
        self.assertEqual(resp.status_code, 200)

    def test_get_next_disliked_dog(self):
        self.client.put('/api/dog/1/disliked/')
        resp = self.client.get('/api/dog/1/disliked/next/')
        self.assertEqual(resp.status_code, 200)

    def test_get_next_undecided_dog(self):
        resp = self.client.get('/api/dog/1/undecided/next/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], 2)

    def test_get_next_undecided_dog_exceed_max_pk(self):
        resp = self.client.get('/api/dog/3/undecided/next/')
        data = resp.data
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['id'], 1)

    def test_put_sterilized_true(self):
        resp = self.client.put('/api/dog/1/sterilized/true/')
        data = resp.data
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['sterilized'], True)

    def test_delete_dog(self):
        resp = self.client.delete('/api/dog/1/')
        self.assertEqual(resp.status_code, 204)

    def test_create_dog(self):
        resp = self.client.post('/api/dog/', {"name": "Muffin",
                                              "image_filename": "3.jpg",
                                              "breed": "Boxer",
                                              "age": 24,
                                              "gender": "f",
                                              "size": "xl"})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['name'], 'Muffin')

    def test_update_dog(self):
        resp = self.client.patch('/api/dog/1/', {'name': 'Bjorn'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], 'Bjorn')


class UserPrefViewSetTestCase(TestSetUp):
    def test_userpref_get(self):
        resp = self.client.get('/api/user/preferences/')
        self.test_userpref = models.UserPref.objects.get(user=self.test_user)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['gender'], self.test_userpref.gender)

    def test_userpref_put(self):
        resp = self.client.put('/api/user/preferences/',
                               {'age': "b,a,s", 'gender': 'm', 'size': "l,xl"}
                               )
        self.test_userpref = models.UserPref.objects.get(user=self.test_user)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['age'], self.test_userpref.age)


# Serializer Tests
class DogSerializerTest(TestCase):
    def setUp(self):
        self.test_dog = models.Dog.objects.create(**DOG1)
        self.serializer = serializers.DogSerializer(self.test_dog)

    def tearDown(self):
        self.test_dog.delete()

    def test_dog_serializer(self):
        data = self.serializer.data
        self.assertEqual(data['name'], DOG1['name'])
        self.assertEqual(data['gender'], 'f')


class UserDogSerilizerTest(TestCase):
    def setUp(self):
        self.test_user = models.User.objects.create(**USER)
        self.test_dog = models.Dog.objects.create(**DOG1)
        self.user_dog = models.UserDog.objects.create(
            user=self.test_user,
            dog=self.test_dog,
            status='d')
        self.serializer = serializers.UserDogSerializer(self.user_dog)

    def tearDown(self):
        self.test_dog.delete()
        self.test_user.delete()
        self.user_dog.delete()

    def test_userdog_serializer(self):
        data = self.serializer.data
        self.assertEqual(data['status'], 'd')
        self.assertCountEqual(data.keys(), ['status', 'dog'])


class UserPrefSerializerTest(TestCase):
    def setUp(self):
        self.test_user = models.User.objects.create(**USER)
        self.user_pref = models.UserPref.objects.get(user=self.test_user)
        self.serialize = serializers.UserPrefSerializer(self.user_pref)

    def tearDown(self):
        self.test_user.delete()
        self.user_pref.delete()

    def test_userpref_serializer(self):
        data = self.serialize.data
        self.assertEqual(data['age'], 'b,y,a,s')
        self.assertEqual(data['gender'], 'm,f')
        self.assertCountEqual(data.keys(), ['id', 'age', 'gender', 'size'])
