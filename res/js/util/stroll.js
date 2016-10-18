'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) {
  return typeof obj;
} : function (obj) {
  return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj;
};

function create_options(defaults, options, adapter) {
    return Object.assign({
        ignore_user_scroll: false,
        allow_invalid_positions: false,
        offset: { x: 0, y: 0 },
        duration: 500,
        focus: true,
        // Robert Penner's easeInOutQuad - http://robertpenner.com/easing/
        easing: function easing(t, b, c, d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        }
    }, defaults, options, {
        start: adapter.get_current_position()
    });
}

function resolve_duration(duration, distance) {
    var type = typeof duration === "undefined" ? "undefined" : _typeof(duration);

    if (type === "number") return duration;
    if (type === "function") return duration(distance);

    var parsed = parseFloat(duration);

    if (isNaN(parsed)) {
        throw new Error("invalid duration");
    }

    return parsed;
}

function resolve_offset(offset, adapter) {
    var type = typeof offset === "undefined" ? "undefined" : _typeof(offset);

    if (type === "number") {
        return adapter.create_pos_from_number(offset);
    }

    if (type === "object") {
        if (typeof offset.x === "undefined") offset.x = 0;
        if (typeof offset.y === "undefined") offset.y = 0;

        return offset;
    }

    throw new Error("invalid offset");
}

function pos_abs(distance) {
    return { x: Math.abs(distance.x), y: Math.abs(distance.y) };
}

function pos_cmp(pos1, pos2) {
    return pos1.x === pos2.x && pos1.y === pos2.y;
}

function pos_add(pos1, pos2) {
    return { x: pos1.x + pos2.x, y: pos1.y + pos2.y };
}

function ease(easing, time_elapsed, start, target, duration) {
    return {
        x: Math.round(easing(time_elapsed, start.x, target.x, duration)),
        y: Math.round(easing(time_elapsed, start.y, target.y, duration))
    };
}

function create_loop(stroll, options) {
    var adapter = options.adapter;

    function start_loop(resolve) {
        var animation_frame = void 0;
        var time_start = void 0;
        var last_pos = void 0;

        function loop(time_current) {
            if (!time_start) {
                time_start = time_current;
            }

            var time_elapsed = time_current - time_start;
            var new_pos = ease(options.easing, time_elapsed, options.start, options.target, options.duration);

            if (!options.allow_invalid_positions && adapter.is_pos_outside_el(new_pos)) {
                return stroll.current_stroll("invalid_position");
            }

            if (!options.ignore_user_scroll && last_pos && !pos_cmp(last_pos, adapter.get_current_position())) {
                return stroll.current_stroll("user_scrolled");
            }

            if (time_elapsed > options.duration) {
                done(resolve);
            } else {
                adapter.scroll_to(new_pos);
                last_pos = adapter.get_current_position();
                next();
            }
        }

        function next() {
            animation_frame = requestAnimationFrame(loop);
        }

        if (stroll.current_stroll) {
            stroll.current_stroll("new_stroll");
        }

        next();

        return stroll.current_stroll = function (cancel_reason) {
            cancelAnimationFrame(animation_frame);
            resolve({ was_cancelled: true, cancel_reason: cancel_reason });
        };
    }

    function done(resolve) {
        stroll.current_stroll = null;

        // easing might create small offsets from the requested target
        adapter.scroll_to(pos_add(options.start, options.target));

        // keyboard navigation might reset the scroll position
        // this sets focus to the element to prevent such problems
        if (options.element && options.focus) {
            if (!options.element.hasAttribute("tabindex")) {
                options.element.setAttribute("tabindex", "-1");
            }

            options.element.focus();
        }

        resolve({ was_cancelled: false });
    }

    return { start: start_loop };
}

function create_stroller(adapter) {
    function stroll(target) {
        var options = arguments.length <= 1 || arguments[1] === undefined ? {} : arguments[1];

        return new Promise(function (resolve) {
            var stroll_options = create_options(stroll.DEFAULTS, options, adapter);
            var offset = resolve_offset(stroll_options.offset, adapter);
            var stroll_target = adapter.resolve_target(target, stroll_options.start, offset);
            var duration = resolve_duration(stroll_options.duration, pos_abs(stroll_target.target));
            var loop = create_loop(stroll, Object.assign({}, stroll_options, stroll_target, {
                duration: duration, offset: offset, adapter: adapter
            }));

            loop.start(resolve);
        });
    }

    stroll.current_stroll = null;
    stroll.relative = function (offset) {
        var options = arguments.length <= 1 || arguments[1] === undefined ? {} : arguments[1];
        return stroll(null, Object.assign({ offset: offset }, options));
    };
    stroll.DEFAULTS = {};

    return stroll;
}

