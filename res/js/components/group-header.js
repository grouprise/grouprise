import { $ } from "../util/dom";

export default (el) => {
    const height = $(".group-info", el).clientHeight;
    const style = document.createElement("style");
    style.innerHTML = `.group-gallery .carousel-slides > li img { min-height: ${height}px; }`;
    document.head.appendChild(style);
};
