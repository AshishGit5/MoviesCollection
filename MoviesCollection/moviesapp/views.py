from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import UserSerializer,MovieSerializer,CollectionSerializer,MoviecollectSerializer,MovieSerializer1
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from .pagination import PaginationsData
import requests
from .o import UrlData
from .models import Movie,Collection
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserRegistrationView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

class MovieApiData(APIView):
    pagination_class = PaginationsData
    def get(self, request):
        serializer = MovieSerializer(UrlData(), many=True)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_data)

@api_view(['POST'])
def CollectionData(request):
    collection_serializer = CollectionSerializer(data=request.data)
    if collection_serializer.is_valid():
        collection = Collection.objects.create(title=collection_serializer.validated_data['title'],description=collection_serializer.validated_data['description'])
        movies_data = collection_serializer.validated_data['movies']
        for movie_data in movies_data:
            movie = Movie.objects.create(title=movie_data['title'],description=movie_data['description'],genres=movie_data['genres'],uuid=movie_data['uuid'])
            collection.movies.set([movie])
        return Response(collection_serializer.data)
    else:
        return Response(collection_serializer.errors)


class CollectionAPIView(generics.RetrieveAPIView):
    def get(self, request):
        collections = Movie.objects.all()
        l=[]
        for collection in collections:
            top3_genres = Movie.objects.filter(genres=collection.genres)
            for i in top3_genres.values():
                for j in i['genres'].split(','):
                    l.append(j)
                print(l)
                b = dict.fromkeys(l,0)
                dic = {}
                for i in b:
                    dic[i] = l.count(i)

                l1 = []
                for j in dic.items():
                    l1.append(j)
                    l1.sort(key= lambda x:x[1],reverse=True)
                    top = dict(l1[0:3])
                top3 = []
                for m in top.keys():
                    top3.append(m)
                    top3_data = ','.join(top3)
                print(top3_data,'----------------------------------')
                data = {
                    'is_success': True,
                    'data': {
                        'collections': [
                            {
                                'id' : collection.id,
                                'title': collection.title,
                                'uuid': collection.uuid,
                                'description': collection.description
                            }
                        ],
                        'favourite_genres': top3_data
                    }
                }
                return Response(data)

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer1
    lookup_field = 'uuid'

    @action(detail=True, methods=['put'])
    def update_movies(self, request, uuid=None):
        collection = self.get_object()
        movies = request.data.get('movies', collection.movies)
        collection.movies = movies
        collection.save()
        serializer = self.get_serializer(collection)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def retrieve_collection(self, request, uuid=None):
        collection = self.get_object()
        serializer = self.get_serializer(collection)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_collection(self, request, uuid=None):
        collection = self.get_object()
        collection.delete()
        return Response({"message": "Collection deleted successfully"})

request_counter = 0
@api_view(['GET'])
def count(request):
    global request_counter
    if request.method == 'GET':
        response_data = {"requests": request_counter}
        return Response(response_data)
    else:
        response_data = {"error": "Unsupported method"}
        return Response(response_data)