from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect

from jet_bridge_base.exceptions.not_found import NotFound
from jet_bridge_base.request import Request
from jet_bridge_base.responses.base import Response
from jet_bridge_base.responses.redirect import RedirectResponse
from jet_bridge_base.status import HTTP_204_NO_CONTENT


class BaseRouteView(generic.View):
    view_cls = None
    view = None

    def prepare(self):
        self.view = self.view_cls()
        self.view.request = Request(
            self.request.method.upper(),
            self.request.scheme,
            self.request._get_raw_host(),
            self.request.path,
            self.kwargs,
            self.request.get_full_path(),
            dict(self.request.GET.lists()),
            self.request.META,
            self.request.body,
            dict(self.request.POST.lists()),
            self.request.FILES.dict()
        )

        self.view.prepare()

    def on_finish(self):
        self.view.on_finish()

    def write_response(self, response):
        if isinstance(response, RedirectResponse):
            return HttpResponseRedirect(response.url, status=response.status)

        result = HttpResponse(response.render(), status=response.status)

        for name, value in self.view.default_headers().items():
            result[name] = value

        for name, value in response.header_items():
            result[name] = value

        return result

    def options(self, request, *args, **kwargs):
        return self.write_response(Response(status=HTTP_204_NO_CONTENT))

    def get(self, *args, **kwargs):
        if not hasattr(self.view, 'get'):
            raise NotFound()
        response = self.view.get(*args, **kwargs)
        return self.write_response(response)

    def post(self, *args, **kwargs):
        if not hasattr(self.view, 'post'):
            raise NotFound()
        response = self.view.post(*args, **kwargs)
        return self.write_response(response)

    def put(self, *args, **kwargs):
        if not hasattr(self.view, 'put'):
            raise NotFound()
        response = self.view.put(*args, **kwargs)
        return self.write_response(response)

    def patch(self, *args, **kwargs):
        if not hasattr(self.view, 'patch'):
            raise NotFound()
        response = self.view.patch(*args, **kwargs)
        return self.write_response(response)

    def delete(self, *args, **kwargs):
        if not hasattr(self.view, 'delete'):
            raise NotFound()
        response = self.view.delete(*args, **kwargs)
        return self.write_response(response)

    def dispatch(self, *args, **kwargs):
        self.prepare()
        response = super(BaseRouteView, self).dispatch(*args, **kwargs)
        self.on_finish()
        return response


def route_view(cls):
    class RouteView(BaseRouteView):
        view_cls = cls

    return RouteView