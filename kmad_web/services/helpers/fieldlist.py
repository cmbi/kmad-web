import logging


logging.basicConfig()
_log = logging.getLogger(__name__)


def delete(fieldlist, delete_index):
    data_length = len(fieldlist)
    tmp_list = []
    for i in range(data_length - delete_index):
        tmp_list.append(fieldlist.data[-1])
        fieldlist.pop_entry()

    tmp_list.reverse()
    for i in tmp_list[1:]:
        fieldlist.append_entry(i)
