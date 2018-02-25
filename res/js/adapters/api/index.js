import Gestalt from './gestalt'
import GestaltSettings from './gestalt-settings'
import Group from './group'
import Image from './image'
import Markdown from './markdown'
import Poll from './poll'

export const gestalt = Gestalt()
export const gestaltSettings = GestaltSettings()
export const group = Group()
export const image = Image()
export const markdown = Markdown()
export const poll = Poll()

export default ({gestalt, gestaltSettings, group, image, markdown, poll})
