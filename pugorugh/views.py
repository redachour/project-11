from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from django.db.models import Q

from . import serializers
from . import models


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class UserPrefView(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    @list_route(methods=['get', 'put'])
    def preferences(self, request, pk=None):
        pref = models.UserPref.objects.get(user=request.user)

        if request.method == 'PUT':
            pref.age = request.data.get('age')
            pref.gender = request.data.get('gender')
            pref.size = request.data.get('size')
            pref.save()

        serializer = serializers.UserPrefSerializer(pref)
        return Response(serializer.data)


class DogView(viewsets.ModelViewSet):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    # extra route to change sterilized to true: api/dog/<pk>/sterilized/true/
    @detail_route(methods=['put'], url_path='sterilized/true')
    def sterilized(self, request, pk=None):
        dog = self.get_object()
        dog.sterilized = True
        dog.save()
        serializer = serializers.DogSerializer(dog)
        return Response(serializer.data)

    # api/dog/<pk>/liked|disliked|undecided/
    @detail_route(methods=['put'], url_path="(?P<stat>[^/.]+)")
    def changed(self, request, pk=None, stat=None):
        user = request.user
        models.UserDog.objects.filter(user=user, dog_id=pk).delete()

        if stat == 'liked':
            userdog = models.UserDog.objects.create(user=user, dog_id=pk,
                                                    status='l')
        elif stat == 'disliked':
            userdog = models.UserDog.objects.create(user=user, dog_id=pk,
                                                    status='d')
        else:
            userdog = models.UserDog.objects.create(user=user, dog_id=pk)

        serializer = serializers.UserDogSerializer(userdog)
        return Response(serializer.data)

    # api/dog/<pk>/liked|disliked|undecided/next/
    @detail_route(methods=['get'], url_path="(?P<stat>[^/.]+)/next")
    def liked(self, request, pk=None, stat=None):
        user = request.user
        user_pref = models.UserPref.objects.get(user=user)

        age_range = []
        if 'b' in user_pref.age:
            for i in range(10):
                age_range.append(i)
        if 'y' in user_pref.age:
            for i in range(10, 30):
                age_range.append(i)
        if 'a' in user_pref.age:
            for i in range(30, 60):
                age_range.append(i)
        if 's' in user_pref.age:
            for i in range(60, 200):
                age_range.append(i)

        dogs = models.Dog.objects.filter(Q(gender__in=user_pref.gender),
                                         Q(age__in=age_range),
                                         Q(size__in=user_pref.size))

        if stat == 'liked':
            dog = dogs.filter(Q(id__gt=pk),
                              Q(userdog__status='l'),
                              Q(userdog__user=user.id))
            if not dog:
                dog = dogs.filter(Q(userdog__status='l'),
                                  Q(userdog__user=user.id))
        elif stat == 'disliked':
            dog = dogs.filter(Q(id__gt=pk),
                              Q(userdog__status='d'),
                              Q(userdog__user=user.id))
            if not dog:
                dog = dogs.filter(Q(userdog__status='d'),
                                  Q(userdog__user=user.id))
        else:
            dog = dogs.filter(Q(id__gt=pk), ~Q(userdog__user=user.id))
            if not dog:
                dog = dogs.filter(~Q(userdog__user=user.id))

        if dog:
            serializer = serializers.DogSerializer(dog.first())
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)
