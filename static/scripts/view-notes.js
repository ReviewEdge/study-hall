(() => {
  let copyLinkP
  let deleteBtn

  window.addEventListener("DOMContentLoaded", async () => {
    // delete note
    deleteBtn = document.getElementById("delete-note")
    if (deleteBtn) {
      deleteBtn.addEventListener("click", deleteNote)
    }

    // bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    })
    
    copyLinkP = document.getElementById('copy-link')
    if (copyLinkP) {
      copyLinkP.addEventListener('click', copyLink)
    }
  })

  const copyLink = () => {
    if (navigator.clipboard) {
      const text = copyLinkP.innerText
      navigator.clipboard.writeText(text);
      copyLinkP.innerHTML = "<i class='fa-solid fa-check'></i> Copied!"
      copyLinkP.classList.add("text-success")
      setTimeout(() => {
        copyLinkP.innerText = text
        copyLinkP.classList.remove("text-success")
      }, 2000)
    }
  }

  const deleteNote = () => {
    if (confirm("Are you sure? This action cannot be undone.")) {
      fetch(`/api/notes/${deleteBtn.dataset.noteId}`, {method: 'DELETE'})
        .then(() => {
          // redirect to the notes page
          window.location.href = '/notes'
        })
        .catch(error => console.log(error))
    }
  }
})()
