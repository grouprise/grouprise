import Snake from "../game/snake";

export default (el) => {
    el.width = el.clientWidth;
    el.height = el.clientWidth;

    const game = Snake(el, { size: 40 });
    game.bind();

    return game;
}
