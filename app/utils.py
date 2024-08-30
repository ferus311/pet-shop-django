from urllib.parse import urlencode


def build_paginated_url(request, page_number):
    query_params = request.GET.copy()
    query_params['page'] = page_number
    return '?' + urlencode(query_params, doseq=True)
