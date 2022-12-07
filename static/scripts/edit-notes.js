(() => {
  const noteID = window.location.pathname.split('/').length > 1 ? window.location.pathname.split('/')[2] : null
  let noteTitle
  let saveStatus

  window.addEventListener("DOMContentLoaded", async () => {
    tinymce.init({
      selector: 'textarea#note-content',
      plugins: 'autoresize image link searchreplace table emoticons wordcount',
      autoresize_bottom_margin: 50,
      autoresize_overflow_padding: 50,
      content_css: 'default,/static/styles/notes.css',
      setup: function(editor) {
        editor.on('Paste Change input Undo Redo', function(e) {
          saveNote()
        })
      }
    })

    noteTitle = document.getElementById("note-title")
    noteTitle.addEventListener("input", saveNote)

    saveStatus = document.getElementById("save-status")
  })

  let timeoutID
  const saveNote = () => {
    clearTimeout(timeoutID)
    timeoutID = setTimeout(function() {
      saveStatus.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Saving...'
      saveStatus.classList.remove("text-success")

      fetch(`/api/notes/${noteID}`, {
        method: 'PATCH',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({id: noteID, title: noteTitle.value, content: tinymce.activeEditor.getContent()}),
      }).then(() => {
          saveStatus.innerHTML = '<i class="fa-solid fa-check"></i> Saved'
          saveStatus.classList.add("text-success")
        })
        .catch(error => console.log(error))

    }, 1000)
  }
})()
