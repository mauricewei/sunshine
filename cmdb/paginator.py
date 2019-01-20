#! /usr/bin/env python3


def paginate(paginator, page, is_paginated):
    """
    该函数用来生成分页程序的变量数据
    这些变量将通过get_context_data函数传输到模版
    """
    if not is_paginated:
        return {}
    # 当前页左边连续的页码号，初始值为空
    left = []
    # 当前页右边连续的页码号，初始值为空
    right = []
    # 表示第 1 页页码后是否需要显示省略号
    left_has_more = False
    # 表示最后一页页码前是否需要显示省略号
    right_has_more = False
    # 表示是否需要显示第 1 页的页码号
    first = False
    # 表示是否需要显示最后一页的页码号
    last = False

    page_number = page.number
    total_pages = paginator.num_pages
    page_range = paginator.page_range

    if page_number == 1:
        # 获取当前页码后的3个页码
        right = page_range[page_number:page_number + 3]
        if right[-1] < total_pages - 1:
            right_has_more = True
        if right[-1] < total_pages:
            last = True
    elif page_number == total_pages:
        # 获取当前页码前连续3个页码
        left = page_range[(page_number - 4) if (page_number - 4)
                          > 0 else 0:page_number - 1]
        if left[0] > 2:
            left_has_more = True
        if left[0] > 1:
            first = True
    else:
        left = page_range[(page_number - 4) if (page_number - 4)
                          > 0 else 0:page_number - 1]
        right = page_range[page_number:page_number + 3]
        if left[0] > 2:
            left_has_more = True
        if left[0] > 1:
            first = True
        if right[-1] < total_pages - 1:
            right_has_more = True
        if right[-1] < total_pages:
            last = True

    data = {
        'left': left,
        'right': right,
        'left_has_more': left_has_more,
        'right_has_more': right_has_more,
        'first': first,
        'last': last,
    }
    return data
