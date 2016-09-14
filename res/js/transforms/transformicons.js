const tcon = {};
const _transformClass = "tcon-transform";
const DEFAULT_EVENTS = {
    transform : ["click"],
    revert : ["click"]
};

function getElementList(elements) {
    if (typeof elements === "string") {
        return Array.prototype.slice.call(document.querySelectorAll(elements));
    } else if (typeof elements === "undefined" || elements instanceof Array) {
        return elements;
    } else {
        return [elements];
    }
}

function getEventList(events) {
    if (typeof events === "string") {
        return events.toLowerCase().split(" ");
    } else {
        return events;
    }
}

function setListeners(elements, events, remove) {
    const method = (remove ? "remove" : "add") + "EventListener";
    const elementList = getElementList(elements);
    const eventLists = {};
    let currentElement = elementList.length;

    // get events or use defaults
    for (const prop in DEFAULT_EVENTS) {
        eventLists[prop] = (events && events[prop]) ? getEventList(events[prop]) : DEFAULT_EVENTS[prop];
    }

    // add or remove all events for all occasions to all elements
    while(currentElement--) {
        for (const occasion in eventLists) {
            let currentEvent = eventLists[occasion].length;
            
            while(currentEvent--) {
                elementList[currentElement][method](eventLists[occasion][currentEvent], handleEvent);
            }
        }
    }
}

function handleEvent(event) {
    tcon.toggle(event.currentTarget);
}

tcon.add = function (elements, events) {
    setListeners(elements, events);
    return tcon;
};

tcon.remove = function (elements, events) {
    setListeners(elements, events, true);
    return tcon;
};

tcon.transform = function (elements) {
    getElementList(elements).forEach(function(element) {
        element.classList.add(_transformClass);
    });
    return tcon;
};

tcon.revert = function (elements) {
    getElementList(elements).forEach(function(element) {
        element.classList.remove(_transformClass);
    });
    return tcon;
};

tcon.toggle = function (elements) {
    getElementList(elements).forEach(function(element) {
        tcon[element.classList.contains(_transformClass) ? "revert" : "transform"](element);
    });
    return tcon;
};

export default (el) => {
    tcon.add(el);
};
