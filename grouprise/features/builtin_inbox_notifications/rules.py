from rules import add_perm, is_authenticated

add_perm("associations.list_activity", is_authenticated)
