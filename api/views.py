from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.conf import settings
import requests
from .models import UserMovie
from .serializers import UserSerializer, UserMovieSerializer

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_tmdb_session():
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    return session


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class WatchLaterListView(generics.ListAPIView):
    serializer_class = UserMovieSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserMovie.objects.filter(user=self.request.user, status='WATCH_LATER').order_by('-added_at')

class WatchedListView(generics.ListAPIView):
    serializer_class = UserMovieSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserMovie.objects.filter(user=self.request.user, status='WATCHED').order_by('-added_at')

class MovieStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        movie_id = request.data.get('movie_id')
        new_status = request.data.get('status')
        title = request.data.get('title')
        poster_path = request.data.get('poster_path', '')

        if not movie_id or not new_status:
            return Response({'error': 'movie_id and status are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in ['WATCH_LATER', 'WATCHED', 'NONE']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            movie = UserMovie.objects.get(user=request.user, movie_id=movie_id)
            if new_status == 'NONE':
                movie.delete()
                return Response({'message': 'Removed from lists'}, status=status.HTTP_200_OK)
            else:
                movie.status = new_status
                if title:
                    movie.title = title
                if poster_path:
                    movie.poster_path = poster_path
                movie.save()
                return Response(UserMovieSerializer(movie).data, status=status.HTTP_200_OK)
        except UserMovie.DoesNotExist:
            if new_status == 'NONE':
                return Response({'error': 'Movie not found in lists'}, status=status.HTTP_404_NOT_FOUND)
            
            if not title:
                return Response({'error': 'title is required for new movie'}, status=status.HTTP_400_BAD_REQUEST)

            movie = UserMovie.objects.create(
                user=request.user,
                movie_id=movie_id,
                title=title,
                poster_path=poster_path,
                status=new_status
            )
            return Response(UserMovieSerializer(movie).data, status=status.HTTP_201_CREATED)

class TMDBTrendingView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request):
        api_key = settings.TMDB_API_KEY

        try:
            session = get_tmdb_session()
            response = session.get(
                "https://api.themoviedb.org/3/trending/movie/day",
                params={"api_key": api_key},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )

            response.raise_for_status()
            return Response(response.json())

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class TMDBSearchView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request):
        api_key = settings.TMDB_API_KEY
        query = request.query_params.get('query', '')

        if not query:
            return Response({'error': 'Search query is required'}, status=400)

        try:
            session = get_tmdb_session()
            response = session.get(
                "https://api.themoviedb.org/3/search/movie",
                params={
                    "api_key": api_key,
                    "query": query
                },
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )

            response.raise_for_status()
            return Response(response.json())

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class TMDBMovieDetailsView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request, movie_id):
        api_key = settings.TMDB_API_KEY

        try:
            session = get_tmdb_session()
            response = session.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}",
                params={
                    "api_key": api_key,
                    "append_to_response": "credits,videos"
                },
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )

            response.raise_for_status()
            return Response(response.json())

        except Exception as e:
            return Response({"error": str(e)}, status=500)