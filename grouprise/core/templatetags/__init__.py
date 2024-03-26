from collections import namedtuple
import functools
from inspect import getfullargspec, unwrap
from typing import Optional

from django.template.library import parse_bits, Library, TagHelperNode


Link = namedtuple("Link", "text url")


class ContextNode(TagHelperNode):
    def __init__(self, nodelist, func, takes_context, args, kwargs):
        super().__init__(func, takes_context, args, kwargs)
        self.nodelist = nodelist

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def render(self, context):
        resolved_args, resolved_kwargs = self.get_resolved_arguments(context)
        _dict = self.func(*resolved_args, **resolved_kwargs)
        with context.push(**_dict):
            return self.nodelist.render(context)


def context_tag(
    library: Library, takes_context: Optional[bool] = None, name: Optional[str] = None
):
    """
    This works similar to a with tag, but instead of defining new context in the template
    it injects parameterizable-context through the logic of the wrapped tag function.
    """
    def decorator(func):
        params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(unwrap(func))
        function_name = (name or getattr(func, "_decorated_function", func).__name__)

        @functools.wraps(func)
        def compile_func(parser, token):
            bits = token.split_contents()[1:]
            args, kwargs = parse_bits(
                parser, bits, params, varargs, varkw, defaults,
                kwonly, kwonly_defaults, takes_context, function_name,
            )
            nodelist = parser.parse((f"end{function_name}",))
            parser.delete_first_token()
            return ContextNode(nodelist, func, takes_context, args, kwargs)
        library.tag(function_name, compile_func)
        return func
    return decorator
