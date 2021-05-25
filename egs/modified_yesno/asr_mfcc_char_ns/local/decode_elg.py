import os
import sys


class Node(object):

    """
    FST Node
    para:
    nid, int, the node index
    p_arc, list, list of Arc objects which connected to the previous nodes
    n_arc, list, list of Arc objects which connected to the next nodes
    """

    def __init__(self, nid, p_arc, n_arc):
        self.nid = nid
        self.p_arc = p_arc
        self.n_arc = n_arc

    def get_index(self):
        return self.nid

    def get_previous(self):
        return self.p_arc

    def get_next(self):
        return self.n_arc


class Arc(object):
    """
    FST Arc
    para:
    head int, the head node index
    tail, int, the tail node index
    iid, int, the input symbol index
    oid, int, the output symbol index
    w, float, the weight
    """

    def __init__(self, head, tail, iid, oid, w):
        self.__head__ = head
        self.__tail__ = tail
        self.__iid__ = iid
        self.__oid__ = oid
        self.__weight__ = w

    def get_head(self):
        return self.__head__

    def get_tail(self):
        return self.__tail__

    def get_iid(self):
        return self.__iid__

    def get_oid(self):
        return self.__oid__

    def get_weight(self):
        return self.__weight__


class WFST(object):
    """
    WFST object
    para:
    input_file: file_path, fst in str form
    """

    @staticmethod
    def read_str(input_file):
        init_nodes = [0]
        final_nodes = []
        nodes = set()
        from_node = dict()
        to_node = dict()
        input_indexes = set()
        output_indexes = set()
        with open(input_file) as f:
            for line in f:
                lc = line.strip().split()
                if len(lc) == 1:
                    final_nodes.append(int(lc[0]))
                head = int(lc[0])
                tail = int(lc[1])
                iid = int(lc[2])
                oid = int(lc[3])
                w = float(lc[4])
                nodes.update((head, tail))

                if head not in from_node.keys():
                    from_node[head] = [(tail, iid, oid, w)]
                else:
                    from_node[head].append((tail, iid, oid, w))
                if tail not in to_node.keys():
                    to_node[tail] = [(head, iid, oid, w)]
                else:
                    to_node[tail].append((head, iid, oid, w))
                input_indexes.add(iid)
                output_indexes.add(oid)

        return init_nodes, final_nodes, nodes, arcs, input_indexes, output_indexes

    def __init__(self, input_file):
        self.__init_nodes__ = init_nodes
        self.__final_nodes__ = final_nodes
        self.__nodes__ = nodes
        self.__arcs__ = arcs
        self.__input_indexes__ = input_indexes
        self.__output_indexes__ = output_indexes
