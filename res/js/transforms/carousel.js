import { $, $$, getAttr } from "luett";
import delegate from "delegate";
import { range } from "lodash";
import stroll from "../util/stroll";

function create_scroller(el) {
    return stroll.factory(el);
}

function attach_nav(el, opts) {
    el.insertAdjacentHTML("beforeend", `
        <div class="${opts.css_nav}">
            <div>
                <button type="button" class="${opts.css_nav_btn} ${opts.css_nav_btn_prev}">
                    <i class="${opts.css_nav_btn_icon}"></i>
                </button>            
            </div>
            <div>
                <button type="button" class="${opts.css_nav_btn} ${opts.css_nav_btn_next}">
                    <i class="${opts.css_nav_btn_icon}"></i>
                </button>
            </div>
        </div>
    `);
}

function attach_index(el, opts, num_slides) {
    if(num_slides <= 1) {
        return;
    }

    el.insertAdjacentHTML("beforeend", `
        <ol class="${opts.css_index}">
            ${range(1, Math.min(num_slides + 1, 5)).map(idx => `
                <li>
                    <button type="button" class="${opts.css_index_btn}" data-carousel-index="${idx}"></button>
                </li>
            `).join("\n")}
        </ol>
    `);
}

function carousel(root, options) {
    const conf = Object.assign({}, carousel.DEFAULTS, options.conf);
    const iface = Object.create(null);
    const crsl = $(`.${conf.css_carousel}`, root);

    // create a default scroller
    let scroller = create_scroller(crsl);
    // configure noop emitter
    let emit = () => {};

    // set state
    let current_slide = 1;

    function unset_current() {
        $$(`.${conf.css_slides} > .${conf.css_current}`, root)
            .forEach((item) => item.classList.remove(conf.css_current));
    }

    function set_current(el) {
        el.classList.add(conf.css_current);
        return scroller({ x: el.offsetLeft, y: el.offsetTop });
    }

    function show_slide(idx) {
        const slide = $(`.${conf.css_slides} > :nth-child(${idx})`, root);

        if(!slide) return iface;

        root.classList.toggle(conf.css_slides_first, idx === 1);
        root.classList.toggle(conf.css_slides_last, idx === num_slides());

        const event_data = { index: idx, carousel: crsl, slide };

        emit("slide:start", event_data);
        unset_current();
        set_current(slide)
            .then(function() {
                emit("slide:end", event_data);
            });

        current_slide = idx;

        return iface;
    }

    function num_slides() {
        return $(`.${conf.css_slides}`).children.length;
    }

    iface.set_emitter = (emitter) => {
        emit = emitter;
        return iface;
    };

    iface.set_scroller = (factory) => {
        scroller = factory(crsl);
        return iface;
    };

    iface.show_slide = (idx) => {
        return show_slide(idx);
    };

    iface.next_slide = () => {
        return show_slide(current_slide + 1);
    };

    iface.prev_slide = () => {
        return show_slide(current_slide - 1);
    };

    delegate(root, `.${conf.css_nav_btn}`, "click", function(event) {
        event.preventDefault();

        if(event.delegateTarget.classList.contains(conf.css_nav_btn_prev)) {
            iface.prev_slide();
        }

        if(event.delegateTarget.classList.contains(conf.css_nav_btn_next)) {
            iface.next_slide();
        }
    });

    delegate(root, `.${conf.css_index_btn}`, "click", function(event) {
        event.preventDefault();
        const idx = parseInt(getAttr(event.delegateTarget, "data-carousel-index"), 10)
        show_slide(idx);
    });

    // add nav
    attach_nav(root, conf);
    attach_index(root, conf, num_slides());

    // set first slide as current but wait for carousel to return
    setTimeout(() => iface.show_slide(current_slide), 0);

    return iface;
}

carousel.DEFAULTS = {
    css_current: "carousel-current",
    css_slides: "carousel-slides",
    css_slides_first: "carousel-first",
    css_slides_last: "carousel-last",
    css_nav: "carousel-nav",
    css_nav_btn: "carousel-btn",
    css_nav_btn_icon: "carousel-btn-icon",
    css_nav_btn_prev: "carousel-btn-prev",
    css_nav_btn_next: "carousel-btn-next",
    css_carousel: "carousel",
    css_index: "carousel-index",
    css_index_btn: "carousel-btn-index"
};

export default carousel;
