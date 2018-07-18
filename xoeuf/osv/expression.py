#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Extensions to `odoo.osv.expression`.

This module reexport all symbols from the `odoo.osv.expression` so it can be
used a replacement.

Additions and changes:

- There's a new `Domain`:class: which allows to do some arithmetic with
  domains.

- The functions `AND`:func: and `OR`:func: don't need to you pass a domain in
  first normal form, they ensure that themselves.

- You can test some a weak form of implication, i.e 'Domain(X).implies(Y)' is
  True if can proof that whenever X is True, Y also is.  This method can have
  false negatives, but not false positives: there are cases for which we can't
  find the proof (we return False) which should be True; but if we return
  True, there's a proof.

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


try:
    from xoutil.objects import crossmethod  # TODO: migrate
except ImportError:
    class crossmethod(object):
        '''Decorate a function as static or instance level.

        Example:

          >>> class Mule(object):
          ...     @crossmethod
          ...     def print_args(*args):
          ...         print(args)

          # Call it as a staticmethod
          >>> Mule.print_args()
          ()

          # Call it as an instance
          >>> Mule().print_args()   # doctest: +ELLIPSIS
          (<...Mule object at ...>,)

        .. note:: This is different from `hybridmethod`:func:.  Hybrid method
                  always receive the implicit argument (either `cls` or
                  `self`).

        '''
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, owner):
            if instance is None:
                return self.func
            else:
                return self.func.__get__(instance, owner)


UNARY_OPERATORS = [this.NOT_OPERATOR]
BINARY_OPERATORS = [this.AND_OPERATOR, this.OR_OPERATOR]


# Exports normalize_leaf so that we can replace 'from xoeuf.odoo.
def normalize_leaf(term):
    if this.is_leaf(term):
        left, operator, right = this.normalize_leaf(term)
        # Avoid no hashable values in domain terms
        if not getattr(right, '__hash__', False) and hasattr(right, '__iter__'):  # noqa
            right = tuple(right)
        return left, operator, right
    return term


