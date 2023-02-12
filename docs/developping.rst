
Developping
===========


For the moment pygame_cards is a very small library so if you want to
use it for something specific, please contact us via github https://github.com/ScienceGamez/pygame_cards .


The following sections are explaining few principles used in pygame_cards.

pygame
------

pygame_cards works on `pygame <https://www.pygame.org>`_ .
It is not necessary to know how pygame works to use pygame_cards.


Inheritance
-----------

Pygame cards works mainly on inheriting from base classes.
This allows the different managers for the graphics or for games to
work for all cards the same and reduces duplicate code.

In particular the implementation for cards is based on dataclasses.
If you don't know about them, you should read a tutorial about them.


Nested Graphics
---------------

Some graphic objects work on nesting, such that if you have one object
which nested inside another the nested object will have its size defined
by the parent object.

For examples Cards are nested in CardsSet which are themselves nested in
Boards.

The advantage of this strategy is that the developer can defined simply
the size for the parent object and the relative positions in the parent.
He does not need to specific the size of each surface.