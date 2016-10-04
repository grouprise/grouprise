import Field from "./field";
import List from "./list";
import { has } from "./util";
import comparison from "./comparison";

const DEFAULT_COLORS = {
    plane: "#f1f3f5",
    text: "#495057",
    snake: "#2A62AC",
    prey: "#F6ED69"
};

const MOVEMENT_AXES = {
    left: "y", right: "y",
    up: "x", down: "x"
};

const MOVEMENTS = {
    left: ["up", "down"],
    right: ["up", "down"],
    up: ["left", "right"],
    down: ["left", "right"]
};

const KEYS = {
    movement: {
        // arrows
        37: "left",
        38: "up",
        39: "right",
        40: "down",

        // wasd
        65: "left",
        87: "up",
        68: "right",
        83: "down",
    },
    control: {
        // misc
        32: "playpause",
    }
};

class DeadSnake extends Error {}

function create_palette(ctx, colors) {
    return {
        fill: (type) => {
            ctx.fillStyle = colors[type];
        }
    }
}

function clear_canvas(canvas, palette) {
    const ctx = canvas.getContext("2d");
    palette.fill("plane");
    ctx.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight);
}

function render_field_to_canvas(field, canvas, palette) {
    const ctx = canvas.getContext("2d");
    const size = canvas.clientWidth / field.size;

    field.get_filled().forEach((tile) => {
        palette.fill(tile.val);
        ctx.fillRect(tile.pos[0] * size, tile.pos[1] * size, size, size);
    });
}

function Snake(field) {
    const iface = {};
    const tail = List(3);

    let direction = "right";
    let current_pos = [0, 0];

    function change_direction(new_direction) {
        if(MOVEMENTS[direction].indexOf(new_direction) !== -1) {
            direction = new_direction;
        }

        return iface;
    }

    function move() {
        // what’s the next position
        const new_pos = field.neighbor(current_pos, direction);

        // check if the tail has the new position
        // in case it has, we’ll eat our tail :)
        if(tail.has(new_pos, comparison.list)) {
            die(new_pos);
        }

        // it’s safe to proceed. add the new position to our tail :)
        tail.append(new_pos);
        current_pos = new_pos;
        return new_pos;
    }

    function die(pos) {
        throw new DeadSnake(pos);
    }

    function eat() {
        tail.increment();
        return iface;
    }

    Object.defineProperty(iface, "direction", {
        get: () => direction
    });

    Object.assign(iface, {
        move, eat, tail,
        left: change_direction.bind(null, "left"),
        up: change_direction.bind(null, "up"),
        right: change_direction.bind(null, "right"),
        down: change_direction.bind(null, "down"),
    });

    return iface;
}

function Game(canvas, opts = {}) {
    opts = Object.assign({}, { size: 100, tick_interval: 75, colors: DEFAULT_COLORS, font_size: 12 }, opts || {});

    const iface = {};
    const ctx = canvas.getContext("2d");
    const center = Math.floor(opts.size / 2);
    const palette = create_palette(ctx, opts.colors);
    const playground = Field(opts.size);
    const snake = Snake(playground);
    const prey = List();

    let last_tick = 0;
    let is_paused = false;
    let frame = null;
    let points = 0;

    ctx.font = `600 ${opts.font_size}px/1 sans-serif`;

    function tick(time) {
        if(time >= last_tick + opts.tick_interval)  {
            if(!is_paused) {
                if(advance()) {
                    return;
                }
            }

            render();
            last_tick = time;
        }

        frame = requestAnimationFrame(tick);
    }

    function finish() {
        ctx.textAlign = "center";
        ctx.font = `700 ${opts.font_size * 3}px/1 sans-serif`;
        ctx.fillText("Game Over", canvas.clientWidth / 2, canvas.clientHeight / 2);
        unbind();
    }

    function new_prey(pos) {
        prey.append(pos || playground.empty());
        playground.replace(prey.values, "prey");
    }

    function advance() {
        try {
            const pos = snake.move();

            if(prey.has(pos, comparison.list)) {
                snake.eat(pos);
                points++;
                new_prey();
            }
        } catch(e) {
            finish();
            return true;
        }

        playground.replace(snake.tail.values, "snake");
    }

    function render() {
        clear_canvas(canvas, palette);
        render_field_to_canvas(playground, canvas, palette);
        palette.fill("text");
        ctx.fillText(`Points: ${points}${is_paused ? " | Paused" : ""}`, 8, 6 + opts.font_size);
    }
    
    function input(event) {
        const key_code = event.keyCode;

        if(has(KEYS.movement, key_code) && !is_paused) {
            snake[KEYS.movement[key_code]].call();
            event.preventDefault();
        }

        if(has(KEYS.control, key_code)) {
            iface[KEYS.control[key_code]].call();
            event.preventDefault();
        }
    }

    function click(event) {
        const canvas_rect = canvas.getBoundingClientRect();
        const movements = MOVEMENTS[snake.direction];
        const movement_axis = MOVEMENT_AXES[snake.direction];
        const pos = {
            x: (event.clientX - canvas_rect.left) / canvas.clientWidth * 100,
            y: (event.clientY - canvas_rect.top) / canvas.clientHeight * 100
        }[movement_axis];
        
        snake[movements[pos < 50 ? 0 : 1]].call();
    }

    function playpause() {
        is_paused = !is_paused;
        return iface;
    }

    function bind() {
        new_prey([center, center]);
        canvas.addEventListener("click", click, false);
        document.addEventListener("keydown", input, false);
        frame = requestAnimationFrame(tick);
        return iface;
    }

    function unbind() {
        canvas.removeEventListener("click", click, false);
        document.removeEventListener("keydown", input, false);
        cancelAnimationFrame(frame);
        return iface;
    }

    Object.assign(iface, { bind, unbind, playpause });
    return iface;
}

export default Game;
