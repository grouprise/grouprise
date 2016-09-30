import bel from "bel";
import delegate from "delegate";

import { $, $$, each, get_attr, index } from "../util/dom";

import Photoswipe from "photoswipe";
import theme from "photoswipe/dist/photoswipe-ui-default";

function attach_template() {
    const template = bel`
<div class="pswp" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="pswp__bg"></div>
    <div class="pswp__scroll-wrap">
        <div class="pswp__container">
            <div class="pswp__item"></div>
            <div class="pswp__item"></div>
            <div class="pswp__item"></div>
        </div>
        <div class="pswp__ui pswp__ui--hidden">
            <div class="pswp__top-bar">
                <div class="pswp__counter"></div>
                
                <button class="pswp__button pswp__button--close sg sg-close" title="Schließen (Esc)"></button>
                <button class="pswp__button pswp__button--share sg sg-share" title="Teilen"></button>
                <button class="pswp__button pswp__button--fs sg sg-fullscreen" title="Vollbild umschalten"></button>
                <button class="pswp__button pswp__button--zoom sg sg-zoom" title="Rein/Raus Zoomen"></button>
                
                <div class="pswp__preloader">
                    <div class="pswp__preloader__icn">
                      <div class="pswp__preloader__cut">
                        <div class="pswp__preloader__donut"></div>
                      </div>
                    </div>
                </div>
            </div>
            
            <div class="pswp__share-modal pswp__share-modal--hidden pswp__single-tap">
                <div class="pswp__share-tooltip"></div> 
            </div>
            
            <button class="pswp__button pswp__button--arrow--left sg sg-left" title="Vorheriges Bild"></button>
            <button class="pswp__button pswp__button--arrow--right sg sg-right" title="Nächstes Bild"></button>
            
            <div class="pswp__caption">
                <div class="pswp__caption__center"></div>
            </div>
        </div>
    </div>
</div>`;

    document.body.appendChild(template);
    return template
}

function calculate_bounding(images, index) {
    const image = images[index];
    const pageYScroll = window.pageYOffset || document.documentElement.scrollTop;
    const rect = image.getBoundingClientRect();

    return {
        x: rect.left,
        y: rect.top + pageYScroll,
        w: rect.width
    };
}

function create_lightbox(gallery) {
    const image_selector = "[href]";
    const image_els = $$(image_selector, gallery);
    const images = each(image_els, (el) => {
        const [ w, h ]= each(get_attr(el, "data-size").split("x"), parseInt);
        return {
            msrc: get_attr($("img", el), "src"),
            src: get_attr(el, "href"),
            w, h
        }
    });

    function show(start_with_index = 0) {
        const template = attach_template();
        const lightbox = new Photoswipe(template, theme, images, {
            index: start_with_index,
            getThumbBoundsFn: calculate_bounding.bind(null, image_els),
            // getDoubleTapZoom: () => 1,
            // maxSpreadZoom: 1,
            // zoomEl: false,
            shareEl: false
        });

        lightbox.listen("destroy", function() {
            document.body.removeChild(template);
        });

        lightbox.init();
    }

    const cleanup_click_listener = delegate(gallery, image_selector, "click", function(e) {
        e.preventDefault();
        const target_index = index(e.delegateTarget.parentNode);
        show(target_index)
    });

    return {
        show: show,
        remove: () => {
            cleanup_click_listener();
        }
    }
}

export default (el) => {
    return create_lightbox($(".gallery", el));
}