class Domain(list):
    '''A predicate expressed as an Odoo domain.

    .. note:: This is an *operational* wrapper around normal Odoo domains
              (lists) with methods to do logical manipulation of such values.

    It's a subtype of Odoo domains (i.e `list`:class:), which means that
    wherever an Odoo domain is expected you can use a Domain.  See the `Liskov
    substitution principle`__.

    __ https://en.wikipedia.org/wiki/Liskov_substitution_principle

    '''
    def __init__(self, seq=None):
        # TODO: Can you do some sanity check to avoid common mistakes?  For
        # me, it's normal that I do ``Model.search(['field', '=', value])``
        # and forget the tuple...
        from xoeuf.odoo.tools.safe_eval import const_eval
        seq = seq or ()
        # some times the domains are saved in db in char or text fields.
        if isinstance(seq, string_types):
            seq = const_eval(seq)
        super(Domain, self).__init__(seq)

    def implies(self, other):
        '''Check if a domain implies another.

        For any two domains `A` and `B`, the following rules are always true:

        - ``A.implies(A)``
        - ``(A & B).implies(A)``
        - ``A.implies(A | B)``.
        - ``not B.implies(A) == (A | B).implies(A)``

        '''
        other = DomainTree(Domain(other).second_normal_form)
        return DomainTree(self.second_normal_form).implies(other)

    @property
    def first_normal_form(self):
        '''The first normal form.

        The first normal form is the same domain with all `and` operators
        explicit.

        For instance, having ``domain`` value like::

            >>> domain = Domain(
            ...     [('field_y', 'not in', False), ('field_x', '!=', 'value')]
            ... )

        Then::

            >>> domain.first_normal_form
            ['&', ('field_y', 'not in', False), ('field_x', '!=', 'value')]

        '''
        return Domain(this.normalize_domain(self))

    @property
    def second_normal_form(self):
        '''The second normal form.

        After obtaining the `first_normal_from`:attr:, change terms to its
        canonical form, and distribute the `not` logical operator inside
        terms.

        .. seealso:: `normalize_leaf`:func: for the canonical form of terms.

        .. seealso:: `distribute_not`:meth:

        Example::

            >>> domain1 = Domain([
            ...     ('field_x', 'not in', False),
            ...     '!',
            ...     ('field_y', '>', 1)
            ... ])

            >>> domain2 = Domain([
            ...     '|',
            ...     ('field_x', 'not in', False),
            ...     ('field_y', '<>', 'value'),
            ...     ('field_z', '>', 1)
            ... ])

            >>> domain3 = Domain([
            ...     '|',
            ...     ('field_x', 'not in', False),
            ...     '!',
            ...     ('field_y', '<>', 'value'),
            ...     ('field_z', '>', 1)
            ... ])

            >>> domain1.first_normal_form
            ['&', ('field_x', '!=', False), ('field_y', '<=', 1)]

            >>> domain2.first_normal_form
            [
                '&',
                '|',
                ('field_x', '!=', False),
                ('field_y', '!=', 'value'),
                ('field_z', '>', 1)
            ]

            >>> domain3.first_normal_form
            [
                '&',
                '|',
                ('field_x', '!=', False),
                ('field_y', '=', 'value'),
                ('field_z', '>', 1)
            ]

        '''
        res = self.first_normal_form
        res = Domain((normalize_leaf(item) for item in res))
        return res.distribute_not()

    @property
    def simplified(self):
        '''A simplified second normal form of the domain.

        Example::

            >>> domain1 = Domain([
            ...     ('field_x', '!=', False),
            ...     ('field_y', '=', 'value'),
            ...     ('field_z', 'in', (1, 2, 3)),
            ...     ('field_y', '=', 'value'),
            ... ])

            >>> domain2 = Domain([
            ...     '|',
            ...     ('field_x', '!=', False),
            ...     ('field_y', '=', 'value'),
            ...     ('field_z', 'in', (1, 2, 3)),
            ...     '|',
            ...     ('field_y', '=', 'value'),
            ...     ('field_x', '!=', False)
            ... ])

            >>> domain3 = Domain([
            ...     ('field_y', '!=', False),
            ...     ('field_x', 'in', (1,)),
            ...     '|',
            ...     ('field_y', '!=', False),
            ...     '|',
            ...     ('field_x', 'in', (1,)),
            ...     ('field_x', 'in', (2,))
            ... ])

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

        '''
        return DomainTree(self.second_normal_form).get_simplified_domain()

    def distribute_not(self):
        '''Return a new domain without `not` operators.

        For instance, having ``domain`` value like::

            >>> domain = Domain([
            ...     '!', ('field_x', '!=', False),
            ...     '!', ('field_y', '=', 'value'),
            ...     '!', ('field_z', 'in', (1, 2, 3)),
            ...     '!', ('field_w', '>', 1),
            ... ])

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

        '''
        return Domain(this.distribute_not(self.first_normal_form))

    @crossmethod
    def AND(*domains):
        '''Join given domains using `and` operator.

        :return: A domain if first normal form.

        '''
        return Domain(this.AND(
            [Domain(domain).second_normal_form for domain in domains]
        ))

    __and__ = __rand__ = AND

    @crossmethod
    def OR(*domains):
        '''Join given domains using `or` operator.

        :return: A domain if first normal form.

        '''
        return Domain(this.OR(
            [Domain(domain).second_normal_form for domain in domains]
        ))

    __or__ = __ror__ = OR

    def __invert__(self):
        return Domain(['!'] + self.second_normal_form)

    def __eq__(self, other):
        '''Two domains are equivalent if both have similar DomainTree.

        '''
        # TODO: In logic, we can identify two predicates if: a implies
        # b and b implies a, although this has nothing to do with them being
        # the *same* predicate.  However, since this implementation only
        # yields True when both domains have the same hash, we can find a, b
        # such that a implies b and b implies a, but a != b.
        other = Domain(other)
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(DomainTree(self.second_normal_form))


class DomainTerm(object):
    def __init__(self, term):
        if isinstance(term, DomainTerm):
            term = term.original
        self.original = term
        term = normalize_leaf(term)
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
            raise ValueError("Invalid domain term %r" % term)

    def __getitem__(self, x):
        if self.is_leaf:
            return (self.left, self.operator, self.right)[x]
        else:
            return self.operator[x]

    def __eq__(self, other):
        if not isinstance(other, DomainTerm):
            other = DomainTerm(other)
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other

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

    def implies(self, other):
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
                # TODO: x = 1  implies x != 2; x = 2 1 implies x > 1
                return False

    def __hash__(self):
        return hash(self.normalized)