function resolve_target_factory(el, create_pos_from_number) {
    return function resolve_target(user_target, start, offset) {
        var type = typeof user_target === "undefined" ? "undefined" : _typeof(user_target);
        var target = type === "string" ? el.querySelector(user_target) : user_target;
        var result = {};

        if (user_target === null || type === "undefined") {
            var zero = { x: 0, y: 0 };
            return resolve_target(offset, zero, zero);
        }

        if (type === "number") {
            var pos = create_pos_from_number(user_target);

            // add start and offset to axes, that are not 0 by default
            pos.x = pos.x - start.x + offset.x;
            pos.y = pos.y - start.y + offset.y;

            result.target = pos;
            result.focus = false;
            return result;
        }

        if (type === "object") {
            result.target = {
                x: (user_target.x || 0) - start.x + offset.x,
                y: (user_target.y || 0) - start.y + offset.y
            };
            result.focus = false;
            return result;
        }

        if (!target || !target.getBoundingClientRect) {
            throw new Error("invalid target");
        }

        var bounding_rect = target.getBoundingClientRect();
        result.element = target;
        result.target = {
            x: bounding_rect.left + offset.x,
            y: bounding_rect.top + offset.y
        };

        return result;
    };
}

function create_pos_from_number_factory(calculate_maxima) {
    return function (number) {
        var maxima = calculate_maxima();
        var primary_axis = maxima.y > maxima.x ? "y" : "x";
        var result = {};

        result[primary_axis] = number;
        result[primary_axis === "x" ? "y" : "x"] = 0;

        return result;
    };
}

function is_pos_outside_el_factory(calculate_maxima) {
    return function (pos) {
        if ((typeof pos === "undefined" ? "undefined" : _typeof(pos)) !== "object") return true;
        var maxima = calculate_maxima();
        return pos.x < 0 || pos.x > maxima.x || pos.y < 0 || pos.y > maxima.y;
    };
}

function create_base_adapter(el, calculate_maxima) {
    var create_pos_from_number = create_pos_from_number_factory(calculate_maxima);
    var is_pos_outside_el = is_pos_outside_el_factory(calculate_maxima);
    var resolve_target = resolve_target_factory(el, create_pos_from_number);

    return { create_pos_from_number: create_pos_from_number, resolve_target: resolve_target, is_pos_outside_el: is_pos_outside_el };
}

function create_window_adapter() {
    function calculate_maxima() {
        var doc_width = Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth) - window.innerWidth;
        var x = Math.max(0, doc_width);

        var doc_height = Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight) - window.innerHeight;
        var y = Math.max(0, doc_height);

        return { x: x, y: y };
    }

    return Object.assign(create_base_adapter(document, calculate_maxima), {
        get_current_position: function get_current_position() {
            return {
                x: window.scrollX || window.pageXOffset,
                y: window.scrollY || window.pageYOffset
            };
        },
        scroll_to: function scroll_to(pos) {
            window.scrollTo(pos.x, pos.y);
        }
    });
}

function create_element_adapter(el) {
    function calculate_maxima() {
        return {
            x: Math.max(0, el.scrollWidth - el.clientWidth),
            y: Math.max(0, el.scrollHeight - el.clientHeight)
        };
    }

    return Object.assign(create_base_adapter(el, calculate_maxima), {
        get_current_position: function get_current_position() {
            return { x: el.scrollLeft, y: el.scrollTop };
        },
        scroll_to: function scroll_to(pos) {
            el.scrollLeft = pos.x;
            el.scrollTop = pos.y;
        }
    });
}

var public_adapters = {
    element: create_element_adapter
};

var stroll = create_stroller(create_window_adapter());

stroll.factory = function (el) {
    var adapter = arguments.length <= 1 || arguments[1] === undefined ? "element" : arguments[1];

    if (typeof adapter === "string") {
        adapter = public_adapters[adapter];
    }

    return create_stroller(adapter(el));
};

module.exports = stroll;