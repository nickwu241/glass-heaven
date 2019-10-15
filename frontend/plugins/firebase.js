import firebase from 'firebase/app'
import 'firebase/firestore'
const config = {
  projectId: 'easy-companies-overview'
}
firebase.initializeApp(config)
firebase.firestore().settings({})
const fsdb = firebase.firestore()
export { fsdb }
