import Group from './group'
import Author from './author'
import api from '../api'

const group = Group(api.group)
const author = Author(api.gestalt, window.app.conf.gestalt.id, group)

export default ({group, author})
