from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse


class ManagerAccessMixin:
    """
    Миксин, который обеспечивает доступ к представлению только для менеджеров
    и администратора.

    Проверка осуществляется по атрибуту is_staff и is_superuser текущего пользователя.
    Если пользователь не является менеджером или администратором,
    происходит перенаправление на главную страницу
    с соответствующим информационным сообщением.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Переопределение метода dispatch для проверки прав доступа.
        Если пользователь не является менеджером или администратором,
        он будет перенаправлен на главную страницу.
        :param request: HttpRequest объект.
        """

        if not (request.user.is_staff or request.user.is_superuser):
            messages.info(request=request, message='У вас нет соответствующих прав доступа!')
            return redirect(reverse('app_main:index'))

        return super().dispatch(request, *args, **kwargs)


class CreatorAccessMixin:
    """
    Миксин, обеспечивающий доступ к редактированию объектов
    только тому пользователю сервиса, который их создал.
    """

    def check_creator_access(self, obj) -> bool:
        """
        Проверяет, имеет ли текущий пользователь доступ
        к редактированию или удалению объекта.
        :param obj: Объект, который нужно проверить.
        """
        return obj.created_by == self.request.user

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Переопределение метода dispatch для проверки доступа пользователя
        перед редактированием или удалением объекта.
        Если пользователь не является создателем объекта,
        он будет перенаправлен на главную страницу.
        :param request: HttpRequest объект.
        """
        obj = self.get_object()

        if not self.check_creator_access(obj=obj):
            message = 'У вас нет разрешения на редактирование и удаление этого объекта'
            messages.info(request=self.request, message=message)
            return redirect(reverse('app_main:index'))

        return super().dispatch(request, *args, **kwargs)


class CombinedAccessMixin:
    """
    Миксин, обеспечивающий доступ к представлению только для создателя, менеджеров
    и администратора.

    Проверка осуществляется по атрибуту is_staff и is_superuser текущего пользователя,
    а также по сравнению создателя объекта с текущим пользователем.
    Если пользователь не является создателем, менеджером или администратором,
    происходит перенаправление на главную страницу
    с соответствующим информационным сообщением.
    """

    def check_access(self, obj) -> bool:
        """
        Проверяет, имеет ли текущий пользователь доступ
        к редактированию или удалению объекта.
        :param obj: Объект, который нужно проверить.
        """
        return obj.created_by == self.request.user or self.request.user.is_staff or self.request.user.is_superuser

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Переопределение метода dispatch для проверки прав доступа.
        Если пользователь не является создателем, менеджером или администратором,
        он будет перенаправлен на главную страницу.
        :param request: HttpRequest объект.
        """

        obj = self.get_object()

        if not self.check_access(obj=obj):
            messages.info(request=request, message='У вас нет соответствующих прав доступа!')
            return redirect(reverse('app_main:index'))

        return super().dispatch(request, *args, **kwargs)


class NewsletterLogAccessMixin:
    """
    Mixin, который проверяет, создал ли текущий пользователь рассылку, связанную с логом.
    Если лог относится к рассылке, которую текущий пользователь не создавал, то
    перенаправит на главную страницу с соответствующим сообщением.
    """

    def dispatch(self, request, *args, **kwargs):
        log = self.get_object()

        if log.newsletter.created_by != self.request.user and \
                not self.request.user.is_staff and \
                not self.request.user.is_superuser:
            messages.info(request=request, message='У вас нет доступа к этому логу!')
            return redirect(reverse('app_main:index'))
        return super().dispatch(request, *args, **kwargs)
