import connection as cc
from datetime import datetime

today = datetime.today()


def order_by_value(dataset, param, order='asc'):
    """
    :param dataset: a list of dictionaries
    :param param: the key of the inner dicts based on which the list is sorted
    :param order: default values takes 'asc' or 'desc'
    :return:

    """
    list_of_possible_key_ints = ['id', 'view_number', 'vote_number']
    if param in list_of_possible_key_ints:

        if order == 'desc':
            ordered_dataset = sorted(dataset, key=lambda i: int(i[param]), reverse=True)
        elif order == 'asc':
            ordered_dataset = sorted(dataset, key=lambda i: int(i[param]))
        return ordered_dataset
    elif param == 'submission_time':
        if order == 'desc':
            ordered_dataset = sorted(dataset, key=lambda i: datetime.strptime(i[param], "%Y-%m-%d-%H:%M:%S"), reverse=True)
        elif order == 'asc':
            ordered_dataset = sorted(dataset, key=lambda i: datetime.strptime(i[param], "%Y-%m-%d-%H:%M:%S"))
        return ordered_dataset
    else:
        if order == 'desc':
            ordered_dataset = sorted(dataset, key=lambda i: i[param].lower(), reverse=True)
            return ordered_dataset
        elif order == 'asc':
            ordered_dataset = sorted(dataset, key=lambda i: i[param].lower())
            return ordered_dataset

def make_compat_display(dataset, html_elem = 'not_textarea'):

    if type(dataset) == dict:
        if html_elem == 'not_textarea':
            for dicto in dataset:
                for key in dicto.keys():
                    dicto[key] = dicto[key].replace('\r\n', '<br/>')
        if html_elem == 'textarea':
            for dicto in dataset:
                for key in dicto.keys():
                    dicto[key] = dicto[key].replace('<br/>', '\r\n')
    elif type(dataset) == str:
        if html_elem == 'not_textarea':
            dataset = dataset.replace('\r\n', '<br/>')
        elif html_elem == 'textarea':
            dataset = dataset.replace('<br/>', '\r\n')
    return dataset




#
# questions_list = cc.read_questions('data/questions.csv')
#
# paramt = 'submission_time'
# sorted_list = order_by_value(questions_list, paramt, 'desc')
# print(type(sorted_list))
#
# for elem in sorted_list:
#     print(elem)


