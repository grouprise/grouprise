import Field from './field'
import List from './list'
import { has } from './util'
import comparison from './comparison'

const DEFAULT_COLORS = {
  plane: '#f1f3f5',
  text: '#495057',
  snake: '#2A62AC',
  prey: '#F6ED69'
}

const MOVEMENT_AXES = {
  left: 'y',
  right: 'y',
  up: 'x',
  down: 'x'
}

const MOVEMENTS = {
  left: ['up', 'down'],
  right: ['up', 'down'],
  up: ['left', 'right'],
  down: ['left', 'right']
}

const KEYS = {
  movement: {
        // arrows
    37: 'left',
    38: 'up',
    39: 'right',
    40: 'down',

        // wasd
    65: 'left',
    87: 'up',
    68: 'right',
    83: 'down'
  },
  control: {
        // misc
    32: 'playpause'
  }
}

class DeadSnake extends Error {}

function createPalette (ctx, colors) {
  return {
    fill: (type) => {
      ctx.fillStyle = colors[type]
    }
  }
}

function clearCanvas (canvas, palette) {
  const ctx = canvas.getContext('2d')
  palette.fill('plane')
  ctx.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight)
}

function renderFieldToCanvas (field, canvas, palette) {
  const ctx = canvas.getContext('2d')
  const size = canvas.clientWidth / field.size

  field.getFilled().forEach((tile) => {
    palette.fill(tile.val)
    ctx.fillRect(tile.pos[0] * size, tile.pos[1] * size, size, size)
  })
}

function Snake (field) {
  const iface = {}
  const tail = List(3)

  let direction = 'right'
  let currentPosition = [0, 0]

  function changeDirection (newDirection) {
    if (MOVEMENTS[direction].indexOf(newDirection) !== -1) {
      direction = newDirection
    }

    return iface
  }

  function move () {
        // what’s the next position
    const newPosition = field.neighbor(currentPosition, direction)

        // check if the tail has the new position
        // in case it has, we’ll eat our tail :)
    if (tail.has(newPosition, comparison.list)) {
      die(newPosition)
    }

        // it’s safe to proceed. add the new position to our tail :)
    tail.append(newPosition)
    currentPosition = newPosition
    return newPosition
  }

  function die (pos) {
    throw new DeadSnake(pos)
  }

  function eat () {
    tail.increment()
    return iface
  }

  Object.defineProperty(iface, 'direction', {
    get: () => direction
  })

  Object.assign(iface, {
    move,
    eat,
    tail,
    left: changeDirection.bind(null, 'left'),
    up: changeDirection.bind(null, 'up'),
    right: changeDirection.bind(null, 'right'),
    down: changeDirection.bind(null, 'down')
  })

  return iface
}

function Game (canvas, opts = {}) {
  opts = Object.assign({}, { size: 100, tickInterval: 75, colors: DEFAULT_COLORS, fontSize: 12 }, opts || {})

  const iface = {}
  const ctx = canvas.getContext('2d')
  const center = Math.floor(opts.size / 2)
  const palette = createPalette(ctx, opts.colors)
  const playground = Field(opts.size)
  const snake = Snake(playground)
  const prey = List()

  let lastTick = 0
  let isPaused = false
  let frame = null
  let points = 0

  ctx.font = `600 ${opts.fontSize}px/1 sans-serif`

  function tick (time) {
    if (time >= lastTick + opts.tickInterval) {
      if (!isPaused) {
        if (advance()) {
          return
        }
      }

      render()
      lastTick = time
    }

    frame = window.requestAnimationFrame(tick)
  }

  function finish () {
    ctx.textAlign = 'center'
    ctx.font = `700 ${opts.fontSize * 3}px/1 sans-serif`
    ctx.fillText('Game Over', canvas.clientWidth / 2, canvas.clientHeight / 2)
    opts.onFinish && opts.onFinish()
    unbind()
  }

  function newPrey (pos) {
    prey.append(pos || playground.empty())
    playground.replace(prey.values, 'prey')
  }

  function advance () {
    try {
      const pos = snake.move()

      if (prey.has(pos, comparison.list)) {
        snake.eat(pos)
        points++
        newPrey()
      }
    } catch (e) {
      finish()
      return true
    }

    playground.replace(snake.tail.values, 'snake')
  }

  function render () {
    clearCanvas(canvas, palette)
    renderFieldToCanvas(playground, canvas, palette)
    palette.fill('text')
    ctx.fillText(`Points: ${points}${isPaused ? ' | Paused' : ''}`, 8, 6 + opts.fontSize)
  }

  function input (event) {
    const keyCode = event.keyCode

    if (has(KEYS.movement, keyCode) && !isPaused) {
      snake[KEYS.movement[keyCode]].call()
      event.preventDefault()
    }

    if (has(KEYS.control, keyCode)) {
      iface[KEYS.control[keyCode]].call()
      event.preventDefault()
    }
  }

  function click (event) {
    const canvasRect = canvas.getBoundingClientRect()
    const movements = MOVEMENTS[snake.direction]
    const movementAxis = MOVEMENT_AXES[snake.direction]
    const pos = {
      x: (event.clientX - canvasRect.left) / canvas.clientWidth * 100,
      y: (event.clientY - canvasRect.top) / canvas.clientHeight * 100
    }[movementAxis]

    snake[movements[pos < 50 ? 0 : 1]].call()
  }

  function playpause () {
    isPaused = !isPaused
    return iface
  }

  function bind () {
    newPrey([center, center])
    canvas.addEventListener('click', click, false)
    document.addEventListener('keydown', input, false)
    frame = window.requestAnimationFrame(tick)
    return iface
  }

  function unbind () {
    canvas.removeEventListener('click', click, false)
    document.removeEventListener('keydown', input, false)
    window.cancelAnimationFrame(frame)
    return iface
  }

  Object.assign(iface, { bind, unbind, playpause })
  return iface
}

export default Game
