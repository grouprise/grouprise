import qwest from "qwest";
import cookie from "cookie_js";

const endpoint = "/stadt/api/images/";

function transform(file) {
    return {
        id: file.id,
        label: file.title,
        content: file.file
    };
}

export function get(opts = {}) {
    return function() {
        return qwest.get(endpoint, opts.filters)
            .then((xhr, files) => {
                return Promise.resolve(files.map(transform));
            });
    }
}

export function create(opts = {}) {
    return function(file) {
        file = Object.assign({}, opts, file);

        const data = new FormData();
        data.set("file", file.content);
        data.set("weight", file.weight || 0);
        data.set("csrfmiddlewaretoken", cookie.get("csrftoken"));

        if(file.content_id) {
            data.set("content", file.content_id);
        }

        return qwest.post(endpoint, data)
            .then((xhr, data) => {
                return Promise.resolve(transform(data));
            });
    };
}

export function update(opts = {}) {
    return function(file) {
        const _data = Object.assign({}, opts, file);
        const data = {};

        data.id = _data.id;
        data.weight = _data.weight;

        if(_data.content_id) {
            data.content = _data.content_id;
        }

        return qwest.put(endpoint, data)
            .then((xhr, data) => {
                return Promise.resolve(transform(data));
            });
    }
}
