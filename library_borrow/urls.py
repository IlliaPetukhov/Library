from rest_framework import routers
from library_borrow.views import (
    BorrowingViewSet,
    PaymentViewSet,
    BookViewSet
)

router = routers.DefaultRouter()
router.register("books", BookViewSet)
router.register("borrowings", BorrowingViewSet)
router.register("payments", PaymentViewSet)
urlpatterns = router.urls
app_name = "library-api-1"
