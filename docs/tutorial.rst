Tutorial
========




Using an existing card game
---------------------------


`pygame_cards` provides you with a base set of cards.

TODO: write how to use it.


Creating a new card game
------------------------


The tutorial of pygame_cards will show you how to
make a simple card game.

As an example we will create a small minions game.
It will be something a bit similar to
`hearthstone <https://hearthstone.blizzard.com/>`_.


Creating your cards
^^^^^^^^^^^^^^^^^^^

First we will focus on designing our cards.

Inheriting from the Abstract Class
""""""""""""""""""""""""""""""""""


You need to define some fields for your card.
You can do that by inheriting from :py:class:`~pygame_cards.abstract.AbstractCard` .

It has only one mandatory argument which is `name` but we can add many others.

See the script below that generates a minion for you.

.. literalinclude:: ../examples/tutorial/minion_card.py
    :language: python


If you are not familiar with
`dataclasses <https://docs.python.org/3/library/dataclasses.html#module-dataclasses>`_
you can just
think that it helps you create instances as it creates the :py:func:`__init__`
for you.

We can see the the output of this script gives us ::

    MinionCard(name='Frodo the Hobbit', u_id=0, health=6, attack=2, cost=3)

We can see that a :py:attr:`u_id` field was created for us.
This is used to track every instance of a Card that is created during the
execution of the game.



Creating a set of Cards
"""""""""""""""""""""""

Now that we know how to create a card, we want to create all the content
we want.

For that we will use the Class :py:class:`~pygame_cards.set.CardsSet`.
You can use it like a python list:


.. literalinclude:: ../examples/tutorial/minion_set.py
    :language: python


Usually you will want to save your data in files instead of writing it
directly in python. For that you can use the :py:func:`pygame_cards.load.from_json`
method.

.. note::
    If you need specific capabilities in your CardSet based on your cards,
    you can inherit from this class and create your own.


Adding Graphics
"""""""""""""""
