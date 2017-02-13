import Group from './group'
import Gestalt from './gestalt'
import GestaltSettings from './gestalt-settings'
import Image from './image'
import Markdown from './markdown'

export const image = Image()
export const group = Group()
export const gestalt = Gestalt()
export const gestaltSettings = GestaltSettings()
export const markdown = Markdown()

export default ({group, gestalt, image, gestaltSettings, markdown})
