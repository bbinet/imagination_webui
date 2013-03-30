from pyramid.view import view_config


@view_config(route_name='show', renderer='string')
def show(request):
    return 'show'


@view_config(route_name='update', renderer='string')
def update(request):
    return 'update'
