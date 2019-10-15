import firebase from 'firebase/app'
import 'firebase/analytics'
import 'firebase/firestore'

// Your web app's Firebase configuration
var firebaseConfig = {
  apiKey: 'AIzaSyC6VHOu72_ds4prumJ4ccxiiFjTEwpmwgQ',
  authDomain: 'glass-heaven.firebaseapp.com',
  databaseURL: 'https://glass-heaven.firebaseio.com',
  projectId: 'glass-heaven',
  storageBucket: 'glass-heaven.appspot.com',
  messagingSenderId: '91985148506',
  appId: '1:91985148506:web:0835012af908114dd57663',
  measurementId: 'G-ZSN1VRN4MY'
}

// Initialize Firebase
firebase.initializeApp(firebaseConfig)
firebase.analytics()

const db = firebase.firestore()
export { db }
