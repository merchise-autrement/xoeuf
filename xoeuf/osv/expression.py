#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------
# xoeuf.api
# ---------
# Copyright (c) 2015-2017 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-10-02

'''Odoo expression extension.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import operator
from itertools import chain
from xoeuf.odoo.osv import expression as _odoo_expression
from xoutil.eight import string_types


# TODO: `copy_members` will be deprecated in xoutil 1.8, use instead the same
# mechanisms as `xoutil.future`.
from xoutil.modules import copy_members as _copy_python_module_members
this = _copy_python_module_members(_odoo_expression)
del _copy_python_module_members
del _odoo_expression


class Domain(list):
    """ Type for odoo filter domain handle.

    An odoo domain filter is an extended list to allow additional
    operations like `&`, `|`, `-`, `imply`, `normalized`, `simplified` and
    modify behaviour to allow compare two domains.

    You can do:

    #. A & B

    #. A | B

    #. -A

    #. A == B

    #. A.imply(B)

    #. A.normalized

    #. A.simplified


    """

    def __init__(self, seq=None):
        from odoo.tools.safe_eval import const_eval
        seq = seq or ()
        # some times the domains are saved in db in char or text fields.
        if isinstance(seq, string_types):
            seq = const_eval(seq)
        super(Domain, self).__init__(seq)

    def imply(self, other):
        """ Check if a odoo filter domain imply an other.

        A => A
        A & b => A
        A => A | B
        A | B => A iff B => A

        """
        other = DomainTree(Domain(other).normalized)
        return DomainTree(self.normalized).imply(other)

    def normalize_domain(self):
        """Explicit all `and` operators.

        For instance, having ``domain`` value like::

            >>> domain = Domain(
            >>>     [('field_y', 'not in', False), ('field_x', '!=', 'value')]
            >>> )

        Then::

            >>> domain.normalize_domain
            ['&', ('field_y', 'not in', False), ('field_x', '!=', 'value')]

        """
        return Domain(this.normalize_domain(self))

    @property
    def normalized(self):
        """Normalize domain in 3 steps:
        1. Explicit all `and` operators.
        2. Change a term's operator to some canonical form.
        3. Remove `not` operators negating the target term operator.

        For instance, having ``domain1``, ``domain2`` and ``domain3`` value
        like::

            >>> domain1 = Domain([
            >>>     ('field_x', 'not in', False),
            >>>     '!',
            >>>     ('field_y', '>', 1)
            >>> ])
            >>> domain2 = Domain([
            >>>     '|',
            >>>     ('field_x', 'not in', False),
            >>>     ('field_y', '<>', 'value'),
            >>>     ('field_z', '>', 1)
            >>> ])
            >>> domain3 = Domain([
            >>>     '|',
            >>>     ('field_x', 'not in', False),
            >>>     '!',
            >>>     ('field_y', '<>', 'value'),
            >>>     ('field_z', '>', 1)
            >>> ])

        Then::

            >>> domain1.normalized
            ['&', ('field_x', '!=', False), ('field_y', '<=', 1)]

            >>> domain2.normalized
            [
                '&',
                '|',
                ('field_x', '!=', False),
                ('field_y', '!=', 'value'),
                ('field_z', '>', 1)
            ]

            >>> domain3.normalized
            [
                '&',
                '|',
                ('field_x', '!=', False),
                ('field_y', '=', 'value'),
                ('field_z', '>', 1)
            ]

        """
        res = self.normalize_domain()
        res = Domain((this.normalize_leaf(item) for item in res))
        return res.distribute_not()

    @property
    def simplified(self):
        """ Normalize the domain and exclude redundant terms.

        For instance, having ``domain1``, ``domain2`` and ``domain3`` value
        like::

            >>> domain1 = Domain([
            >>>     ('field_x', '!=', False),
            >>>     ('field_y', '=', 'value'),
            >>>     ('field_z', 'in', (1, 2, 3)),
            >>>     ('field_y', '=', 'value'),
            >>> ])
            >>> domain2 = Domain([
            >>>     '|',
            >>>     ('field_x', '!=', False),
            >>>     ('field_y', '=', 'value'),
            >>>     ('field_z', 'in', (1, 2, 3)),
            >>>     '|',
            >>>     ('field_y', '=', 'value'),
            >>>     ('field_x', '!=', False)
            >>> ])
            >>> domain3 = Domain([
            >>>     ('field_y', '!=', False),
            >>>     ('field_x', 'in', (1,)),
            >>>     '|',
            >>>     ('field_y', '!=', False),
            >>>     '|',
            >>>     ('field_x', 'in', (1,)),
            >>>     ('field_x', 'in', (2,))
            >>> ])

        Then::

            >>> domain1.simplified
            [
                '&',
                '&',
                ('field_x', '!=', False),
                ('field_y', '=', 'value'),
                ('field_z', 'in', (1, 2, 3))
            ]

            >>> domain2.simplified
            [
                '&',
                '|',
                ('field_x', '!=', False),
                ('field_y', '=', 'value'),
                ('field_z', 'in', (1, 2, 3))
            ]

            >>> domain3.simplified
            ['&', ('field_x', 'in', (1,)), ('field_y', '!=', False)]

        """
        return DomainTree(self.normalized).get_simplified_domain()

    def distribute_not(self):
        """ Remove `not` operators negating the target term operator.

        .. note:: Normalizes the domain is required.

        For instance, having ``domain`` value like::

            >>> domain = Domain([
            >>>     '!', ('field_x', '!=', False),
            >>>     '!', ('field_y', '=', 'value'),
            >>>     '!', ('field_z', 'in', (1, 2, 3)),
            >>>     '!', ('field_w', '>', 1),
            >>> ])

        Then::

            >>> domain.distribute_not()
            [
                '&',
                '&',
                '&',
                ('field_x', '=', False),
                ('field_y', '!=', 'value'),
                ('field_z', 'not in', (1, 2, 3)),
                ('field_w', '<=', 1)
            ]
        """
        return Domain(this.distribute_not(self.normalize_domain()))

    def AND(*domains):
        """ Join given domains using `and` operator. To do this is needed
        normalize the domains

        :return: normalized odoo filter domain.
        """
        return Domain(this.AND(
            [Domain(domain).normalized for domain in domains]
        ))

    __and__ = __rand__ = AND

    def OR(*domains):
        """ Join given domains using `or` operator. To do this is needed
        normalize the domains

        :return: normalized odoo filter domain.
        """
        return Domain(this.OR(
            [Domain(domain).normalized for domain in domains]
        ))

    __or__ = __ror__ = OR

    def __neg__(self):
        return Domain(['!'] + self.normalized)

    def __eq__(self, other):
        """ Two domains are equivalent if both have similar DomainTree.

        """
        other = Domain(other)
        return DomainTree(self.normalized) == DomainTree(other.normalized)

    def __hash__(self):
        return hash(DomainTree(self.normalized))


class DomainTerm(object):

    def __init__(self, term):
        if isinstance(term, DomainTerm):
            term = term.original
        self.original = term
        term = this.normalize_leaf(term)
        self.normalized = term
        if this.is_operator(term):
            self.is_operator = True
            self.operator = term
            self.is_leaf = self.left = self.right = False
        elif this.is_leaf(term):
            self.is_operator = False
            self.is_leaf = True
            self.left, self.operator, self.right = term
        else:
            # TODO: May be a # TypeError.
            raise ValueError("Invalid domain term.")

    def __getitem__(self, x):
        if self.is_leaf:
            return (self.left, self.operator, self.right)[x]
        else:
            return self.operator[x]

    def __eq__(self, other):
        if not isinstance(other, DomainTerm):
            other = DomainTerm(other)
        return self.normalized == other.normalized

    def __repr__(self):
        if self.original == self.normalized:
            return repr(self.original)
        else:
            return '%r => %r' % (self.original, self.normalized)

    operators_implication = {
        '=?': lambda x, y: operator.eq(x, y) or y is False,
        '>': operator.ge,
        '>=': operator.ge,
        '<': operator.le,
        '<=': operator.le,
        'in': lambda x, y: all(i in y for i in x),
        'not in': lambda x, y: all(i in x for i in y),
        'like': lambda x, y: x.find(y) >= 0,
        # TODO: asd_g imply asdfg `_` == any character
        '=like': lambda x, y: x.find(y) >= 0,
        'not like': lambda x, y: y.find(x) >= 0,
        'ilike': lambda x, y: x.lower().find(y.lower()) >= 0,
        # TODO: asd_g imply asdfg `_` == any character
        '=ilike': lambda x, y: x.lower().find(y.lower()) >= 0,
        'not ilike': lambda x, y: y.lower().find(x.lower()) >= 0,
    }

    def imply(self, other):
        other = DomainTerm(other)
        # equals terms are implied.
        if self == other:
            return True
        # terms which different left operand can't be compared.
        elif self.left != other.left:
            return False
        elif self.is_operator:
            # & => &
            return self.operator == other.operator
        else:
            # (x = 1)  => (x = 1)
            # (x > 1) => (x > 0)
            # (x in (1,2,3)) => (x in (1,2,3,4))
            if self.operator == other.operator:
                compare = self.operators_implication.get(other.operator)
                return compare(self.right, other.right) if compare else False
            else:
                # TODO: x = 1  imply x != 2; x = 2 1 imply x > 1
                return False

    def __hash__(self):
        return hash(self.normalized)


class DomainTree(object):
    """ Tree structure to express odoo filter domains.

    A domain like this:
    [
        ('field_y', '!=', False),
        ('field_x', '=', 'value'),
        '|',
        ('field_z', 'in', (1, 2, 3))
        ('field_w', '>', 1)
    ]

    Is represented like this:
                                   +-----+
                                   | '&' |
                                   +--+--+
                                      |
                 +--------------------+------------------------+
                 |                    |                        |
    +------------+-----------+ +------+------------------+  +--+--+
    |('field_y', '!=', False)| |('field_x', '=', 'value')|  | '|' |
    +------------------------+ +-------------------------+  +--+--+
                                                               |
                                +------------------------------+--------+
                                |                                       |
                   +------------+---------------+       +---------------+---+
                   |('field_z', 'in', (1, 2, 3))|       |('field_w', '>', 1)|
                   +----------------------------+       +-------------------+

    """

    def __init__(self, domain):
        term = domain.pop(0)
        self.term = DomainTerm(term)
        if term in this.DOMAIN_OPERATORS:
            count = 1
            childs = set()
            while len(childs) <= count:
                if domain[0] == term:
                    count += 1
                    domain.pop(0)
                else:
                    child = DomainTree(domain)
                    # If new node is al ready implied by any other ignore it.
                    if any(x.imply(child) for x in childs):
                        count -= 1
                    else:
                        childs.add(child)
            # if a tree node have only one child it be come into it child.
            if len(childs) == 1:
                child = childs.pop()
                self.term = child.term
                self.childs = child.childs
                self.is_leaf = child.is_leaf
            else:
                self.childs = childs
                self.is_leaf = False
        else:
            self.childs = set()
            self.is_leaf = True

    @property
    def sorted_childs(self):
        return sorted(self.childs, key=lambda item: item.term.normalized)

    def get_simplified_domain(self):
        res = Domain(self.term for x in range(1, len(self.childs) or 2))
        if not self.is_leaf:
            res.extend(
                chain(
                    *(x.get_simplified_domain() for x in self.sorted_childs)
                )
            )
        return res

    def __repr__(self):
        if self.is_leaf:
            return repr(self.term)
        else:
            return '(%s)' % (' %r ' % self.term).join(
                repr(child) for child in self.sorted_childs
            )

    def __eq__(self, other):
        if self.is_leaf == other.is_leaf:
            if self.is_leaf:
                return self.term == other.term
            else:
                return (
                    self.term == other.term and not self.childs ^ other.childs
                )
        return False

    def imply(self, other):
        funct = all if other.term == this.AND_OPERATOR else any
        if self.is_leaf:
            # A => A
            if self.term.imply(other.term):
                return True
            # A => A | B
            if not other.is_leaf and funct(self.imply(child)
                                           for child in other.sorted_childs):
                return True
        elif not self.is_leaf:
            funct2 = any if self.term == this.AND_OPERATOR else all
            # A & B => A
            if funct2(child.imply(other) for child in self.sorted_childs):
                return True
            # A & B => A | B
            if funct(funct2(child.imply(other_child)
                            for child in self.sorted_childs)
                     for other_child in other.sorted_childs):
                return True
        return False

    def __hash__(self):
        return hash(tuple([self.term] + self.sorted_childs))

