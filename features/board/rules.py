from rules import add_perm

from features.associations import predicates as associations


add_perm('board.create', associations.is_public)
