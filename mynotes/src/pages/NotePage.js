import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ReactComponent as ArrowLeft } from '../assets/arrow-left.svg'

const NotePage = () => {
  let { id }  = useParams();
  let navigate = useNavigate()
  let [note, setNote] = useState({})
  useEffect(() => {
    let getNote = async () => {
      if (id === 'new') return
      let response = await fetch(`/api/notes/${id}`)
      let data = await response.json()
      setNote(data)
    }
    getNote()
  }, [id])

  let createNote = async () => {
    await fetch(`/api/notes/create/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({body: note.body || ""})
    })
  }

  let updateNote = async () => {
    await fetch(`/api/notes/${id}/update/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({body: note.body || ""})
    })
  }

  let deleteNote = async () => {
    await fetch(`/api/notes/${id}/delete/`, {
      method: 'DELETE'
    })
    navigate('/')
  }

  let handleSubmit = async () => {
    if (id !== 'new' && !note.body?.trim()) {
      await deleteNote()
    } else if (id !== 'new') {
      await updateNote()
    } else if (id === 'new' && note.body?.trim()) {
      await createNote()
    }
    navigate('/')
  }

  return (
    <div className='note'>
      <div className="note-header">
        <h3>
          <button type="button" onClick={handleSubmit} aria-label="Go back">
            <ArrowLeft />
          </button>
        </h3>
        {id !== 'new' ? (
          <button type="button" onClick={deleteNote}>Delete</button>
        ):(
          <button type="button" onClick={handleSubmit}>Save</button>
        )}
      </div>
      <div className="note-body">
        <textarea
          onChange={(e) => {setNote({...note, 'body':e.target.value})}}
          value={note.body || ""}
          placeholder="Write a note..."
        />
      </div>
    </div>
  )
}

export default NotePage
