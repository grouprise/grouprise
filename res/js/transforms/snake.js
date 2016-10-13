import Snake from "../game/snake";

export default (el, conf = {}) => {
    const width = el.getBoundingClientRect().width;
    el.width = width;
    el.height = width;

    const game = Snake(el, Object.assign({ size: 40 }, conf));
    game.bind();

    return game;
}
