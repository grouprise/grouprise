# Django-Shell

The console-based interface of the django shell allows *any* kind of interaction with the *grouprise* data.

A good understanding of Python and Django are highly recommended if you want to use this interface for advanced data surgery operations.
In all other cases you should use the [Django-Admin web interface](/management/django_admin) or the [Matrix-Commander](/management/matrix_commander) instead.

## Enter the shell

Execute the following on *grouprise* host:

```shell
grouprisectl shell
```

Now you may enter arbitrary Python statements within your configured Django environment:
```python
from grouprise.features.gestalten.models import Gestalt
print(Gestalt.objects.count())
```
