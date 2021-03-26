  
"""
    redblacktree.py
    https://github.com/stanislavkozlovski/Red-Black-Tree/blob/master/rb_tree.py
    Tweaked by JLB
        - added custom functions for key comparison
        - added __del__, __contains__, __getitem, __setitem__
        - Using Key/Value now
        - Added ability to Remove an individual Value
        - Added in_order, validate_key, is_color checkers, and many gets
        - Removed ceil, floor
        - Consolidated rotate
    RB Tree Properties:
        0. Root is always black
        1. Every node is colored with either RED or black
        2. All leaf (nil) nodes are colored with black; if a node’s child
            is missing then we will assume that it has a nil child in that
            place and this nil child is always colored black.
        3. Both children of a RED node must be black nodes.
        4. Every path from a node n to a descendent leaf has the same number
            of black nodes (not counting node n). We call this number the
            black height of n, which is denoted by bh(n).
"""

# Sys Imperttss!
from enum import Enum
import operator


# __all__ is a global list of classes
__all__ = ["RBColorEnum", "RBDirectionEnum", "RBNode", "RedblackTree"]


class RBColorEnum(Enum):
    """
    RBColorEnum, used by our RedblackTree
    Defines Colors for nodes.
    """

    black = 0
    NIL = 1
    RED = 2


class RBDirectionEnum(Enum):
    """
    RBDirectionEnum for RedblackEnum
    Defines directions for RedblackTree
    """

    LEFT = 0
    RIGHT = 1


class RBNode:
    """
    Red-black Node in a Binary Tree
    """

    # Slots are useful to define what class variables this class will have
    # This reduces RAM consumption since Python naturally hands all classes
    # a dictionary's worth of variable storage.
    __slots__ = ["_key", "_values", "_color", "_parent", "_left", "_right"]

    def __init__(self, key, value, color, parent=None, left=None, right=None):
        """ Constructor! """

        self._key = key
        self._values = []
        self._values.append(value)
        self._color = color
        self._parent = parent
        self._left = left
        self._right = right

    def __eq__(self, other):
        """
        Equals
        If this node is set to = or != something else,
        this handles it.
        """

        # Other is a RBNode?
        if isinstance(other, RBNode):

            # Neither node set up?
            if self._color == RBColorEnum.NIL and self._color == other._color:
                return True

            # Comparison if our Parents are the same.
            if self._parent is None or other._parent is None:
                parents_are_same = (
                    self._parent is None and
                    other._parent is None
                )
            else:
                parents_are_same = (
                    self._parent._key == other._parent._key and
                    self._parent._color == other._parent._color
                )

            # Everything matches!?
            return (
                self._key == other._key and
                self._color == other._color and
                parents_are_same
            )

        # Let the other object handle it!
        else:
            return other.__eq__(self)

    def __iter__(self):
        """
        Iterator
        This grabs all the way left first, then goes right.
        It waits for something to request the inner result.
        """

        if self._left._color != RBColorEnum.NIL:
            yield from self._left.__iter__()

        yield self.__repr__()

        if self._right._color != RBColorEnum.NIL:
            yield from self._right.__iter__()

    def __repr__(self):
        """
        Formal String
        """

        return f"{self._color} {self._key} {self._values} RBNode"

    def has_children(self) -> bool:
        """
        Returns a boolean indicating if the node has children
        """

        return bool(self.get_children_count())

    def get_children_count(self) -> int:
        """
        Returns the number of NOT NIL children the node has
        """

        if self._color == RBColorEnum.NIL:
            return 0

        return sum(
            [
                int(self._left._color != RBColorEnum.NIL),
                int(self._right._color != RBColorEnum.NIL)
            ]
        )


