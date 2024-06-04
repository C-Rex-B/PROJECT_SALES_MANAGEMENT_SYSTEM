# from django.core.exceptions import PermissionDenied

# class AdminRequiredMixin:
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated or not request.user.is_admin:
#             raise PermissionDenied
#         return super().dispatch(request, *args, **kwargs)


# from django.core.exceptions import PermissionDenied

# class AdminRequiredMixin:
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_staff:
#             raise PermissionDenied
#         return super().dispatch(request, *args, **kwargs)



from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        raise PermissionDenied
