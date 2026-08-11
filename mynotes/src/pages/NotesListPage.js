import React, { useState, useEffect } from 'react'
import ListItem from '../components/ListItem.js'
import AddButton from '../components/AddButton.js'

const NotesListPage = () => {
    let [notes, setNotes] = useState([])
    let [loading, setLoading] = useState(true)
    let [error, setError] = useState("")

    useEffect(() => {
        getNotes()
    }, []) // fires once when the component is mounted

    let getNotes = async () => {
        try {
            let response = await fetch('/api/notes/')
            let data = await response.json()
            setNotes(data)
        } catch (fetchError) {
            setError("Unable to load notes right now.")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className='notes'>
            <div className="notes-header">
                <div>
                    <p className="notes-eyebrow">Workspace overview</p>
                    <h2 className="notes-title">
                        &#9782; Notes
                    </h2>
                </div>
                <p className="notes-count">{notes.length}</p>
            </div>
            <p className="notes-intro">
                A lean notes service with Docker, Gunicorn, Django REST, and Kubernetes probes baked in.
            </p>
            <div className='notes-list'>
                {loading && <p className="empty-state">Loading notes...</p>}
                {error && <p className="empty-state error">{error}</p>}
                {!loading && !error && notes.length === 0 && (
                    <p className="empty-state">No notes yet. Create the first one.</p>
                )}
                {notes.map((note,index) => {
                    return (
                        <div className='note-preview' key={index}>
                            <ListItem note={note}/>
                        </div>
                    )
                })}
            </div>
            <AddButton/>
        </div>
    )
}

export default NotesListPage
