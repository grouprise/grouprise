import emoji_regex from "emoji-regex";

const filters = [
    function emoji(content) {
        return content.replace(emoji_regex(), "<span class='emoji' data-emoji='$&'></span>");
    }
];

export default (el, opts) => {
    const orig_content = el.innerHTML;
    el.innerHTML = filters.reduce((content, filter) => filter(content, opts), orig_content); 

    return {
        restore() { el.innerHTML = orig_content }
    }
};
