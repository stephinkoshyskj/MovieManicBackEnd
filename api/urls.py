from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, WatchLaterListView, WatchedListView, MovieStatusView, TMDBTrendingView, TMDBSearchView, TMDBMovieDetailsView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('movies/watch-later/', WatchLaterListView.as_view(), name='watch_later'),
    path('movies/watched/', WatchedListView.as_view(), name='watched'),
    path('movies/status/', MovieStatusView.as_view(), name='movie_status'),
    path('tmdb/trending/', TMDBTrendingView.as_view(), name='tmdb_trending'),
    path('tmdb/search/', TMDBSearchView.as_view(), name='tmdb_search'),
    path('tmdb/movie/<int:movie_id>/', TMDBMovieDetailsView.as_view(), name='tmdb_movie_details'),
]
