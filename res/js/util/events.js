import EventEmitter from "eventemitter2";

function evented(obj) {
    Object.assign(obj, EventEmitter.prototype);
    return obj;
}

function evented_function(func) {
    function wrapper() {
        wrapper.emit("dispatch", arguments);
        const result = func.apply(this, arguments);
        wrapper.emit("call", result);
        return result;
    }
    evented(wrapper);
    return wrapper;
}

export { evented, evented_function };