class RedBlackTree:
    """
    Red/Black Tree
    """

    # Every node has null nodes as children initially,
    # create one such object for easy management
    NIL_NODE = RBNode(key=None, value=None, color=RBColorEnum.NIL, parent=None)

    def __init__(
        self,
        key_comparator_function=None,
        key_equals_function=None,
        key_validator_function=None
       ):
        """
        Constructor?
        """

        # Key Comparator handles greater and less than
        if key_comparator_function is None:
            self._key_comparator_function = self.__simple_key_comparator
        else:
            self._key_comparator_function = key_comparator_function

        # Key Equals is used for determining if two values... equal each other.
        if key_equals_function is None:
            self._key_equals_function = self.__simple_key_equals
        else:
            self._key_equals_function = key_equals_function

        # Key Validator is used for Add/Remove, ensuring the key entered
        # is a valid entry
        # ... this probably isn't needed?
        if key_validator_function is None:
            self._key_validator_function = self.__simple_key_validator
        else:
            self._key_validator_function = key_validator_function

        # Root!
        self._root = None

    def __contains__(self, key):
        """
        Contains?
        """

        return self.contains(key)

    def __delitem__(self, key):
        """
        Delete an item?
        """

        if self.validate_key(key):
            self.remove_key(key)

    def __getitem__(self, key):
        """
        Get an item?
        """

        return self.find_node(key)[0]

    def __iter__(self):
        """
        Iteratoor!
        """

        # No data?
        if not self._root:
            return []

        yield from self._root.__iter__()

    def __setitem__(self, key, value):
        """
        Given a key/value, inserts it
        """

        self.add(key, value)

    def __str__(self):
        """
        Print the 'informal' version.
        """

        return str(self.in_order(self._root))

    def add(self, key, value):
        """
        Adds the given Key/Value to our RBTree
        """

        if not self.validate_key(key):
            return

        #  Need a root?  YOU GOT IT.
        if not self._root:
            self._root = RBNode(
                key=key,
                value=value,
                color=RBColorEnum.black,
                parent=None,
                left=self.NIL_NODE,
                right=self.NIL_NODE
            )
            return

        # Parent Node and Direction (L or R)
        parent, node_dir = self.find_node(key, True)

        # No parent?  We out
        if parent is None:
            return

        # Parent but no Direction?  ADD!
        elif node_dir is None:
            parent._values.append(value)
            return

        # Create a new node and either add it to our left or right, as needed.
        new_node = RBNode(
            key=key,
            value=value,
            color=RBColorEnum.RED,
            parent=parent,
            left=self.NIL_NODE,
            right=self.NIL_NODE
        )
        if node_dir == RBDirectionEnum.LEFT:
            parent._left = new_node
        else:
            parent._right = new_node

        # Try to balance us!
        self.try_rebalance(new_node)

    def contains(self, key):
        """
        Returns a boolean indicating if
        the given value is present in the tree
        """

        return bool(self.find_node(key)[0])

    def find_node(self, key, to_nil=False):
        """
        Given a key, attempts to find it in our Tree.
        If we have to_nil as True, we are looking for a Nil node to
        put its data in.
        """

        def inner_find(node):
            """
            Recursion function to find a node!
            """

            # Nope!
            if not node or node == self.NIL_NODE:
                return None, None

            # Key presented same as one we want?
            elif self._key_equals_function(key, node._key):
                return node, None

            # Greater Than!
            elif not self._key_comparator_function(key, node._key):

                # We going to_nil and it a match?
                if to_nil and node._right == self.NIL_NODE:
                    return node, RBDirectionEnum.RIGHT

                # Go on.
                return inner_find(node._right)

            # Less Than!
            elif self._key_comparator_function(key, node._key):

                # We going to_nil and it a match?
                if to_nil and node._left == self.NIL_NODE:
                    return node, RBDirectionEnum.LEFT

                # Go on.
                return inner_find(node._left)

        # Return!
        if self._root:
            return inner_find(self._root)
        else:
            return self.NIL_NODE

    def get_child_node(self, node):
        """
        Gets our Child, left first.
        """

        return node._left if node._left != self.NIL_NODE else node._right

    def get_grandparent_node(self, node):
        """
        Gets our Grandparent
        """

        return self.get_parent_node(self.get_parent_node(node))

    def get_maximum_node(self, node):
        """
        Useful for finding the Largest node either in the
        Left or Right Tree
        """

        # To the right, to the right!
        if node._right != self.NIL_NODE:
            return self.get_maximum_node(node._right)
        else:
            return node

    def get_minimum_node(self, node):
        """
        Useful for finding the Smallest node either in the
        Left or Right Tree
        """

        # Must... go... DEEPER!
        if node._left != self.NIL_NODE:
            return self.get_minimum_node(node._left)
        else:
            return node

    def get_node_color(self, node):
        """
        Gets our node's color.
        This is a function because if the node
        is None, it is NIL
        """

        if node:
            return node._color
        return RBColorEnum.NIL

    def get_parent_node(self, node):
        """
        Gets our Parent, has node validation
        """

        # We exist?
        if not node:
            return None

        # Return
        return node._parent

    def get_sibling_node(self, node):
        """
        Returns the sibling of the node, as well as the side it is on
        e.g
            20 (A)
           /     \
        15(B)    25(C)
        __get_sibling(25(C)) => 15(B), RBDirectionEnum.RIGHT
        """

        # Our Parent
        parent_node = self.get_parent_node(node)

        # Find the sibling!  If we have a Parent
        if parent_node:

            # We left or right?
            if parent_node._left == node:
                return parent_node._right, RBDirectionEnum.RIGHT
            else:
                return parent_node._left, RBDirectionEnum.LEFT

        # No parent, return none!
        else:
            return None

    def get_uncle_node(self, node):
        """
        Gets the Uncle of a given node
        """

        return self.get_sibling_node(self.get_parent_node(node))[0]

    def has_sibling_node(self, node):
        """
        Do we have a sibling?
        """

        if self.get_sibling_node(node)[0]:
            return True
        return False

    def in_order(self, node):
        """
        Returns a list of our Nodes from left to ride, in order.
        """

        # Gotta have one!
        if node:
            return (
                self.in_order(node._left) +
                [[node._key, node._values, node._parent, node._color]] +
                self.in_order(node._right)
            )

        # Return Empty
        return []

    def is_node_color(self, color, op, *nodes):
        """
        Takes in a color, an operator (from operator) and a
        single to multiple nodes.
        Sees if all given nodes are operator to the color.
        """

        return all(op(color, node._color) for node in nodes)

    def is_node_black(self, *nodes):
        """
        Are the given node(s), black?
        """

        return self.is_node_color(RBColorEnum.black, operator.eq, *nodes)

    def is_node_red(self, *nodes):
        """
        Are the given node(s) RED?
        """

        return self.is_node_color(RBColorEnum.RED, operator.eq, *nodes)

    def is_node_not_red(self, *nodes):
        """
        Are the givne node(s), not RED?
        """

        return self.is_node_color(RBColorEnum.RED, operator.ne, *nodes)

    def is_set_correctly(self, node):
        """
        Helper check function.
        Used to ensure we are a valid GY Tree
        """

        # If node is a leaf, check Property 2
        if not node:
            return True, 1

        # If node is the root, check Property 0
        if not self.get_parent_node(node) and self.is_node_red(node):
            return False, 0

        # If node is red, check Property 3
        if self.is_node_red(node):

            # Count of Green
            green_count = 0

            # Check our left/right children and see if they are YELLOW
            if (
                (node._left and self.is_node_red(node._left)) or
                (node._right and self.is_node_red(node._right))
            ):
                return False, -1

        # The number of GREEN nodes to the leaves includes the same node
        else:
            green_count = 1

        # Check the subtrees for Property 4
        right, green_count_right = self.is_set_correctly(node._right)
        left, green_count_left = self.is_set_correctly(node._left)

        # We all True?
        return all([right, left, green_count_right == green_count_left]),
        green_count_right + green_count

    def node_comparator(self, node_one, node_two):
        """
        Using our key comparator function, compares two nodes.
        """

        return self._key_comparator_function(node_one._key, node_two._key)

    def remove_key(self, key):
        """
        Try to get a node with 0 or 1 children.
        Either the node we're given has 0 or 1 children or we get
        its successor.
        """

        #  Grab our Node to Remove
        node_to_remove, _ = self.find_node(key)

        # Node is not in our tree?
        if node_to_remove is None:
            return

        # Pass along the node.
        self.remove_node(node_to_remove)

    def remove_node(self, node):
        """
        Given a node, removes it
        """

        # If our node has two children, we go left for our highest
        # successor, and replace us with them.
        if node.get_children_count() == 2:
            successor = self.get_minimum_node(node._right)
            node._key = successor._key
            node._values = successor._values
            node = successor

        # Has 0 or 1 children!
        self.__remove(node)

    def remove_value(self, key, value):
        """
        Given a Key/Value, tries to remove just the value from our RBTree
        If it is the lone Value of a node, removes the node as well.
        """

        # Get our node.
        node, _ = self.find_node(key)

        # Our value here?
        if value in node._values:
            node._values.remove(value)

        # Any values left?
        if len(node._values) == 0:
            self.remove_node(node)

    def rotate(
        self, direction, node, parent_node,
        grandparent_node, to_recolor=False
    ):
        """
        Rotate direction, given three nodes.
        """

        # Get our Great Grand Parent
        great_grandparent_node = self.get_parent_node(grandparent_node)

        # Update the parent.
        self.__update_parent(
            parent_node, grandparent_node,
            great_grandparent_node
        )

        # Stored Node
        stored_node = None

        if direction == RBDirectionEnum.LEFT:

            # Store and change.
            stored_node = parent_node._left
            parent_node._left = grandparent_node

            # Save the old left values
            grandparent_node._right = stored_node

        else:

            # Store and change.
            stored_node = parent_node._right
            parent_node._right = grandparent_node

            # Save the old right values
            grandparent_node._left = stored_node

        # Update Parents
        grandparent_node._parent = parent_node
        stored_node._parent = grandparent_node

        # Need to recolor?
        if to_recolor:
            parent_node._color = RBColorEnum.black
            node._color = RBColorEnum.RED
            grandparent_node._color = RBColorEnum.RED

    def try_rebalance(self, node):
        """
        Given a red child node, determine if there is a need to
        rebalance (if the parent is red)
        If there is, rebalance it
        """

        # Store our Parent and Grandparent
        parent_node = self.get_parent_node(node)
        grandparent_node = self.get_parent_node(parent_node)

        # Need to rebalance!
        if (
            parent_node is None or
            grandparent_node is None or
            (
                self.is_node_not_red(node) or
                self.is_node_not_red(parent_node)
            )
        ):
            return

        # What direction is our node from the parent?
        node_dir = (
            RBDirectionEnum.LEFT
            if self.node_comparator(node, parent_node)
            else RBDirectionEnum.RIGHT
        )
        parent_node_dir = (
            RBDirectionEnum.LEFT
            if self.node_comparator(parent_node, grandparent_node)
            else RBDirectionEnum.RIGHT
        )
        uncle_node = self.get_uncle_node(node)
        # grandparent_node._right if parent_node_dir == RBDirectionEnum.LEFT
        # else grandparent_node._left

        # General Direction we are going.
        general_direction = (node_dir, parent_node_dir)

        # Not a RED Uncle?
        if self.is_node_not_red(uncle_node):

            # Rotate
            if (general_direction == (
                    RBDirectionEnum.LEFT,
                    RBDirectionEnum.LEFT
            )):
                self.rotate(
                    RBDirectionEnum.RIGHT, node,
                    parent_node, grandparent_node, True)

            elif (general_direction == (
                    RBDirectionEnum.RIGHT,
                    RBDirectionEnum.RIGHT
            )):
                self.rotate(
                    RBDirectionEnum.LEFT, node,
                    parent_node, grandparent_node, True)

            elif (general_direction == (
                    RBDirectionEnum.LEFT,
                    RBDirectionEnum.RIGHT
            )):
                self.rotate(
                    RBDirectionEnum.RIGHT, None,
                    node, parent_node)
                # Due to the prev rotation, our node is now the parent
                self.rotate(
                    RBDirectionEnum.LEFT, parent_node,
                    node, grandparent_node, True)

            elif (general_direction == (
                    RBDirectionEnum.RIGHT,
                    RBDirectionEnum.LEFT
            )):
                self.rotate(
                    RBDirectionEnum.LEFT, None,
                    node, parent_node)
                # Due to the prev rotation, our node is now the parent
                self.rotate(
                    RBDirectionEnum.RIGHT, parent_node,
                    node, grandparent_node, True)

            else:
                raise Exception(
                                f"{general_direction}"
                                f" is not a valid direction!"
                )

        # Uncle is RED
        else:
            self.__recolor(grandparent_node)

    def update_key(self, key, value, new_key):
        """
        Given a key, updates a node by removing/adding
        """

        # Remove us.
        self.remove_value(key, value)

        # Add us
        self.add(new_key, value)

    def validate_key(self, key):
        """
        Calls our key validator function.
        """

        if not self._key_validator_function(key):
            raise Exception(f"Could not validate key: {key}!")
        else:
            return True

    def __recolor(self, grandparent):
        """
        Given a grandparent, pushes down black
        """

        # Push it!
        grandparent._right._color = RBColorEnum.black
        grandparent._left._color = RBColorEnum.black

        # Root is always black!
        if grandparent != self._root:
            grandparent._color = RBColorEnum.RED

        # Rebalance!
        self.try_rebalance(grandparent)

    def __remove(self, node):
        """
        Receives a node with 0 or 1 children (typically some sort of successor)
        and removes it according to its color/children
        :param node: RBNode with 0 or 1 children
        """

        # Grab a child
        # Looks left, then goes right.
        child_node = self.get_child_node(node)

        # We root?
        if node == self._root:

            # Valid child?
            if child_node != self.NIL_NODE:

                # If we're removing the root and it has one valid child,
                #  simply make that child the root
                self._root = child_node
                self._root._parent = None
                self._root._color = RBColorEnum.black

            else:
                self._root = None

        # We RED?
        elif self.is_node_red(node):

            # If we have children and we are red, just remove us.
            if not node.has_children():
                self.__remove_leaf(node)

            else:
                """
                Since the node is red he cannot have a child.
                If he had a child, it'd need to be black, but that would
                mean that the black height would be bigger on the one
                side and that would make our tree invalid
                """
                raise Exception("Unexpected behavior")

        # Node is black!
        else:

            # Grab our children.
            left_child_node = node._left
            right_child_node = node._right

            # Sanity Check
            if (
                right_child_node.has_children() or
                left_child_node.has_children()
            ):
                raise Exception(
                                "The red child of a black node with 0"
                                "or 1 children cannot have children, otherwise"
                                "the black height of the tree becomes invalid!"
                )

            # Our child RED?
            elif self.is_node_red(child_node):
                """
                Swap the values with the red child and remove it
                (basically un-link it) Since we're a node with one
                child only, we can be sure that there are no nodes
                below the red child.
                """

                node._key = child_node._key
                node._values = child_node._values
                node._left = child_node._left
                node._right = child_node._right

            # black child
            else:
                self.__remove_black_node(node)

    def __remove_leaf(self, node):
        """
        Simply removes a leaf node by making it's parent point to a NIL LEAF
        """

        # Get our parent
        parent_node = self.get_parent_node(node)

        # In those weird cases where they're equal due to the successor swap
        if (
            not self._key_comparator_function(node._key, parent_node._key) or
            self._key_equals_function(node._key, parent_node._key)
        ):
            parent_node._right = self.NIL_NODE
        else:
            parent_node._left = self.NIL_NODE

    def __remove_black_node(self, node):
        """
        Loop through each case recursively until we reach a terminating case.
        What we're left with is a leaf node which is ready to be deleted
        without consequences
        """

        self.__case_1(node)
        self.__remove_leaf(node)

    def __simple_key_comparator(self, key_one, key_two):
        """ Simple Key Comparator """

        return key_one < key_two

    def __simple_key_equals(self, key_one, key_two):
        """ Simple Key Equals """

        return key_one == key_two

    def __simple_key_validator(self, key):
        """ Simple Key Validator """

        return isinstance(key, int)

    def __update_parent(self, node, old_child_node, new_parent_node):
        """
        Our node 'switches' places with the old child
        Assigns a new parent to the node.
        If the new_parent is None, this means that our node becomes the root
        of the tree
        """

        # Set our new parent
        node._parent = new_parent_node

        # Did we bring along a parent?
        if new_parent_node:

            # Determine the old child's position in order to put node there
            if self._key_comparator_function(
                old_child_node._key,
                new_parent_node._key
            ):
                new_parent_node._left = node
            else:
                new_parent_node._right = node

        # We root!
        else:
            self._root = node

    def __case_1(self, node):
        r"""
        Case 1 is when there's a double black node on the root
        Because we're at the root, we can simply remove it
        and reduce the black height of the whole tree.
            __|10B|__                  __10B__
           /         \      ==>       /       \
          9B         20B            9B        20B
        """

        # We Root?  We black!
        if self._root == node:
            node._color = RBColorEnum.black
            return

        self.__case_2(node)

    def __case_2(self, node):
        r"""
        Case 2 applies when
            the parent is black
            the sibling is RED
            the sibling's children are black or NIL
        It takes the sibling and rotates it
                         40B                                              60B
                        /   \       --CASE 2 ROTATE-->                   /   \
                    |20B|   60R       LEFT ROTATE                     40R   80B
    DBL black IS 20----^   /   \      SIBLING 60R                     /   \
                         50B    80B                                |20B|  50B
            (if the sibling's direction was left of it's parent, we would
            RIGHT ROTATE it)
        Now the original node's parent is RED
        and we can apply case 4 or case 6
        """

        # Get our parent and sibling
        parent_node = self.get_parent_node(node)
        sibling_node, direction = self.get_sibling_node(node)

        # Our sibling RED, our parent is black, and our sibling doesn't have
        # RED children.
        if (
            self.is_node_red(sibling_node) and
            self.is_node_black(parent_node) and
            self.is_node_not_red(
                sibling_node._left,
                sibling_node._right
            )
        ):

            # Rotate us
            self.rotate(direction, None, sibling_node, parent_node)

            # Changes colors
            parent_node._color = RBColorEnum.RED
            sibling_node._color = RBColorEnum.black

            # Check Root
            return self.__case_1(node)

        # Next!
        self.__case_3(node)

    def __case_3(self, node):
        r"""
        Case 3 deletion is when:
            the parent is black
            the sibling is black
            the sibling's children are black
        Then, we make the sibling red and
        pass the double black node upwards
                            Parent is black
               ___50B___    Sibling is black                  ___50B___
              /         \   Sibling's children are black     /         \
           30B          80B        CASE 3                 30B        |80B|
          /   \        /   \        ==>                   /  \        /   \
        20B   35R    70B   |90B|<---REMOVE              20B  35R     70R   X
              /  \                                               /   \
            34B   37B                                          34B   37B
         Continue with other cases
        """

        # Get our parent and sibling
        parent_node = self.get_parent_node(node)
        sibling_node, _ = self.get_sibling_node(node)

        # Is our parent and sibling black, and neither of the
        # sibling's children RED?
        if (
            self.is_node_black(sibling_node, parent_node) and
            self.is_node_not_red(
                sibling_node._left,
                sibling_node._right
            )
        ):

            # Color the sibling red and forward the double black node upwards
            # (call the cases again for the parent)
            sibling_node._color = RBColorEnum.RED
            return self.__case_1(parent_node)

        self.__case_4(node)

    def __case_4(self, node):
        r"""
        If the parent is red and the sibling is black with no red children,
        simply swap their colors
        DB-Double Black
                __10R__                   __10B__
               /       \                 /       \
             DB        15B      ===>    X        15R
                      /   \                     /   \
                    12B   17B                 12B   17B
        The black height ofthe left subtree has been incremented
        And the on ebelow stays the same
        No consequences, we are done!
        """

        # Get our parent
        parent_node = self.get_parent_node(node)

        # Is our parent RED?
        if self.is_node_red(parent_node):

            # Get our sibling
            sibling_node, _ = self.get_sibling_node(node)

            # Is our sibling black and both of its children not RED?
            if (
                self.is_node_black(sibling_node) and
                self.is_node_not_red(
                    sibling_node._left,
                    sibling_node._right
                )
            ):

                # Switch Colors
                parent_node._color, sibling_node._color = sibling_node._color, parent_node._color

                # Terminating
                return

        self.__case_5(node)

    def __case_5(self, node):
        r"""
        Case 5 is a rotation that changes the circumstances so that we can do
        a case 6
        If the closer node is red and the outer black or NIL, we do a left/right
        rotation, depending on the orientation
        This will showcase when the CLOSER NODE's direction is RIGHT
              ___50B___
             /         \
           30B        |80B|  <-- Double black
          /  \        /   \      Closer node is red (35R)
        20B  35R     70R   X     Outer is black (20B)
            /   \                So we do a LEFT ROTATION
          34B  37B               on 35R (closer node)
                  __50B__
                 /       \
                35B      |80B|        Case 6 is now
              /   \      /           applicable here,
             30R    37B  70R           so we redirect the node
            /   \                      to it :)
          20B   34B
        """

        # Get our sibling and direction.
        sibling_node, direction = self.get_sibling_node(node)

        # Get our children.
        closer_node = (
            sibling_node._right
            if direction == RBDirectionEnum.LEFT
            else sibling_node._left
        )
        outer_node = (
            sibling_node._left
            if direction == RBDirectionEnum.LEFT
            else sibling_node._right
        )

        # Is our sibling black, the closer RED, and our outer not RED?
        if (
            self.is_node_red(closer_node) and
            self.is_node_not_red(outer_node) and
            self.is_node_black(sibling_node)
        ):

            # Rotate and set closer to black, setting sibling to RED
            self.rotate(direction, None, closer_node, sibling_node)
            closer_node._color = RBColorEnum.black
            sibling_node._color = RBColorEnum.RED

        self.__case_6(node)

    def __case_6(self, node):
        r"""
        Case 6 requires
            SIBLING to be black
            OUTER NODE to be RED
        Then, does a right/left rotation on the sibling
        This will showcase when the SIBLING's direction is LEFT
                            Double Black
                    __50B__       |                         __35B__
                   /       \      |                        /       \
      SIBLING--> 35B      |80B| <-                       30R       50R
                /   \      /                            /   \     /   \
             30R    37B  70R   Outer node is RED      20B   34B 37B    80B
            /   \              Closer node doesn't                     /
         20B   34B                 matter                            70R
                               Parent doesn't
                                   matter
                               So we do a right rotation on 35B!
        """

        # Get our sibling and direction
        sibling_node, direction = self.get_sibling_node(node)
        outer_node = (
            sibling_node._left
            if direction == RBDirectionEnum.LEFT
            else sibling_node._right
        )

        # Internal rotation, given a direction.
        def __case_6_rotation(direction):

            # Get parent's color
            parent_node = self.get_parent_node(sibling_node)._color
            parent_node_color = parent_node._color

            # Rotate our sibling and parent.
            self.rotate(direction, None, sibling_node, parent_node)

            # New parent is sibling
            sibling_node._color = parent_node_color
            sibling_node._right._color = RBColorEnum.black
            sibling_node._left._color = RBColorEnum.black

        # Is our sibling black and our outer RED?
        if self.is_node_black(sibling_node) and self.is_node_red(outer_node):
            return __case_6_rotation(direction)

        raise Exception('We should have ended here, something is wrong')


# I think this makes sure we are not used as a main file.
if __name__ == '__main__':
    pass