class DomainTree(object):
    '''Tree structure to express Odoo domains.

    .. warning:: This class in not a public API of this model.  Its attributes
       may change in incompatible ways from one release to the other.

    A domain like this::

      [
          '&',
          '&',
          ('field_y', '!=', False),
          ('field_x', '=', 'value'),
          '|',
          ('field_z', 'in', (1, 2, 3)),
          ('field_w', '>', 1)
      ]

    Is represented like this::

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

    .. warning:: The domain must be in the second normal form.

    '''
    def __init__(self, domain, parent=None):
        term = domain.pop(0)
        self.term = DomainTerm(term)
        self.parent = parent
        if term in this.DOMAIN_OPERATORS:
            count = 2  # minimum number of operand in an operation.
            children = set()
            while count:
                if domain[0] == term:
                    count += 1
                    domain.pop(0)
                else:
                    child = DomainTree(domain, self)
                    # A & ((B & C) | A) should be simplified as A & B & C
                    if child.term == self.term:
                        children |= child.children
                    else:
                        children.add(child)
                    count -= 1
            # if a tree node have only one child it be come into it child.
            if len(children) == 1:
                child = children.pop()
                self.term = child.term
                self.children = child.children
            else:
                self.children = children
        else:
            self.children = set()
        self._simplify()

    @property
    def is_operator(self):
        return self.term in this.DOMAIN_OPERATORS

    @property
    def is_leaf(self):
        return not self.is_operator

    def _simplify(self):
        """Remove redundant branches.

        """
        for child in set(self.children):
            if self.term == this.AND_OPERATOR:
                # If current `child` is implied by any other ignore it.
                func = lambda x, y: y.implies(x)
            else:
                # If current `child` implies any other ignore it.
                func = lambda x, y: x.implies(y)
            if any(func(child, y) for y in self.children - {child}):
                self.children.remove(child)
        if len(self.children) == 1:
            _self = self.children.pop()
            self.children = _self.children
            self.term = _self.term

    @property
    def sorted_children(self):
        # TODO: Sort by hash is weird.  What does it mean?
        return sorted(self.children, key=lambda item: hash(item))

    def get_simplified_domain(self):
        if self.parent:
            res = Domain(
                self.term.original for x in range(1, len(self.children) or 2)
            )
        elif self.is_leaf:
            res = Domain([self.term.original])
        else:
            # Initials `&` aren't needed.
            res = Domain(
                [self.term.original] if self.term == this.OR_OPERATOR else []
            )
        if not self.is_leaf:
            res.extend(
                chain(
                    *(x.get_simplified_domain() for x in self.sorted_children)
                )
            )
        return res

    def __repr__(self):
        if self.is_leaf:
            return repr(self.term)
        else:
            return '(%s)' % (' %r ' % self.term).join(
                repr(child) for child in self.sorted_children
            )

    def __eq__(self, other):
        if self.is_leaf == other.is_leaf:
            if self.is_leaf:
                return self.term == other.term
            else:
                return self.term == other.term and not self.children ^ other.children  # noqa
        return False

    def __ne__(self, other):
        return not self == other

    def implies(self, other):
        funct = all if other.term == this.AND_OPERATOR else any
        if self.is_leaf:
            # A => A
            if self.term.implies(other.term):
                return True
            # A => A | B
            if other.is_operator and funct(self.implies(child)
                                           for child in other.sorted_children):
                return True
        elif self.is_operator:
            funct2 = any if self.term == this.AND_OPERATOR else all
            # A & B => A
            if funct2(child.implies(other) for child in self.sorted_children):
                return True
            # A & B => A | B
            if funct(funct2(child.implies(other_child)
                            for child in self.sorted_children)
                     for other_child in other.sorted_children):
                return True
        return False

    def __hash__(self):
        return hash(tuple([self.term] + self.sorted_children))

    def walk(self):
        '''Performs a post-fix walk of the tree.

        Yields tuples of ``(kind, what)``.  `kind` can be either 'TERM' or
        'OPERATOR'.  `what` will be the term or operator.  For `term` it will
        the tuple ``(field, operator, arg)`` in Odoo domains.  For `operator`
        it will be the string identifying the operator.

        Despite that the tree allows AND (``&``) and OR (``|``) operator to
        have more than two children, we generate OPERATOR items for the
        equivalent binary expression tree::

           >>> from xoeuf.osv.expression import Domain, DomainTree
           >>> d = Domain([('a', '=', 1), ('b', '=', 2), ('c', '=', 3)])
           >>> tree = DomainTree(d.second_normal_form)
           >>> list(tree.walk())
           [('TERM', ('a', '=', 1)),
            ('TERM', ('c', '=', 3)),
            ('TERM', ('b', '=', 2)),
            ('OPERATOR', '&'),
            ('OPERATOR', '&')]

        .. note:: DomainTree always simplify its input.  The walk is not a
           syntactical walk of the input but of its simplified form.  Since
           all operators are commutative, the order of the children may differ
           widely from run to the other.

        '''
        if self.is_leaf:
            yield ('TERM', self.term.original)
        else:
            for which in self.children:
                for what in which.walk():
                    yield what
            yield ('OPERATOR', self.term)
            # Since the tree groups more than two children under a single
            # instance of binary operator, we have to yield it once per pair.
            if self.term.original in BINARY_OPERATORS:
                for _ in range(len(self.children) - 2):
                    yield ('OPERATOR', self.term)


# Exports AND and OR so that we can replace 'from xoeuf.odoo.
def AND(domains):
    return Domain.AND(*domains)


def OR(domains):
    return Domain.OR(*domains)
