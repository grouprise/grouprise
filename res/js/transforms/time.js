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

function transform_to(el, opts) {
    return () => {
        el.innerHTML = moment(opts.conf.ref || new Date()).to(el.getAttribute("datetime"));
    };
}

function transform_days_until(el, opts) {
    return () => {
        const days = moment(el.getAttribute("datetime")).diff(opts.conf.ref || new Date(), "days");
        el.setAttribute("data-days", days);
        el.innerHTML = moment(el.getAttribute("datetime")).diff(opts.conf.ref || new Date(), "days");
    };
}

function create_transform(el, opts) {
    if(opts.is_type("from")) {
        return add_transform(transform_from(el, opts));
    }

    if(opts.is_type("to")) {
        return add_transform(transform_to(el, opts));
    }

    if(opts.is_type("days-until")) {
        return add_transform((transform_days_until(el, opts)));
    }
}

setInterval(transform_now, 60 * 1000);

export default create_transform;
