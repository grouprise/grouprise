import moment from "moment";

// load locale files
import de from "moment/locale/de";

// initialize locale
moment.locale("de");

const transforms = [];

function transform_now(index = null) {
    if(index) {
        transforms[index]();
    } else {
        transforms.forEach((transform) => transform());
    }
}

function add_transform(transform) {
    const index = transforms.push(transform) - 1;
    transform_now(index);
    return transform;
}

function transform_from(el, opts) {
    return () => {
        el.innerHTML = moment(el.getAttribute("datetime")).from(opts.conf.ref || new Date());
    };
}

function create_transform(el, opts) {
    if(opts.is_type("from")) {
        return add_transform(transform_from(el, opts));
    }
}

setInterval(transform_now, 60 * 1000);

export default create_transform;
